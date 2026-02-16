from crewai import Agent

writer = Agent(
    role="Manufacturing Report Writer",
    goal="Convert research into professional manufacturing reports",
    backstory="Expert technical writer for manufacturing intelligence",
    verbose=True
)
