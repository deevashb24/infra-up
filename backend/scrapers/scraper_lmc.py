import requests

def scrape_lmc():
    """
    Lucknow Municipal Corporation (lmc.up.nic.in) Scraper Template.
    Targets local road repairs and zone-wise civic works.
    """
    print("Initiating LMC Civic Works Scraper...")
    
    mock_payload = {
        "title": "Alambagh Zone Drain Cleaning & Repair",
        "description": "Pre-monsoon sanitation prep.",
        "raw_type": "सीवर", # Hindi for sewer
        "authority": "LMC",
        "district": "Lucknow",
        "longitude": 80.9015,
        "latitude": 26.8123,
        "budget": 2.5
    }
    
    requests.post("http://localhost:8000/admin/ingest", json=mock_payload)

if __name__ == "__main__":
    scrape_lmc()
