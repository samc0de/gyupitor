import os
import json
from crewai.tools import BaseTool

from pydantic import BaseModel, Field, model_validator

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
        """
        job_run_dir: str = os.getenv('JOB_RUN_DIR', '')
        full_path = os.path.join(job_run_dir, file_path)
        
        if mode not in ['w', 'a']:
            return "Error: Invalid mode. Use 'w' for write or 'a' for append."
            
        try:
            directory = os.path.dirname(full_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            # --- Modification for Appending JSON Lists ---
            if mode == 'a' and os.path.exists(full_path) and os.path.getsize(full_path) > 0:
                with open(full_path, 'r+') as f:
                    f.seek(0, os.SEEK_END)
                    pos = f.tell()
                    if pos > 0:
                        f.seek(pos - 1)
                        if f.read(1) == ']':
                            f.seek(pos - 1)
                            f.write(',')
                            if content.startswith('['):
                                content = content[1:]
                            f.write(content)
                        else:
                            f.write(content)
                    else:
                        f.write(content)
            else:
                with open(full_path, 'w') as f:
                    f.write(content)
            
            return f"File '{file_path}' has been updated successfully (mode: {mode})."
        except Exception as e:
            return f"Error updating file: {e}"
