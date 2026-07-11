import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import os
import time
import random

# Read the ScraperAPI key from the environment (GitHub Actions will inject this)
API_KEY = os.getenv("SCRAPER_API_KEY")

# If testing locally without the key, this will remind you
if not API_KEY:
    print("WARNING: No SCRAPER_API_KEY found. Script may fail if running in the cloud.")

LEAGUE_URL = "https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1"
BASE_DOMAIN = "https://www.transfermarkt.com"

def get_proxied_url(target_url):
    """Wraps the target URL in the ScraperAPI proxy."""
    if API_KEY:
        return f"http://api.scraperapi.com?api_key={API_KEY}&url={target_url}"
    return target_url

def get_club_urls():
    print("Fetching club links from the Premier League main page...")
    
    # We use the proxy URL here
    response = requests.get(get_proxied_url(LEAGUE_URL))
    
    if response.status_code != 200:
        print(f"Failed to fetch league page: HTTP {response.status_code}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    table = soup.find('table', class_='items')
    
    # --- ERROR HANDLING ADDED HERE ---
    if not table:
        print("CRITICAL ERROR: Could not find the main table. Cloudflare might have blocked the request.")
        return []
    # ---------------------------------

    club_links = []
    rows = table.find('tbody').find_all('tr')
    for row in rows:
        td = row.find_all('td', class_='hauptlink')
        if not td: continue
            
        a_tag = td[0].find('a')
        if a_tag and 'href' in a_tag.attrs:
            club_name = a_tag.text.strip()
            detailed_link = a_tag['href'].replace('startseite', 'kader') + "/plus/1"
            club_links.append({"club_name": club_name, "url": BASE_DOMAIN + detailed_link})
            
    print(f"Found {len(club_links)} clubs.")
    return club_links

def clean_market_value(value_str):
    if not value_str or value_str == '-': return 0
    value_str = value_str.replace('€', '').strip()
    if 'm' in value_str: return int(float(value_str.replace('m', '')) * 1_000_000)
    elif 'k' in value_str: return int(float(value_str.replace('k', '')) * 1_000)
    return 0

def scrape_team_data(url, club_name, scrape_date):
    print(f"Scraping {club_name}...")
    
    # We use the proxy URL here too
    response = requests.get(get_proxied_url(url))
    soup = BeautifulSoup(response.text, 'html.parser')
    
    table = soup.find('table', class_='items')
    if not table: 
        print(f"Failed to find player table for {club_name}")
        return []

    players_data = []
    rows = table.find('tbody').find_all('tr', class_=['odd', 'even'])
    
    for row in rows:
        try:
            name_cell = row.find('td', class_='hauptlink')
            player_name = name_cell.text.strip() if name_cell else "Unknown"
            
            cells = row.find_all('td', class_='zentriert')
            age = cells[1].text.strip() if len(cells) > 1 else "Unknown"
            
            value_cell = row.find('td', class_='rechts hauptlink')
            raw_value = value_cell.text.strip() if value_cell else "0"
            clean_value = clean_market_value(raw_value)
            
            players_data.append({
                "scrape_date": scrape_date,
                "league": "Premier League",
                "club": club_name,
                "player_name": player_name,
                "age": age,
                "raw_value_string": raw_value,
                "market_value_eur": clean_value
            })
        except Exception:
            continue
            
    return players_data

if __name__ == "__main__":
    scrape_date = datetime.date.today().isoformat()
    all_league_players = []
    
    clubs = get_club_urls()
    
    for club in clubs:
        team_data = scrape_team_data(club['url'], club['club_name'], scrape_date)
        all_league_players.extend(team_data)
        time.sleep(random.uniform(1.0, 2.5))
        
    if all_league_players:
        df = pd.DataFrame(all_league_players)
        print(f"\n--- Scraping Complete: Found {len(df)} total players ---")
        
        filename = f"premier_league_values_{scrape_date}.parquet"
        df.to_parquet(filename, index=False)
        print(f"Data successfully saved to {filename}")