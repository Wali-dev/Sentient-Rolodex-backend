from crewai_tools import WebScraperTool

# Scraper for extracting contract details from OTT platform
netflix_scraper = WebScraperTool(url='https://help.netflix.com/legal/termsofuse')
prime_scraper = WebScraperTool(url='https://www.primevideo.com/help?nodeId=202095490')
hotstar_scraper = WebScraperTool(url='https://www.hotstar.com/in/terms-of-use')

# A tool to scrape data from multiple OTT platforms
ott_scrapers = [netflix_scraper, prime_scraper, hotstar_scraper]
