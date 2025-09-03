from crewai.tools import BaseTool
import os

class FileWriterTool(BaseTool):
    name: str = "FileWriterTool"
    description: str = "A tool that can write content to a file. Use it when you need to save results, logs, or other text."

    def _run(self, file_path: str, content: str) -> str:
        """Use this tool to write content to a file."""
        try:
            directory = os.path.dirname(file_path)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            with open(file_path, 'w') as f:
                f.write(content)
            
            return f"File '{file_path}' has been written successfully."
        except Exception as e:
            return f"Error writing file: {e}"
