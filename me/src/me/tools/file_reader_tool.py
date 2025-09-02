import os
import json
from crewai.tools import BaseTool

import io
import csv

def json_to_csv(batch: list[dict]) -> str:
    """Converts a list of JSON objects (dicts) to a CSV string."""
    if not batch:
        return ""
    
    # Use the keys from the first object as headers
    headers = batch[0].keys()
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    
    writer.writeheader()
    writer.writerows(batch)
    
    return output.getvalue()

class FileReaderTool(BaseTool):
    name: str = "File Reader Tool"
    description: str = "Reads a large JSON file in structured batches, respecting object boundaries."

    _file_cache: dict = {}  # Cache to hold batches for each file
    batch_size_chars: int = 50000  # Target size for each batch in characters

    def _create_batches(self, file_path: str):
        """Reads a JSON file and splits it into batches of CSV data based on character count."""
        if file_path in self._file_cache:
            return

        print(f"DEBUG: Starting CSV batch creation for {file_path} with batch size {self.batch_size_chars} chars.")
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            if not isinstance(data, list):
                print("DEBUG: Data is not a list, converting single object to CSV.")
                self._file_cache[file_path] = [json_to_csv([data])]
                return

            print(f"DEBUG: Loaded {len(data)} records from JSON.")
            batches = []
            current_batch = []

            for i, record in enumerate(data):
                potential_batch = current_batch + [record]
                potential_csv_str = json_to_csv(potential_batch)

                if len(potential_csv_str) > self.batch_size_chars and current_batch:
                    final_csv_str = json_to_csv(current_batch)
                    print(f"DEBUG: Batch full. Finalizing CSV batch {len(batches) + 1} with {len(current_batch)} records, final size: {len(final_csv_str)}")
                    batches.append(final_csv_str)
                    current_batch = [record]
                else:
                    current_batch.append(record)

            if current_batch:
                final_csv_str = json_to_csv(current_batch)
                print(f"DEBUG: Finalizing last CSV batch {len(batches) + 1} with {len(current_batch)} records, final size: {len(final_csv_str)}")
                batches.append(final_csv_str)

            self._file_cache[file_path] = batches
            print(f"INFO: Created {len(batches)} CSV batches for {file_path}.")

        except (json.JSONDecodeError, KeyError) as e:
            print(f"ERROR: Invalid JSON or structure in file {file_path}: {e}")
            self._file_cache[file_path] = [f"Error: Invalid JSON or structure in file {file_path}: {e}"]
        except Exception as e:
            print(f"ERROR: Error reading or processing file {file_path}: {e}")
            self._file_cache[file_path] = [f"Error reading or processing file {file_path}: {e}"]

    def _run(self, file_path: str, batch_number: int = 1) -> str:
        """
        Reads a specific CSV batch from a file.
        The file is read and batched on the first call, and subsequent calls retrieve from cache.
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
        print(f"DEBUG: Retrieving CSV batch {batch_number}/{total_batches}, size: {len(batch_content)} chars.")

        return f"--- CSV Batch {batch_number}/{total_batches} ---\n{batch_content}"
