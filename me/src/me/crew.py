from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from langchain_google_vertexai import VertexAI

# Import Tool Classes directly
from me.tools.bigquery_tool import BigQueryTool
from me.tools.file_reader_tool import FileReaderTool
from me.tools.file_writer_tool import FileWriterTool
from me.tools.shell_tool import ShellTool

@CrewBase
class Me():
    """Me crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self) -> None:
        # Define LLMs
        self.pro_llm = VertexAI(model_name="gemini-2.5-pro")
        self.strict_llm = VertexAI(model_name="gemini-2.5-pro", temperature=0.0)
        self.flash_llm = VertexAI(model_name="gemini-2.5-flash")
        # self.agents_config = load_yaml("config/agents.yaml")
        
        # # Expose the software_architect agent for interactive mode
        # self.software_architect_agent = self.software_architect()

    @agent
    def bq_expert(self) -> Agent:
        return Agent(
            config=self.agents_config['bq_expert'],
            tools=[BigQueryTool(), FileReaderTool(), ShellTool(), FileWriterTool()],
            llm=self.strict_llm,
            verbose=True
        )

    @agent
    def software_architect(self) -> Agent:
        self.software_architect_agent = Agent(
            config=self.agents_config['software_architect'],
            tools=[FileWriterTool(), ShellTool(), FileReaderTool()],
            llm=self.pro_llm,
            verbose=True
        )
        return self.software_architect_agent

    @agent
    def ui_ux_designer(self) -> Agent:
        return Agent(
            config=self.agents_config['ui_ux_designer'],
            tools=[FileWriterTool(), FileReaderTool(), ShellTool()],
            llm=self.pro_llm,
            verbose=True
        )

    @agent
    def polyglot_developer(self) -> Agent:
        return Agent(
            config=self.agents_config['polyglot_developer'],
            tools=[FileWriterTool(), ShellTool()],
            llm=self.flash_llm,
            verbose=True
        )

    @agent
    def system_ai_monitor(self) -> Agent:
        return Agent(
            config=self.agents_config['system_ai_monitor'],
            tools=[FileWriterTool()],
            llm=self.flash_llm,
            verbose=True
        )

    @agent
    def customer_chatbot(self) -> Agent:
        return Agent(
            config=self.agents_config['customer_chatbot'],
            tools=[FileWriterTool()],
            llm=self.flash_llm,
            verbose=True
        )

    @task
    def provide_instructions_task(self) -> Task:
        return Task(
            config=self.tasks_config['provide_instructions_task'],
            agent=self.customer_chatbot()
        )

    @task
    def analyze_and_recommend_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_and_recommend_task'],
            agent=self.bq_expert(),
            context=[self.provide_instructions_task()]
        )

    @task
    def design_full_stack_application_task(self) -> Task:
        return Task(
            config=self.tasks_config['design_full_stack_application_task'],
            agent=self.software_architect(),
            context=[self.analyze_and_recommend_task()]
        )

    @task
    def implement_backend_task(self) -> Task:
        return Task(
            config=self.tasks_config['implement_backend_task'],
            agent=self.polyglot_developer(),
            context=[self.design_full_stack_application_task()]
        )

    @task
    def implement_frontend_task(self) -> Task:
        return Task(
            config=self.tasks_config['implement_frontend_task'],
            agent=self.ui_ux_designer(),
            context=[self.design_full_stack_application_task()]
        )

    @task
    def containerize_and_run_task(self) -> Task:
        return Task(
            config=self.tasks_config['containerize_and_run_task'],
            agent=self.software_architect(),
            context=[self.implement_backend_task(), self.implement_frontend_task()]
        )

    # @task
    # def feedback_and_review_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['feedback_and_review_task'],
    #         agent=self.customer_chatbot(),
    #         context=[self.containerize_and_run_task()]
    #     )

    @crew
    def crew(self) -> Crew:
        """Creates the Me crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

if __name__ == "__main__":
    import sys
    print("Crew script started...")
    try:
        me_crew = Me()
        result = me_crew.crew().kickoff()
        print("Crew kickoff result:")
        print(result)
    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        # Also print traceback for more details
        import traceback
        traceback.print_exc()

