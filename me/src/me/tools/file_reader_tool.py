import os
import json
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import io
import csv

def json_to_csv(batch: list[dict]) -> str:
    """Converts a list of JSON objects (dicts) to a CSV string."""
    if not batch:
        return ""
    
    headers = batch[0].keys()
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    
    writer.writeheader()
    writer.writerows(batch)
    
    return output.getvalue()

class FileReaderToolSchema(BaseModel):
    """Input schema for the File Reader Tool."""
    file_path: str = Field(..., description="The path to the JSON file to be read.")
    batch_number: int = Field(default=1, description="The batch number to retrieve. Defaults to 1.")

class FileReaderTool(BaseTool):
    name: str = "FileReaderTool"
    description: str = "Reads a large JSON file in structured batches, respecting object boundaries, and returns the data in CSV format."
    args_schema: type[BaseModel] = FileReaderToolSchema

    _file_cache: dict = {}
    batch_size_chars: int = 50000

    def _create_batches(self, file_path: str):
        """Reads a JSON file and splits it into batches of CSV data based on character count."""
        if file_path in self._file_cache:
            return

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            if not isinstance(data, list):
                self._file_cache[file_path] = [json_to_csv([data])]
                return

            batches = []
            current_batch = []

            for record in data:
                potential_batch = current_batch + [record]
                potential_csv_str = json_to_csv(potential_batch)

                if len(potential_csv_str) > self.batch_size_chars and current_batch:
                    final_csv_str = json_to_csv(current_batch)
                    batches.append(final_csv_str)
                    current_batch = [record]
                else:
                    current_batch.append(record)

            if current_batch:
                final_csv_str = json_to_csv(current_batch)
                batches.append(final_csv_str)

            self._file_cache[file_path] = batches
        except (json.JSONDecodeError, KeyError) as e:
            self._file_cache[file_path] = [f"Error: Invalid JSON or structure in file {file_path}: {e}"]
        except Exception as e:
            self._file_cache[file_path] = [f"Error reading or processing file {file_path}: {e}"]

    def _run(self, file_path: str, batch_number: int) -> str:
        """
        Reads a specific CSV batch from a file.
        """
        if file_path not in self._file_cache:
            self._create_batches(file_path)

        batches = self._file_cache.get(file_path, [])
        total_batches = len(batches)

        if not batches:
            return "Error: No data to process or an error occurred during file processing."
        
        if batch_number < 1 or batch_number > total_batches:
            return f"Error: Batch number {batch_number} is out of range. Total batches: {total_batches}."
        
        batch_content = batches[batch_number - 1]

        return f"--- CSV Batch {batch_number}/{total_batches} ---\n{batch_content}"
