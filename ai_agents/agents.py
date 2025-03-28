from crewai import Agent
from .tools import ott_scrapers

# Contract Researcher Agent
contract_researcher = Agent(
    role="OTT Contract Analyst",
    goal="Analyze OTT platform contracts and identify any breaches.",
    tools=ott_scrapers,
    verbose=True
)

# Legal Expert Agent
legal_expert = Agent(
    role="Legal Compliance Checker",
    goal="Compare extracted contract data with predefined contract terms and flag violations.",
    verbose=True
)
