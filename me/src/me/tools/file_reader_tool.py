import os
from crewai.tools import BaseTool

class FileReaderTool(BaseTool):
    name: str = "File Reader Tool"
    description: str = "Reads the contents of a file and returns it as a string."

    def _run(self, file_path: str) -> str:
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {e}"
