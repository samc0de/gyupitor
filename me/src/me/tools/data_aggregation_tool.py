import json
from crewai.tools import BaseTool

class DataAggregationTool(BaseTool):
    name: str = "Data Aggregation and Summarization Tool"
    description: str = "Reads a large BQ results JSON file, calculates key statistics, and returns a compact, actionable summary."

    def _run(self, file_path: str) -> str:
        """
        Processes a raw BQ results file to create a summary that is safe to pass to an LLM.

        Args:
            file_path: The path to the input JSON file from the BigQueryTool.
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                return json.dumps({"error": "Input JSON is not a list of objects."})

            # --- Perform Aggregation ---
            num_jobs = len(data)
            cache_hits = sum(1 for row in data if row.get('job_details_summary', {}).get('cacheHit'))
            
            # --- Find Top 5 Most Expensive Jobs by total_slot_ms ---
            # It's possible total_slot_ms is not present, so default to 0
            sorted_jobs = sorted(
                [job for job in data if job.get('total_slot_ms')], 
                key=lambda x: x.get('total_slot_ms', 0), 
                reverse=True
            )
            top_5_jobs = [
                {
                    "job_id": job.get('job_id'),
                    "user_email": job.get('user_email'),
                    "total_slot_ms": job.get('total_slot_ms'),
                    "total_bytes_processed": job.get('total_bytes_processed'),
                    "query_hash": job.get('query_hash')
                }
                for job in sorted_jobs[:5]
            ]
            
            # --- Create a compact summary ---
            summary = {
                "total_jobs_analyzed": num_jobs,
                "jobs_with_cache_hit": cache_hits,
                "top_5_most_expensive_jobs": top_5_jobs
            }
            
            return json.dumps(summary, indent=4)

        except FileNotFoundError:
            return json.dumps({"error": f"File not found: {file_path}"})
        except json.JSONDecodeError:
            return json.dumps({"error": f"Could not decode JSON from file: {file_path}"})
        except Exception as e:
            return json.dumps({"error": f"An unexpected error occurred: {str(e)}"})
