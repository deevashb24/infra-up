import requests

def scrape_pwd():
    """
    Scraper template for UP Public Works Department (uppwd.gov.in)
    Extracts high-budget state highway and district road networks.
    """
    print("Initiating UP PWD Scraper...")
    
    mock_payload = {
        "title": "Gorakhpur Link Road Patchwork",
        "description": "Extensive patchwork and widening.",
        "raw_type": "मार्ग",
        "authority": "PWD UP",
        "district": "Gorakhpur",
        "longitude": 83.3732,
        "latitude": 26.7606,
        "budget": 350.0
    }
    
    res = requests.post("http://localhost:8000/admin/ingest", json=mock_payload)
    print(res.json())

if __name__ == "__main__":
    scrape_pwd()
