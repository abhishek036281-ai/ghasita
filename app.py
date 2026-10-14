from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import urllib.parse
import re
import traceback

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

WIKI_HEADERS = {'User-Agent': 'GhasitaFinder/5.0 (music-discovery@local.app)'}

@app.route('/')
def index():
    return app.send_static_file('index.html')

def get_itunes_songs(term):
    try:
        url = f"https://itunes.apple.com/search?term={urllib.parse.quote(term)}&entity=song&limit=5"
        r = requests.get(url, timeout=5).json()
        return r.get('results', [])
    except Exception:
        return []

def search_wikipedia(term):
    try:
        # Search list
        url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(term)}&utf8=&format=json"
        res = requests.get(url, headers=WIKI_HEADERS, timeout=5).json()
        items = res.get('query', {}).get('search', [])
        if not items:
            return None, None
            
        term_words = [w.lower() for w in re.split(r'\s+', term) if len(w) > 2]
        best_item = items[0]
        for it in items[:6]:
            t_lower = it['title'].lower()
            if term_words and all(tw in t_lower for tw in term_words):
                best_item = it
                break
                
        title = best_item['title']
        
        # Get full intro extract (includes birth dates, full names, etc.)
        ext_url = f"https://en.wikipedia.org/w/api.php?action=query&prop=extracts&exintro=true&explaintext=true&titles={urllib.parse.quote(title)}&format=json"
        ext_res = requests.get(ext_url, headers=WIKI_HEADERS, timeout=5).json()
        pages = ext_res.get('query', {}).get('pages', {})
        for k, v in pages.items():
            if k != '-1' and v.get('extract'):
                return title, v.get('extract').strip()
                
    except Exception as e:
        print("Wiki search error:", e)
    return None, None

def resolve_and_answer(user_text, artist_context=""):
    user_lower = user_text.lower().strip()
    artist_context = artist_context.strip()
    
    # Identify subject
    subject = artist_context
    
    # Clean question prefixes and suffixes
    q_clean = user_lower
    prefixes = [
        "who is ", "who are ", "what is ", "where does ", "where is ", "when was ",
        "tell me about ", "tell me ", "details of ", "date of birth of ", "dob of ",
        "kya hai ", "kaun hai ", "kon hai ", "which singer ", "whose song is "
    ]
    for p in prefixes:
        if q_clean.startswith(p):
            q_clean = q_clean[len(p):].strip()
            
    suffixes = [
        " date of birth", " dob", " birthday", " age", " net worth", " songs", 
        " wife", " family", " biography", " bio", " live", " address", " singer"
    ]
    for s in suffixes:
        if q_clean.endswith(s):
            q_clean = q_clean[:-len(s)].strip()
            
    pronouns = {"he", "she", "they", "him", "her", "this", "it", "his", "their", "yeh", "ye", "wo", "woh"}
    cleaned_words = set(q_clean.split())
    
    if q_clean and not (cleaned_words & pronouns):
        # User specified a particular subject or song in their prompt
        subject = q_clean.title()
    elif not subject:
        subject = q_clean.title()
        
    print(f"Resolving: user_text='{user_text}', artist='{artist_context}' -> subject='{subject}'")
    
    # 1. Query Wikipedia for subject
    title, extract = search_wikipedia(subject)
    
    # 2. Check if asking about Date of Birth / Age
    if any(k in user_lower for k in ["date of birth", "dob", "born", "birthday", "age", "janam"]):
        if extract:
            m = re.search(r'\((?:born\s+)?([^\)]*?\b\d{4}\b[^\)]*?)\)', extract)
            if m:
                return f"<strong>{title}</strong> was born on <strong>{m.group(1)}</strong>.<br><br>{extract}", f"Wikipedia ({title})"
            return f"<strong>{title}</strong>:<br>{extract}", f"Wikipedia ({title})"
            
    # 3. Check if general bio or who is question
    if any(k in user_lower for k in ["who", "kon", "kaun", "about", "bio", "singer", "artist", "details"]):
        if extract:
            return extract, f"Wikipedia ({title})"

    # 4. Check iTunes for music releases if extract is missing or if songs were asked
    itunes_songs = get_itunes_songs(subject)
    if any(k in user_lower for k in ["song", "hit", "album", "track", "music", "gana"]):
        if itunes_songs:
            song_lines = [f"• <strong>{s.get('trackName')}</strong> by {s.get('artistName')} <em>({s.get('collectionName', 'Single')})</em>" for s in itunes_songs[:5]]
            response = f"Top songs for <strong>{subject}</strong>:<br>" + "<br>".join(song_lines)
            if extract:
                response += f"<br><br><strong>About:</strong> {extract[:250]}..."
            return response, "Music Database & Wikipedia"

    # 5. Fallback with whatever extract we found
    if extract:
        return extract, f"Wikipedia ({title})"
        
    # 6. Fallback to iTunes song info
    if itunes_songs:
        song_lines = [f"• <strong>{s.get('trackName')}</strong> by {s.get('artistName')}" for s in itunes_songs[:4]]
        return f"Found music tracks for <strong>'{subject}'</strong>:<br>" + "<br>".join(song_lines), "iTunes Music"
        
    return f"I couldn't find detailed info for '{user_text}'. Try asking about an artist's songs, birth date, or biography!", "Singer AI"

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json or {}
        user_text = data.get('userText') or data.get('query') or ''
        artist_context = data.get('artist') or ''
        
        if not user_text:
            return jsonify({"error": "No query provided"}), 400
            
        answer, source = resolve_and_answer(user_text, artist_context)
        return jsonify({
            "answer": answer,
            "source": source
        })

    except Exception as e:
        print(traceback.format_exc())
        return jsonify({
            "answer": "Something went wrong while fetching the answer.",
            "source": "Error"
        }), 500

if __name__ == '__main__':
    print("Starting backend server on http://localhost:5000")
    app.run(debug=True, port=5000)
