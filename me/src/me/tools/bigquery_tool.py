import os
import io
import csv
import json
import hashlib
from datetime import datetime
from crewai.tools import BaseTool
from google.cloud import bigquery


def aggregate_timeline_metrics(timeline: list[dict]) -> dict:
    """
    Aggregates the timeline snapshots of a BigQuery job into a single summary
    of key performance and cost indicators.
    """
    if not timeline:
        return {}

    # --- Key Metrics Calculation ---
    last_entry = timeline[-1]
    total_runtime_ms = last_entry.get("elapsed_ms", 0)
    slot_ms_consumed = last_entry.get("total_slot_ms", 0)
    final_completed_units = last_entry.get("completed_units", 0)
    
    peak_slots = max(t.get("active_units", 0) or 0 for t in timeline)
    queue_pressure = max(t.get("pending_units", 0) or 0 for t in timeline)
    
    # --- Throughput Calculation (units per second) ---
    throughput = (final_completed_units / (total_runtime_ms / 1000)) if total_runtime_ms > 0 else 0

    # --- Concurrency Trend (Slope of active_units vs. time) ---
    # Using a simple linear regression calculation
    n = len(timeline)
    if n > 1:
        x = [t.get("elapsed_ms", 0) or 0 for t in timeline]
        y = [t.get("active_units", 0) or 0 for t in timeline]
        sum_x = sum(x)
        sum_y = sum(y)
        sum_xy = sum(xi * yi for xi, yi in zip(x, y))
        sum_x2 = sum(xi**2 for xi in x)
        
        numerator = n * sum_xy - sum_x * sum_y
        denominator = n * sum_x2 - sum_x**2
        
        slope = numerator / denominator if denominator != 0 else 0
    else:
        slope = 0  # Cannot determine a trend from a single point

    return {
        "total_runtime_ms": total_runtime_ms,
        "peak_slots_used": peak_slots,
        "slot_ms_consumed": slot_ms_consumed,
        "concurrency_trend_slope": round(slope, 4),
        "max_queue_pressure": queue_pressure,
        "throughput_units_per_sec": round(throughput, 2)
    }


def job_details_to_summary(details: dict) -> dict:
    """Extract key cost and performance indicators from the verbose job details."""
    if not details:
        return {}
    
    # Extract cache hit status
    cache_hit = details.get("jobStatistics", {}).get("query", {}).get("cacheHit", "unknown")

    # Extract billing tier and estimated bytes processed
    billing_tier = details.get("jobStatistics", {}).get("query", {}).get("billingTier", "unknown")
    estimated_bytes = details.get("jobStatistics", {}).get("query", {}).get("estimatedBytesProcessed", 0)

    # Simplified statement type
    statement_type = details.get("jobStatistics", {}).get("query", {}).get("statementType", "unknown")

    return {
        "cacheHit": cache_hit,
        "billingTier": billing_tier,
        "estimatedBytesProcessed": estimated_bytes,
        "statementType": statement_type
    }



class BigQueryTool(BaseTool):
    name: str = "BigQuery Tool"
    description: str = "Executes a BigQuery SQL query. Pre-processes results to handle large and repeated fields by deduplicating them and saving the raw data to separate, cross-referenced files."
    
    # --- New, more organized directory structure ---
    base_cache_dir: str = ".bq_cache"
    results_dir: str = os.path.join(base_cache_dir, "query_results")
    raw_queries_dir: str = os.path.join(base_cache_dir, "raw_queries")
    raw_timelines_dir: str = os.path.join(base_cache_dir, "raw_timelines")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.raw_queries_dir, exist_ok=True)
        os.makedirs(self.raw_timelines_dir, exist_ok=True)

    def _get_cache_filename(self, query: str) -> str:
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        return os.path.join(self.results_dir, f"{query_hash}.json")

    def _preprocess_results(self, rows: list) -> list:
        processed_rows = []
        seen_queries = set()

        for row in rows:
            processed_row = dict(row)
            job_id = processed_row.get('job_id', f"unknown_job_{hashlib.sha256(json.dumps(processed_row, default=str).encode()).hexdigest()}")

            # --- Deduplicate 'query_text' field ---
            # TODO: Implement a future "Synthesis Agent" that correlates the job performance
            # analysis with the SQL query structure analysis. This agent will take the outputs
            # from the job analysis (keyed by q_hash) and the SQL analysis (also keyed by
            # q_hash) to provide a root cause analysis and a specific, actionable recommendation.
            # This will allow the LLM to connect performance bottlenecks (e.g., high pending_units)
            # with SQL anti-patterns (e.g., JOIN on a string column).

            if 'query_text' in processed_row and processed_row['query_text']:
                # Normalize the query by lowercasing and removing all whitespace for a true, semantic hash
                query_text = processed_row['query_text']
                normalized_query = "".join(query_text.lower().split())
                query_hash = hashlib.sha256(normalized_query.encode()).hexdigest()
                processed_row['query_hash'] = query_hash
                
                if query_hash not in seen_queries:
                    query_filename = os.path.join(self.raw_queries_dir, f"{query_hash}.sql")
                    with open(query_filename, 'w') as f:
                        f.write(query_text) # Save the original query text for readability
                    seen_queries.add(query_hash)
                
                del processed_row['query_text']

            # --- Create a single, aggregated summary from the 'timeline' data ---
            if 'timeline' in processed_row and processed_row['timeline']:
                try:
                    # The BQ client library might auto-parse the JSON, so handle both string and list cases
                    timeline_data = processed_row['timeline'] if isinstance(processed_row['timeline'], list) else json.loads(processed_row['timeline'])
                    processed_row['timeline_summary'] = aggregate_timeline_metrics(timeline_data)
                    
                except (json.JSONDecodeError, IndexError, KeyError, TypeError) as e:
                    print(f"WARNING: Could not process timeline for job {job_id}. Error: {e}")
                    processed_row['timeline_summary'] = {"error": "Could not process timeline data."}

                if 'timeline' in processed_row:
                    del processed_row['timeline']

            # --- Summarize the 'job_details' field ---
            if 'job_details' in processed_row and processed_row['job_details']:
                try:
                    details_data = processed_row['job_details'] if isinstance(processed_row['job_details'], dict) else json.loads(processed_row['job_details'])
                    processed_row['job_details_summary'] = job_details_to_summary(details_data)
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"WARNING: Could not process job_details for job {job_id}. Error: {e}")
                    processed_row['job_details_summary'] = {"error": "Could not process job_details data."}

                if 'job_details' in processed_row:
                    del processed_row['job_details']
            
            processed_rows.append(processed_row)
        return processed_rows

    def _run(self, query: str) -> str:
        cache_file = self._get_cache_filename(query)

        # if os.path.exists(cache_file):
        #     print(f"INFO: Returning cached BQ results from {cache_file}.")
        #     with open(cache_file, 'r') as f:
        #         processed_rows = json.load(f)
        #     print(f"INFO: Pre-processing {len(processed_rows)} rows from cache.")
        #     return f"Successfully retrieved cached results. The data is at {cache_file}. Use the PromptDataBatcherTool to split it into batches."

        try:
            print("INFO: Executing new BigQuery query...")
            with open("bq_queries.log", "a") as f:
                f.write(f"[{datetime.now()}] QUERY:\n{query}\n\n")
            client = bigquery.Client()
            query_job = client.query(query)
            results = query_job.result()
            
            # --- Robust Data Handling: Write to file, then read back ---
            raw_results_file = os.path.join(self.results_dir, "raw_q_result.json")
            rows_to_write = [dict(row) for row in results]

            with open(raw_results_file, 'w') as f:
                json.dump(rows_to_write, f, default=str)
            print(f"INFO: Wrote {len(rows_to_write)} raw results to {raw_results_file}.")

            # Now, read the data back from the file to ensure consistency
            with open(raw_results_file, 'r') as f:
                rows_to_process = json.load(f)

            print(f"INFO: Pre-processing {len(rows_to_process)} rows.")
            processed_rows = self._preprocess_results(rows_to_process)
            
            final_output = json.dumps(processed_rows, indent=4, default=str)

            print(f"INFO: Caching {len(processed_rows)} processed rows to {cache_file}.")
            with open(cache_file, 'w') as f:
                f.write(final_output)
            
            return f"Successfully executed query and cached {len(processed_rows)} results to {cache_file}. Use the PromptDataBatcherTool to split it into batches."
        except Exception as e:
            print(f"FATAL: Error executing BigQuery query: {e}")
            raise
