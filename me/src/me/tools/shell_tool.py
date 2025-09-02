from crewai.tools import BaseTool
import os

class ShellTool(BaseTool):
    name: str = "ShellTool"
    description: str = "A tool that can be used to run shell commands."

    def _run(self, command: str) -> str:
        """Use this tool to run shell commands."""
        return os.popen(command).read()
