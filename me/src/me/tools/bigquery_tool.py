from crewai.tools import BaseTool
from google.cloud import bigquery

class BigQueryTool(BaseTool):
    name: str = "BigQuery Tool"
    description: str = "Executes a BigQuery SQL query and returns the results."

    def _run(self, query: str) -> str:
        try:
            client = bigquery.Client()
            query_job = client.query(query)
            results = query_job.result()  # Waits for the job to complete.

            rows = [dict(row) for row in results]
            return str(rows)
        except Exception as e:
            return f"Error executing BigQuery query: {e}"
