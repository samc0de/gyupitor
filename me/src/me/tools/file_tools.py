import os
from crewai.tools import BaseTool

class WriteFileTool(BaseTool):
    name: str = "Write File Tool"
    description: str = "Writes text content to a specified file. Use this to save your work."

    def _run(self, file_path: str, content: str) -> str:
        try:
            # Ensure the directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing to file: {e}"
