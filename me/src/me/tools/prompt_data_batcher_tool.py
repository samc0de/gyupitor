import json
import os
from crewai.tools import BaseTool

class PromptDataBatcherTool(BaseTool):
    name: str = "Prompt Data Batcher Tool"
    description: str = "Reads a large JSON file and splits it into multiple, smaller batch files based on a token limit."
    
    TOKEN_LIMIT = 800000  # Set a safe token limit for each batch

    def _estimate_tokens(self, data: dict) -> int:
        """A simple heuristic to estimate token count."""
        return len(json.dumps(data, default=str)) / 4

    def _run(self, input_file_path: str) -> str:
        """
        Reads a large JSON file and splits it into smaller batch files.

        Args:
            input_file_path: The path to the large JSON file to be processed.
        """
        try:
            with open(input_file_path, 'r') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                return json.dumps({"error": "Input JSON is not a list of objects."})

            basename, _ = os.path.splitext(input_file_path)
            
            batches = []
            current_batch = []
            current_tokens = 0

            for row in data:
                row_tokens = self._estimate_tokens(row)

                if current_tokens + row_tokens > self.TOKEN_LIMIT and current_batch:
                    batches.append(current_batch)
                    current_batch = []
                    current_tokens = 0
                
                current_batch.append(row)
                current_tokens += row_tokens
            
            if current_batch:
                batches.append(current_batch)

            if not batches:
                return "No data to process."

            print(f"INFO: Splitting {len(data)} rows from {input_file_path} into {len(batches)} batches.")
            for i, batch in enumerate(batches, 1):
                batch_file = f"{basename}-batch-{i}.json"
                with open(batch_file, 'w') as f:
                    json.dump(batch, f, indent=4, default=str)
            
            return f"Successfully split the data into {len(batches)} batches with the basename '{basename}'. Instruct the analysis agent to loop from 1 to {len(batches)} and read the files named '{basename}-batch-N.json'."

        except FileNotFoundError:
            return json.dumps({"error": f"File not found: {input_file_path}"})
        except json.JSONDecodeError:
            return json.dumps({"error": f"Could not decode JSON from file: {input_file_path}"})
        except Exception as e:
            return json.dumps({"error": f"An unexpected error occurred: {str(e)}"})
