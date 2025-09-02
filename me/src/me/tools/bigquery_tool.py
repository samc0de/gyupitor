import os
import io
import csv
import json
import hashlib
from datetime import datetime
from crewai.tools import BaseTool
from google.cloud import bigquery


def timeline_to_csv(timeline: list[dict], top_n: int = 5) -> str:
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
                    
                    timeline_filename = os.path.join(self.raw_timelines_dir, f"{job_id}_timeline.json")
                    # with open(timeline_filename, 'w') as f:
                    #     json.dump(timeline_data, f, indent=4)
                    # processed_row['timeline_details_file'] = timeline_filename

                except (json.JSONDecodeError, IndexError, KeyError, TypeError) as e:
                    print(f"WARNING: Could not process timeline for job {job_id}. Error: {e}")
                    processed_row['timeline_summary'] = {"error": "Could not process timeline data."}

                if 'timeline' in processed_row:
                    del processed_row['timeline']
            
            processed_rows.append(processed_row)
        return processed_rows

    def _run(self, query: str) -> str:
        cache_file = self._get_cache_filename(query)

        if os.path.exists(cache_file):
            print(f"INFO: Returning pre-processed, file-cached BQ results from {cache_file}.")
            with open(cache_file, 'r') as f:
                return f"Successfully retrieved cached results from {cache_file}. The BQ expert should now analyze this file. Other agents should wait for the BQ expert's analysis."

        try:
            print("INFO: Executing new BigQuery query...")
            client = bigquery.Client()
            query_job = client.query(query)
            results = query_job.result()
            rows = [dict(row) for row in results]
            
            print(f"INFO: Pre-processing {len(rows)} rows to handle large and repeated fields.")
            processed_rows = self._preprocess_results(rows)
            
            final_output = json.dumps(processed_rows, indent=4, default=str)

            print(f"INFO: Caching processed results to {cache_file}.")
            with open(cache_file, 'w') as f:
                f.write(final_output)
            
            return f"Successfully executed query and cached processed results to {cache_file}. The BQ expert should now analyze this file. Other agents should wait for the BQ expert's analysis."
        except Exception as e:
            print(f"FATAL: Error executing BigQuery query: {e}")
            raise
