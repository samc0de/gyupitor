from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from me.tools.openhands_tool import OpenHandsTool
from langchain_google_vertexai import VertexAI
from me.tools.file_tools import WriteFileTool
from me.tools.bigquery_tool import BigQueryTool
# If you want to run a snippet of code before or after the crew starts,
from me.tools.shell_tool import ShellTool
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Me():
    """Me crew"""

    agents: List[BaseAgent]
    tasks: List[Task]
    llm: VertexAI
    def __init__(self) -> None:
        self.pro_llm = VertexAI(
            model_name="gemini-2.5-pro",
            temperature=0.2,
            top_p=0.9,
            top_k=40,
            max_output_tokens=4096
        )
        self.flash_llm = VertexAI(
            model_name="gemini-2.5-flash",
            temperature=0.2,
            top_p=0.9,
            top_k=40,
            max_output_tokens=4096
        )
        self.file_write_tool = WriteFileTool()
        self.bigquery_tool = BigQueryTool()
        self.shell_tool = ShellTool()
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def bq_expert(self) -> Agent:
        return Agent(
            config=self.agents_config['bq_expert'], # type: ignore[index]
            tools=[self.bigquery_tool],
            llm=self.pro_llm,
            verbose=True
        )

    @agent
    def software_architect(self) -> Agent:
        return Agent(
            config=self.agents_config['software_architect'], # type: ignore[index]
            tools=[self.file_write_tool, self.shell_tool],
            llm=self.pro_llm,
            verbose=True
        )

    @agent
    def ui_ux_designer(self) -> Agent:
        return Agent(
            config=self.agents_config['ui_ux_designer'], # type: ignore[index]
            llm=self.pro_llm,
            verbose=True
        )

    @agent
    def polyglot_developer(self) -> Agent:
        return Agent(
            config=self.agents_config['polyglot_developer'], # type: ignore[index]
            tools=[OpenHandsTool(), self.file_write_tool, self.shell_tool],
            llm=self.flash_llm,
            verbose=True
        )

    @agent
    def system_ai_monitor(self) -> Agent:
        return Agent(
            config=self.agents_config['system_ai_monitor'], # type: ignore[index]
            tools=[self.file_write_tool],
            llm=self.flash_llm,
            verbose=True
        )



    @agent
    def customer_chatbot(self) -> Agent:
        return Agent(
            config=self.agents_config['customer_chatbot'], # type: ignore[index]
            tools=[self.file_write_tool],
            llm=self.flash_llm,
            verbose=True
        )

    @task
    def execute_bq_query_task(self) -> Task:
        return Task(
            config=self.tasks_config['execute_bq_query_task'],
            agent=self.bq_expert()
        )

    @task
    def analyze_bq_results_task(self) -> Task:
        return Task(
            config=self.tasks_config['analyze_bq_results_task'],
            agent=self.bq_expert(),
            context=[self.execute_bq_query_task()]
        )

    @task
    def initial_architecture_task(self) -> Task:
        return Task(
            config=self.tasks_config['initial_architecture_task'],
            context=[self.analyze_bq_results_task()]
        )

    @task
    def initial_ui_design_task(self) -> Task:
        return Task(
            config=self.tasks_config['initial_ui_design_task'], # type: ignore[index]
            context=[self.initial_architecture_task()]
        )

    @task
    def development_kickoff_task(self) -> Task:
        return Task(
            config=self.tasks_config['development_kickoff_task'], # type: ignore[index]
            context=[self.initial_architecture_task(), self.initial_ui_design_task()]
        )

    @task
    def deployment_task(self) -> Task:
        return Task(
            config=self.tasks_config['deployment_task'], # type: ignore[index]
            context=[self.development_kickoff_task()]
        )

    @task
    def user_update_task(self) -> Task:
        return Task(
            config=self.tasks_config['user_update_task'], # type: ignore[index]
            context=[self.deployment_task()]
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Me crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
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

