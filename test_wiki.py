import requests
import urllib.parse

def get_wiki_summary(search_term):
    headers = {"User-Agent": "Mozilla/5.0"}
    search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(search_term)}&utf8=&format=json"
    res = requests.get(search_url, headers=headers).json()
    if res.get("query", {}).get("search"):
        best_title = res["query"]["search"][0]["title"]
        print(f"[{search_term}] -> Title found: {best_title}")
        return best_title
    return None

def heuristic_search(query):
    words = query.split()
    queries = []
    if len(words) >= 2: queries.append(" ".join(words[:2]))
    if len(words) >= 3: queries.append(" ".join(words[:3]))
    queries.append(query)
    
    for q in queries:
        title = get_wiki_summary(q)
        if title:
            return title

heuristic_search("pawan singh date of birth")
heuristic_search("drake net worth")
heuristic_search("badshah")
