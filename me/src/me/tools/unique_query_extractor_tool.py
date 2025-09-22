import json
import os
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class UniqueQueryExtractorToolSchema(BaseModel):
    file_path: str = Field(..., description="The path to the input JSON file from the BigQueryTool.")

class UniqueQueryExtractorTool(BaseTool):
    name: str = "Unique Query Extractor Tool"
    description: str = "Reads a JSON file of BigQuery job results and extracts a list of unique query hashes."
    args_schema: type[BaseModel] = UniqueQueryExtractorToolSchema

    def _run(self, file_path: str) -> str:
        """
        Extracts unique query hashes from a JSON file.
        """
        job_run_dir: str = os.getenv('JOB_RUN_DIR', '')
        full_path = os.path.join(job_run_dir, file_path)
        
        try:
            with open(full_path, 'r') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                return json.dumps({"error": "Input JSON is not a list of objects."})

            query_hashes = {item.get('query_hash') for item in data if item.get('query_hash')}
            
            return json.dumps({"unique_query_hashes": list(query_hashes)}, indent=4)

        except FileNotFoundError:
            return json.dumps({"error": f"File not found: {full_path}"})
        except json.JSONDecodeError:
            return json.dumps({"error": f"Could not decode JSON from file: {full_path}"})
        except Exception as e:
            return json.dumps({"error": f"An unexpected error occurred: {str(e)}"})
