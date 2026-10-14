import requests
from bs4 import BeautifulSoup
import urllib.parse

def test_lite():
    url = "https://lite.duckduckgo.com/lite/"
    data = {"q": "date of birth of pawan singh"}
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    res = requests.post(url, data=data, headers=headers)
    soup = BeautifulSoup(res.text, 'html.parser')
    
    snippets = soup.select(".result-snippet")
    print("Found snippets:", len(snippets))
    if snippets:
        print("Snippet 1:", snippets[0].get_text(strip=True))

if __name__ == "__main__":
    test_lite()
