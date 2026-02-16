from crewai import Crew
from tasks.research_task import create_research_task
from tasks.writing_task import create_writing_task

def run_crew(product_name):
    research_task = create_research_task(product_name)
    writing_task = create_writing_task()

    crew = Crew(
        agents=[research_task.agent, writing_task.agent],
        tasks=[research_task, writing_task],
        verbose=True
    )

    return crew.kickoff()
