import os
import json
from crewai.tools import BaseTool

from pydantic import BaseModel, Field

class FileWriterToolSchema(BaseModel):
    """Input schema for the File Writer Tool."""
    file_path: str = Field(..., description="The path to the file.")
    content: str = Field(..., description="The content to write or append.")
    mode: str = Field(default='w', description="'w' for write (overwrite), 'a' for append. Defaults to 'w'.")

class FileWriterTool(BaseTool):
    name: str = "FileWriterTool"
    description: str = "A tool that can write or append content to a file. Use it to save results, logs, or other text."
    args_schema: type[BaseModel] = FileWriterToolSchema

    def _run(self, file_path: str, content: str, mode: str = 'w') -> str:
        """
        Use this tool to write or append content to a file.

        Args:
            file_path: The path to the file.
            content: The content to write or append.
            mode: 'w' for write (overwrite), 'a' for append. Defaults to 'w'.
        """
        if mode not in ['w', 'a']:
            return "Error: Invalid mode. Use 'w' for write or 'a' for append."
            
        try:
            directory = os.path.dirname(file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            # --- Modification for Appending JSON Lists ---
            # If appending, we need to handle JSON list formatting correctly.
            if mode == 'a' and os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                # 1. Read the existing content
                with open(file_path, 'r+') as f:
                    f.seek(0, os.SEEK_END)
                    pos = f.tell()
                    # Check if the file ends with ']'
                    if pos > 0:
                        f.seek(pos - 1)
                        if f.read(1) == ']':
                            # Overwrite ']' with a comma
                            f.seek(pos - 1)
                            f.write(',')
                            # The new content should not start with '['
                            if content.startswith('['):
                                content = content[1:]
                            f.write(content)
                        else:
                            # If it's not a valid list, just append
                            f.write(content)
                    else:
                        f.write(content)
            else:
                # Default behavior for writing a new file or overwriting
                with open(file_path, 'w') as f:
                    f.write(content)
            
            return f"File '{file_path}' has been updated successfully (mode: {mode})."
        except Exception as e:
            return f"Error updating file: {e}"
