import requests

def scrape_nhai():
    """
    NHAI (nhai.gov.in) Scraper Template explicitly targeting UP regions.
    """
    print("Initiating NHAI Expressway Tracker...")
    
    mock_payload = {
        "title": "Varanasi Ring Road Phase 3",
        "description": "Six-lane bypass project.",
        "raw_type": "राजमार्ग", # Highway
        "authority": "NHAI",
        "district": "Varanasi",
        "longitude": 82.9739,
        "latitude": 25.3176,
        "budget": 2040.0
    }
    
    requests.post("http://localhost:8000/admin/ingest", json=mock_payload)

if __name__ == "__main__":
    scrape_nhai()
