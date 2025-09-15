import json
import os
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class UniqueValueExtractorToolSchema(BaseModel):
    file_path: str = Field(..., description="The path to the input JSON file.")
    data_key: str = Field(..., description="The key to extract unique values from.")

class UniqueValueExtractorTool(BaseTool):
    name: str = "Unique Value Extractor Tool"
    description: str = "Reads a JSON file and extracts a list of unique values for a specified key."
    args_schema: type[BaseModel] = UniqueValueExtractorToolSchema

from functools import reduce
import operator

def get_from_dict(data_dict, map_list):
    """Iteratively access nested dictionary keys."""
    return reduce(operator.getitem, map_list, data_dict)

class UniqueValueExtractorTool(BaseTool):
    name: str = "UniqueValueExtractorTool"
    description: str = "Reads a JSON file and extracts a list of unique values for a specified key, including nested keys (e.g., 'a.b.c')."
    args_schema: type[BaseModel] = UniqueValueExtractorToolSchema

    def _run(self, file_path: str, data_key: str) -> str:
        """
        Extracts unique values from a JSON file for a given key, supporting nested keys.
        """
        full_path = file_path
        keys = data_key.split('.')
        
        try:
            with open(full_path, 'r') as f:
                data = json.load(f)
            
            if not isinstance(data, list):
                return json.dumps({"error": "Input JSON is not a list of objects."})

            unique_values = set()
            for item in data:
                try:
                    value = get_from_dict(item, keys)
                    if value:  # Ensure value is not null or empty
                        unique_values.add(value)
                except (KeyError, TypeError):
                    # This happens if a key in the path doesn't exist or data isn't a dict
                    continue
            
            if not unique_values:
                 return json.dumps({
                    "error": f"The nested data_key '{data_key}' was not found in any of the {len(data)} records, or the values were all null/empty.",
                }, indent=4)

            return json.dumps({"unique_values": sorted(list(unique_values))}, indent=4)

        except FileNotFoundError:
            return json.dumps({"error": f"File not found: {full_path}"})
        except json.JSONDecodeError:
            return json.dumps({"error": f"Could not decode JSON from file: {full_path}"})
        except Exception as e:
            return json.dumps({"error": f"An unexpected error occurred: {str(e)}"})
