import requests

def scrape_upjn():
    """
    Jal Nigam UP (upjn.org) Water Infrastructure Scraper.
    """
    print("Initiating UP Jal Nigam Tracker...")
    
    mock_payload = {
        "title": "Kanpur South Water Supply Network",
        "description": "Laying deep pipelines for drinking water.",
        "raw_type": "जल कार्य", # Water works
        "authority": "Jal Nigam UP",
        "district": "Kanpur",
        "longitude": 80.3319,
        "latitude": 26.4499,
        "budget": 450.0
    }
    
    requests.post("http://localhost:8000/admin/ingest", json=mock_payload)

if __name__ == "__main__":
    scrape_upjn()
