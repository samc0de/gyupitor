import os
import io
import csv
import json
import hashlib
from datetime import datetime
from crewai.tools import BaseTool
from google.cloud import bigquery


def timeline_to_csv(timeline: list[dict], top_n: int = 3) -> str:
    """Convert BigQuery job timeline JSON to a compact CSV for cost optimization."""

    # Pick only cost-impacting fields
    simplified = [
        {
            "id": stage.get("id"),
            "name": stage.get("name"),
            "slotMs": stage.get("slotMs", 0),
            "computeMs": stage.get("computeMs", 0),
            "readMb": stage.get("readMb", 0),
            "writeMb": stage.get("writeMb", 0),
        }
        for stage in timeline
    ]

    # Sort by slotMs descending
    simplified.sort(key=lambda s: s.get("slotMs", 0), reverse=True)

    # Either top_n or stages above cutoff (e.g., 10%)
    total_slots = sum(s["slotMs"] for s in simplified)
    cutoff = 0.1 * total_slots if total_slots else 0
    filtered = [s for s in simplified if s["slotMs"] >= cutoff][:top_n]

    # Convert to CSV string
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["id", "name", "slotMs", "computeMs", "readMb", "writeMb"])
    writer.writeheader()
    writer.writerows(filtered)

    return output.getvalue()

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
            if 'query_text' in processed_row and processed_row['query_text']:
                query_text = processed_row['query_text']
                query_hash = hashlib.sha256(query_text.encode()).hexdigest()
                processed_row['query_hash'] = query_hash
                
                if query_hash not in seen_queries:
                    query_filename = os.path.join(self.raw_queries_dir, f"{query_hash}.sql")
                    with open(query_filename, 'w') as f:
                        f.write(query_text)
                    seen_queries.add(query_hash)
                
                del processed_row['query_text']

            # --- Create meaningul, stagewise summary for 'timeline' ---
            if 'timeline' in processed_row and processed_row['timeline']:
                try:
                    # The BQ client library might auto-parse the JSON, so handle both string and list cases
                    timeline_data = processed_row['timeline'] if isinstance(processed_row['timeline'], list) else json.loads(processed_row['timeline'])
                    processed_row['timeline_metrics'] = timeline_to_csv(timeline_data)
                    
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
        with open("bq_queries.log", "a") as f:
            f.write(f"[{datetime.now()}] QUERY:\n{query}\n\n")
        cache_file = self._get_cache_filename(query)

        if os.path.exists(cache_file):
            print(f"INFO: Returning cached BQ results from {cache_file}.")
            return f"Successfully retrieved cached results. The data is at {cache_file}. Use the PromptDataBatcherTool to split it into batches."

        try:
            print("INFO: Executing new BigQuery query...")
            client = bigquery.Client()
            query_job = client.query(query)
            results = query_job.result()
            rows = [dict(row) for row in results]
            
            print(f"INFO: Pre-processing {len(rows)} rows.")
            processed_rows = self._preprocess_results(rows)
            
            final_output = json.dumps(processed_rows, indent=4, default=str)

            print(f"INFO: Caching {len(rows)} processed rows to {cache_file}.")
            with open(cache_file, 'w') as f:
                f.write(final_output)
            
            return f"Successfully executed query and cached {len(rows)} results to {cache_file}. Use the PromptDataBatcherTool to split it into batches."
        except Exception as e:
            print(f"FATAL: Error executing BigQuery query: {e}")
            raise
