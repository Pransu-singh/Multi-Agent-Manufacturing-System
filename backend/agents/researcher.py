from crewai import Agent
from tools.web_search import supplier_search

researcher = Agent(
    role="Manufacturing Researcher",
    goal="Find suppliers, raw materials, costs and locations",
    backstory="Expert in industrial sourcing and supply chain research",
    tools=[supplier_search],
    verbose=True
)
