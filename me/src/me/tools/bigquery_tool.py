import os
import json
import hashlib
from crewai.tools import BaseTool
from google.cloud import bigquery

class BigQueryTool(BaseTool):
    name: str = "BigQuery Tool"
    description: str = "Executes a BigQuery SQL query and returns the results as a string. Results are cached in a local file."
    cache_dir: str = ".bq_cache"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        os.makedirs(self.cache_dir, exist_ok=True)

    def _get_cache_filename(self, query: str) -> str:
        """Creates a unique filename from a hash of the query."""
        query_hash = hashlib.sha256(query.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{query_hash}.json")

    def _run(self, query: str) -> str:
        cache_file = self._get_cache_filename(query)

        if os.path.exists(cache_file):
            print("INFO: Returning file-cached BigQuery results.")
            with open(cache_file, 'r') as f:
                return json.load(f)

        try:
            print("INFO: Executing new BigQuery query.")
            client = bigquery.Client()
            query_job = client.query(query)
            results = query_job.result()  # Waits for the job to complete.

            rows = [dict(row) for row in results]
            result_str = str(rows) # Keep the output as string as expected by agents

            with open(cache_file, 'w') as f:
                json.dump(result_str, f)
            
            return result_str
        except Exception as e:
            return f"Error executing BigQuery query: {e}"
