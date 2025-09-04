import os
from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from langchain_google_vertexai import VertexAI
from me.utils.llm_logging_callback import LLMLoggingCallback

# Import Tool Classes directly
from me.tools.bigquery_tool import BigQueryTool
from me.tools.file_reader_tool import FileReaderTool
from me.tools.file_writer_tool import FileWriterTool
from me.tools.shell_tool import ShellTool
from me.tools.data_aggregation_tool import DataAggregationTool

@CrewBase
class Me():
    """Me crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    def __init__(self) -> None:
        # Create a logger instance
        # Define the absolute path for the log directory
        log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'llm_prompts'))
        self.logger = LLMLoggingCallback(log_dir=log_dir)
        
        # Define LLMs with the logger callback
        self.pro_llm = VertexAI(model_name="gemini-2.5-pro", callbacks=[self.logger])
        self.strict_llm = VertexAI(model_name="gemini-2.5-pro", temperature=0.0, callbacks=[self.logger])
        self.flash_llm = VertexAI(model_name="gemini-2.5-flash", callbacks=[self.logger])
        # self.agents_config = load_yaml("config/agents.yaml")
        
        # # Expose the software_architect agent for interactive mode
        # self.software_architect_agent = self.software_architect()

    @agent
    def bq_expert(self) -> Agent:
        return Agent(
            config=self.agents_config['bq_expert'],
            tools=[BigQueryTool(), FileReaderTool(), ShellTool(), FileWriterTool(), DataAggregationTool()],
            llm=self.strict_llm,
            verbose=True
        )

    @agent
    def bq_expert_flash(self) -> Agent:
        return Agent(
            config=self.agents_config['bq_expert'],
            tools=[BigQueryTool(), FileReaderTool(), ShellTool(), FileWriterTool(), DataAggregationTool()],
            llm=self.flash_llm,
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
    def execute_bigquery_query_task(self) -> Task:
        return Task(
            config=self.tasks_config['execute_bigquery_query_task'],
            agent=self.bq_expert_flash()
        )

    @task
    def analyze_and_save_results_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_and_save_results_task'],
            agent=self.bq_expert(),
            context=[self.execute_bigquery_query_task()]
        )


    @task
    def extract_queries_task(self) -> Task:
        return Task(
            config=self.tasks_config['extract_queries_task'],
            agent=self.bq_expert_flash(),
            context=[self.execute_bigquery_query_task()]
        )


    @task
    def analyze_queries_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_queries_task'],
            agent=self.bq_expert(),
            context=[self.extract_queries_task(), self.analyze_and_save_results_task()]
        )

    # @task
    # def design_full_stack_application_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['design_full_stack_application_task'],
    #         agent=self.software_architect(),
    #         context=[self.analyze_and_recommend_task()]
    #     )

    # @task
    # def implement_backend_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['implement_backend_task'],
    #         agent=self.polyglot_developer(),
    #         context=[self.design_full_stack_application_task()]
    #     )

    # @task
    # def implement_frontend_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['implement_frontend_task'],
    #         agent=self.ui_ux_designer(),
    #         context=[self.design_full_stack_application_task()]
    #     )

    # @task
    # def containerize_and_run_task(self) -> Task:
    #     return Task(
    #         config=self.tasks_config['containerize_and_run_task'],
    #         agent=self.software_architect(),
    #         context=[self.implement_backend_task(), self.implement_frontend_task()]
    #     )

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

