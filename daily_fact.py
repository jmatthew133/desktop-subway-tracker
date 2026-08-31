import requests
import json
import urllib3
from datetime import datetime
from pathlib import Path

# Suppress SSL warnings for Raspberry Pi compatibility
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CACHE_DIR = Path(__file__).resolve().parent / "cache"
CACHE_FILE = CACHE_DIR / "daily_fact.json"

FACT_URL = "https://www.drivebird.com/api/facts/today"

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
        print("Using cached fact")
        return cached
    
    # Fetch from API
    try:
        # Disable SSL verification for Raspberry Pi compatibility
        resp = requests.get(FACT_URL, timeout=5, verify=False)
        resp.raise_for_status()
        js = resp.json()
        
        # Extract fact from drivebird response: {"data": {"fact": "..."}}
        fact = js.get("data", {}).get("fact")
        
        if fact:
            _save_fact_to_cache(fact)
            print("Fetched from API")
            return fact
    except Exception as e:
        print(f"Error fetching daily fact: {e}")
    
    # Fallback if API fails
    print("[Fact] Using fallback message")
    return "Did you know? Something interesting about the world!"
