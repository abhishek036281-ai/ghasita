import requests
import urllib.parse
import json

def test_scrape():
    query = "where does pawan singh live"
    # Search for the best Wikipedia page
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&utf8=&format=json"
    res = requests.get(search_url).json()
    
    if res.get("query", {}).get("search"):
        best_title = res["query"]["search"][0]["title"]
        print("Best match:", best_title)
        
        # Get extract
        summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(best_title)}"
        summary_res = requests.get(summary_url).json()
        print("Extract:", summary_res.get("extract", "No extract"))

if __name__ == "__main__":
    test_scrape()
