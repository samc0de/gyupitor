from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List
from cag.me.tools.openhands_tool import OpenHandsTool
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class Me():
    """Me crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def bq_expert(self) -> Agent:
        return Agent(
            config=self.agents_config['bq_expert'], # type: ignore[index]
            verbose=True
        )

    @agent
    def software_architect(self) -> Agent:
        return Agent(
            config=self.agents_config['software_architect'], # type: ignore[index]
            verbose=True
        )

    @agent
    def ui_ux_designer(self) -> Agent:
        return Agent(
            config=self.agents_config['ui_ux_designer'], # type: ignore[index]
            verbose=True
        )

    @agent
    def polyglot_developer(self) -> Agent:
        return Agent(
            config=self.agents_config['polyglot_developer'], # type: ignore[index]
            tools=[OpenHandsTool()],
            verbose=True
        )

    @agent
    def system_ai_monitor(self) -> Agent:
        return Agent(
            config=self.agents_config['system_ai_monitor'], # type: ignore[index]
            verbose=True
        )

    @agent
    def customer_chatbot(self) -> Agent:
        return Agent(
            config=self.agents_config['customer_chatbot'], # type: ignore[index]
            verbose=True
        )

    @task
    def initial_bq_analysis_task(self) -> Task:
        return Task(
            config=self.tasks_config['initial_bq_analysis_task'], # type: ignore[index]
        )

    @task
    def initial_architecture_task(self) -> Task:
        return Task(
            config=self.tasks_config['initial_architecture_task'], # type: ignore[index]
        )

    @task
    def initial_ui_design_task(self) -> Task:
        return Task(
            config=self.tasks_config['initial_ui_design_task'], # type: ignore[index]
        )

    @task
    def development_kickoff_task(self) -> Task:
        return Task(
            config=self.tasks_config['development_kickoff_task'], # type: ignore[index]
        )

    @task
    def user_update_task(self) -> Task:
        return Task(
            config=self.tasks_config['user_update_task'], # type: ignore[index]
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
