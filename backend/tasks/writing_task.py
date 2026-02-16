from crewai import Task
from agents.writer import writer

def create_writing_task():
    return Task(
        description=(
            "Generate a structured manufacturing report with headings, tables, "
            "cost analysis and recommendations"
        ),
        expected_output="Professional manufacturing report",
        agent=writer
    )
