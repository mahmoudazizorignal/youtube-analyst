import os
import yaml
from typing import List
from crewai import (
    Agent, 
    Task, 
    LLM, 
    Crew as crewai_crew, 
    Process,
)
from core.types import CrewResponse
from crewai_tools import FileReadTool


class Crew:
    
    def __init__(self, llm: LLM, verbose: bool = False):
        self.file_read_tool = FileReadTool()
        self.config_path = os.path.join(
            os.path.dirname( os.path.dirname(__file__) ),
            "assets/config.yaml",
        )
        with open(self.config_path, "r") as file:
            self.config = yaml.safe_load(file)
        
        self.analysis_agent = Agent(
            role=self.config["agents"][0]["role"],
            goal=self.config["agents"][0]["goal"],
            backstory=self.config["agents"][0]["backstory"],
            verbose=verbose,
            tools=[self.file_read_tool],
            llm=llm,
        )

        self.response_synthesizer_agent = Agent(
            role=self.config["agents"][1]["role"],
            goal=self.config["agents"][1]["goal"],
            backstory=self.config["agents"][1]["backstory"],
            verbose=verbose,
            llm=llm,
        )

        self.analysis_task = Task(
            description=self.config["tasks"][0]["description"],
            expected_output=self.config["tasks"][0]["expected_output"],
            agent=self.analysis_agent
        )

        self.response_task = Task(
            description=self.config["tasks"][1]["description"],
            expected_output=self.config["tasks"][1]["expected_output"],
            agent=self.response_synthesizer_agent
        )
        
        self.crew = crewai_crew(
            agents=[self.analysis_agent, self.response_synthesizer_agent],
            tasks=[self.analysis_task, self.response_task],
            process=Process.sequential,
            verbose=verbose,
        )
    
    def kickoff(self, file_paths: List[str]) -> CrewResponse:
        return self.crew.kickoff(
            inputs={
                "file_paths": ", ".join(file_paths),
            }
        )
