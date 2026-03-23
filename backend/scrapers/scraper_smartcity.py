import requests

def scrape_smartcity():
    """
    Scraper template for Lucknow Smart City (lucknowsmartcity.com)
    Targeting specific Pan-City IT and Road infrastructure works.
    """
    print("Initiating Smart City Scraper...")
    
    mock_payload = {
        "title": "Smart Traffic Intersections - Phase 2",
        "description": "Installation of adaptive traffic signals and cameras.",
        "raw_type": "सड़क निर्माण",
        "authority": "Smart City Lucknow",
        "district": "Lucknow",
        "longitude": 80.9322,
        "latitude": 26.8400,
        "budget": 45.0
    }
    
    res = requests.post("http://localhost:8000/admin/ingest", json=mock_payload)
    print("Ingestion Response:", res.json())

if __name__ == "__main__":
    scrape_smartcity()
