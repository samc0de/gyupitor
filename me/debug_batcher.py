import os
import sys
import json

# Add the src directory to the Python path to import the tool
sys.path.insert(0, os.path.abspath('./src'))

from me.tools.prompt_data_batcher_tool import PromptDataBatcherTool

def debug_batching(input_file_path):
    """
    Runs the PromptDataBatcherTool with the given input file and prints the result.
    """
    if not os.path.exists(input_file_path):
        print(f"Error: The file '{input_file_path}' does not exist.")
        print("Please replace 'path/to/your/cached_bq_results.json' with the actual file path.")
        return

    # 1. Instantiate the tool
    batcher_tool = PromptDataBatcherTool()

    # 2. Run the tool with the input file
    print(f"Running the batcher tool on: {input_file_path}")
    result = batcher_tool._run(input_file_path=input_file_path)

    # 3. Print the result
    print("\n--- Batcher Tool Output ---")
    print(result)
    print("---------------------------\n")

    # 4. Verify the output
    try:
        # The tool's output message tells you the basename and number of batches
        # Example: "Successfully split the data into 5 batches with the basename '...'.
        # Instruct the analysis agent to loop from 1 to 5 and read the files named '...-batch-N.json'."
        
        # Parse the output to find the basename and number of batches
        parts = result.split("'")
        if "Successfully" in result and len(parts) > 1:
            basename = parts[1]
            num_batches = int(result.split(" ")[5])

            print("Verification:")
            for i in range(1, num_batches + 1):
                batch_file = f"{basename}-batch-{i}.json"
                if os.path.exists(batch_file):
                    print(f"  ✅ Found batch file: {batch_file}")
                else:
                    print(f"  ❌ Missing batch file: {batch_file}")
        else:
            print("Could not parse the output to verify batch files. The tool may have returned an error.")

    except (IndexError, ValueError) as e:
        print(f"Could not automatically verify the batch files due to an unexpected output format or error: {e}")


if __name__ == "__main__":
    # --- IMPORTANT ---
    # Replace this with the actual path to your cached BigQuery results file.
    # This file should be a JSON file containing a list of job objects.
    cached_bq_results_path = "path/to/your/cached_bq_results.json"
    
    debug_batching(cached_bq_results_path)
