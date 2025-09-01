#!/usr/bin/env python
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import warnings

from datetime import datetime

from me.crew import Me

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew's main tasks once, then enter an interactive mode for feedback.
    """
    me_crew = Me()
    crew = me_crew.crew()

    print("🚀 Kicking off the main crew to perform initial analysis and setup...")
    try:
        # Run the main sequence of tasks
        main_result = crew.kickoff()
        print("\n✅ Main crew execution finished.")
        print("---------------------------------")
        print("Main execution result:", main_result)
        print("---------------------------------")

    except Exception as e:
        print(f"An error occurred during the main run: {e}")
        return  # Exit if the main run fails

    print("\nEntering interactive mode. You can now provide feedback or ask questions.")
    
    # Identify the customer_chatbot agent for the interactive loop
    customer_chatbot = next((agent for agent in crew.agents if agent.role == 'Customer Chatbot'), None)
    
    if not customer_chatbot:
        print("Error: Could not find the Customer Chatbot agent.")
        return

    while True:
        try:
            user_input = input("You: ")
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting the interactive session.")
                break

            # Create a new, specific task for the chatbot for each interaction
            interactive_task = Task(
                description=f"Address the user's latest message: '{user_input}'. Use your memory of the project to provide a relevant response. Do not re-run the entire project.",
                agent=customer_chatbot,
                expected_output="A helpful and context-aware response to the user's message."
            )
            
            # Execute only this single task using a temporary crew
            chat_crew = Crew(
                agents=[customer_chatbot],
                tasks=[interactive_task],
                verbose=False,
                memory=True
            )
            result = chat_crew.kickoff()
            
            print("\nChatbot:")
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
