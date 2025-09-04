import json
from crewai.tools import BaseTool

class JsonBatchReaderTool(BaseTool):
    name: str = "JSON Batch Reader Tool"
    description: str = "Reads a large JSON file containing a list of items and returns a specific batch of those items."
    batch_size: int = 50  # Number of jobs per batch

    def _run(self, file_path: str, batch_number: int = 1) -> str:
        """
        Reads a JSON file and returns a specific batch of items from the list.

        Args:
            file_path: The path to the input JSON file.
            batch_number: The batch number to retrieve (1-indexed).
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                return json.dumps({"error": "Input JSON is not a list."})

            total_items = len(data)
            total_batches = (total_items + self.batch_size - 1) // self.batch_size

            if batch_number < 1 or batch_number > total_batches:
                return json.dumps({
                    "error": f"Invalid batch number. Please provide a number between 1 and {total_batches}.",
                    "total_batches": total_batches
                })

            start_index = (batch_number - 1) * self.batch_size
            end_index = start_index + self.batch_size
            batch_data = data[start_index:end_index]

            return json.dumps({
                "batch_number": batch_number,
                "total_batches": total_batches,
                "jobs_in_batch": len(batch_data),
                "batch_data": batch_data
            }, default=str)

        except FileNotFoundError:
            return json.dumps({"error": f"File not found: {file_path}"})
        except json.JSONDecodeError:
            return json.dumps({"error": f"Could not decode JSON from file: {file_path}"})
        except Exception as e:
            return json.dumps({"error": f"An unexpected error occurred: {str(e)}"})
