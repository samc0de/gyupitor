import os
from datetime import datetime
from langchain.callbacks.base import BaseCallbackHandler
from typing import Any, Dict, List

class LLMLoggingCallback(BaseCallbackHandler):
    """Callback handler for logging LLM prompts."""

    def __init__(self, log_dir: str = "llm_prompts"):
        super().__init__()
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Called when an LLM call starts."""
        for i, prompt in enumerate(prompts):
            # Create a unique filename with a timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = os.path.join(self.log_dir, f"{timestamp}_prompt_{i+1}.txt")
            
            # Write the prompt to the file
            with open(filename, "w") as f:
                f.write(prompt)
