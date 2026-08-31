import requests
import json
from datetime import datetime
from pathlib import Path

CACHE_DIR = Path(__file__).resolve().parent / "cache"
CACHE_FILE = CACHE_DIR / "daily_fact.json"

# API: uselessfacts.jsoup.com/random.json
FACT_URL = "https://uselessfacts.jsoup.com/random.json"

def _load_cached_fact():
    if not CACHE_FILE.exists():
        return None
    
    try:
        with open(CACHE_FILE, "r") as f:
            data = json.load(f)
        
        cached_date = data.get("date")
        today = datetime.now().strftime("%Y-%m-%d")
        
        if cached_date == today:
            return data.get("fact")
    except Exception as e:
        print(f"Error loading cache: {e}")
    
    return None

def _save_fact_to_cache(fact):
    try:
        CACHE_DIR.mkdir(exist_ok=True)
        data = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "fact": fact
        }
        with open(CACHE_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        print(f"Error saving cache: {e}")

def get_daily_fact():
    # Try cache first
    cached = _load_cached_fact()
    if cached:
        return cached
    
    # Fetch from API
    try:
        resp = requests.get(FACT_URL, timeout=5)
        resp.raise_for_status()
        js = resp.json()
        fact = js.get("text", "No fact available")
        
        # Save to cache
        _save_fact_to_cache(fact)
        return fact
    except Exception as e:
        print(f"Error fetching daily fact: {e}")
        return "Did you know? Interesting facts coming soon!"
