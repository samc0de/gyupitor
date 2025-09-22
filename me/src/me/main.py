#!/usr/bin/env python
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import warnings
from crewai import Crew, Task

from datetime import datetime

from me.crew import Me

from me.utils.data_getter.stat_analysis import BQJobsDataGetter
from pathlib import Path
warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew's main tasks once, then enter an interactive mode for feedback.
    """
    # --- Create unique directory and inject into inputs ---
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    job_run_dir = f"job_runs/{timestamp}"
    os.makedirs(job_run_dir, exist_ok=True)
    inputs = {
        'job_run_dir': job_run_dir,
        'basename': os.path.basename(job_run_dir)
    }
    # ---

    # --- Run BQ Data Getter ---
    print("📊 Kicking off BQ Data Getter to fetch and process job data...")
    try:
        output_path = Path(job_run_dir) / 'bq_results'
        data_getter = BQJobsDataGetter(output_dir=str(output_path))
        data_getter.run()
        print("✅ BQ Data Getter finished successfully.")
    except Exception as e:
        print(f"\n❌ An error occurred during BQ data gathering: {e}")
        print("Exiting.")
        return
    # ---

    os.environ["JOB_RUN_DIR"] = job_run_dir
    me_crew = Me()
    crew = me_crew.crew()

    print("🚀 Kicking off the main crew to perform initial analysis and setup...")
    try:
        # Run the main sequence of tasks.
        # This is a long-running process. If it hangs, the script will not proceed.
        main_result = crew.kickoff(inputs=inputs)

        print("\n✅ Main crew execution finished successfully.")
        print("---------------------------------")
        print("Final Result:", main_result)
        print("---------------------------------")

    except Exception as e:
        print(f"\n❌ An error occurred during the main crew execution: {e}")
        print("Exiting.")
        return

    print("\n✅ Entering interactive mode. The crew has finished its main tasks.")
    print("You can now ask questions or provide feedback to the Software Architect.")
    
    # Find the Software Architect agent to interact with
    software_architect_agent = None
    for agent in crew.agents:
        if agent.role == 'Cloud Software and DevOps Architect':
            software_architect_agent = agent
            break
    
    if not software_architect_agent:
        print("Error: Could not find the Software Architect agent. Exiting.")
        return

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting the interactive session.")
                break

            # Create a new, single-agent crew for the chat interaction
            # The agent already has the LLM assigned, so we can access it directly.
            chat_crew = Crew(
                agents=[software_architect_agent],
                tasks=[
                    Task(
                        description=f"Address the user's question: '{user_input}'. Use your existing knowledge of the project.",
                        agent=software_architect_agent,
                        expected_output="A helpful, context-aware response."
                    )
                ],
                verbose=False,
                memory=True,
                llm=software_architect_agent.llm  # Access the LLM directly from the agent
            )
            
            result = chat_crew.kickoff()
            
            print("\nSoftware Architect:")
            print(result)
            print("\n-------------------\n")

        except Exception as e:
            print(f"An error occurred during the interactive session: {e}")
            break


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        Me().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Me().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }
    
    try:
        Me().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")
if __name__ == "__main__":
    run()
