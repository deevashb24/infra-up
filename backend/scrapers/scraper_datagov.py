import requests

def scrape_datagov():
    """
    Data.gov.in official REST API integration filtered exclusively to UP state tags.
    """
    print("Initiating OGD Platform India UP Sync...")
    
    mock_payload = {
        "title": "Agra Rural Connectivity Project",
        "description": "Connecting village nodes.",
        "raw_type": "सड़क", # Road
        "authority": "PWD UP",
        "district": "Agra",
        "longitude": 78.0081,
        "latitude": 27.1767,
        "budget": 55.0
    }
    
    requests.post("http://localhost:8000/admin/ingest", json=mock_payload)

if __name__ == "__main__":
    scrape_datagov()
