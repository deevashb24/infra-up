import requests
import json
from bs4 import BeautifulSoup

def scrape_lda():
    """
    Scraper template for Lucknow Development Authority (lda.up.nic.in)
    """
    print("Initiating LDA Scraper targeting active housing & zoning developments...")
    
    # MOCK EXTRACTION LOGIC
    # response = requests.get('http://lda.up.nic.in/ongoing_projects.php')
    # soup = BeautifulSoup(response.text, 'html.parser')
    # for row in soup.find_all('tr', class_='project_row'):
    #    ...
    
    mock_payload = {
        "title": "विभूति खंड आवासीय परिसर (Vibhuti Khand Housing Complex)",
        "description": "Construction of new residential masterplan.",
        "raw_type": "आवास",
        "authority": "LDA",
        "district": "Lucknow",
        "longitude": 81.0021,
        "latitude": 26.8655,
        "budget": 120.5
    }
    
    res = requests.post("http://localhost:8000/admin/ingest", json=mock_payload)
    print("Ingestion Payload:", res.json())

if __name__ == "__main__":
    scrape_lda()
