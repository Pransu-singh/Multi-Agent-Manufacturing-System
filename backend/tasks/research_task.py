from crewai import Task
from agents.researcher import researcher

def create_research_task(product):
    return Task(
        description=f"Research suppliers and manufacturing data for {product}",
        expected_output="Supplier list with costs, materials and locations",
        agent=researcher
    )
