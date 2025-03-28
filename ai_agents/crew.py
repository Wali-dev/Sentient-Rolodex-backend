from crewai import Crew, Process
from agents import contract_researcher, legal_expert
from tasks import contract_scrape_task, contract_check_task

# Define the Crew
crew = Crew(
    agents=[contract_researcher, legal_expert],
    tasks=[contract_scrape_task, contract_check_task],
    process=Process.sequential,
    memory=True,
    cache=True
)

# Start execution
result = crew.kickoff()
print(result)
