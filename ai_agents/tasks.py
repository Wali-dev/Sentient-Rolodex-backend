from crewai import Task
from agents import contract_researcher, legal_expert
from tools import ott_scrapers

# Task to extract contract information
contract_scrape_task = Task(
    description="Scrape OTT platforms (Netflix, Prime, Hotstar) to extract contract agreement terms.",
    expected_output="Raw contract text from OTT platforms.",
    tools=ott_scrapers,
    agent=contract_researcher
)

# Task to check for contract breaches
contract_check_task = Task(
    description="""Analyze contract agreements and check for breaches based on following
     "terms": [
                {
                    "clause": "Payment Terms",
                    "description": "Payment must be made within 30 days of invoice."
                },
                {
                    "clause": "Confidentiality",
                    "description": "Both parties agree to keep all shared information confidential."
                }
            ] """,
    expected_output="A report highlighting any contract violations.",
    agent=legal_expert
)
