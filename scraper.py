import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import time
import random

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

# The main page for the Premier League
LEAGUE_URL = "https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1"
BASE_DOMAIN = "https://www.transfermarkt.com"

def get_club_urls(scraper):
    """
    Scrapes the main league page to find the URLs for all 20 clubs.
    """
    print("Fetching club links from the Premier League main page...")
    response = scraper.get(LEAGUE_URL, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Transfermarkt stores the main club table under this specific class
    table = soup.find('table', class_='items')
    club_links = []
    
    rows = table.find('tbody').find_all('tr')
    for row in rows:
        # The club link is usually in the second column (td) under an 'a' tag
        td = row.find_all('td', class_='hauptlink')
        if not td:
            continue
            
        a_tag = td[0].find('a')
        if a_tag and 'href' in a_tag.attrs:
            club_name = a_tag.text.strip()
            raw_link = a_tag['href']
            
            # Transfermarkt links point to the 'startseite' (overview). 
            # We need to change it to the detailed squad view ('kader' + '/plus/1')
            detailed_link = raw_link.replace('startseite', 'kader') + "/plus/1"
            full_url = BASE_DOMAIN + detailed_link
            
            club_links.append({"club_name": club_name, "url": full_url})
            
    print(f"Found {len(club_links)} clubs.")
    return club_links

def clean_market_value(value_str):
    if not value_str or value_str == '-': return 0
    value_str = value_str.replace('€', '').strip()
    if 'm' in value_str: return int(float(value_str.replace('m', '')) * 1_000_000)
    elif 'k' in value_str: return int(float(value_str.replace('k', '')) * 1_000)
    return 0

def scrape_team_data(scraper, url, club_name, scrape_date):
    """
    Scrapes the player data for a single club.
    """
    print(f"Scraping {club_name}...")
    response = scraper.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    table = soup.find('table', class_='items')
    if not table: return []

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
    # Create one scraper session to maintain cookies
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False})
    scrape_date = datetime.date.today().isoformat()
    
    all_league_players = []
    
    # 1. Get all 20 club URLs dynamically
    clubs = get_club_urls(scraper)
    
    # 2. Loop through each club and scrape their players
    for club in clubs:
        team_data = scrape_team_data(scraper, club['url'], club['club_name'], scrape_date)
        all_league_players.extend(team_data)
        
        # CRITICAL: Be polite to the server to avoid getting IP banned
        sleep_time = random.uniform(2.0, 4.0) 
        time.sleep(sleep_time)
        
    # 3. Export the massive dataset
    if all_league_players:
        df = pd.DataFrame(all_league_players)
        print(f"\n--- Scraping Complete: Found {len(df)} total players ---")
        
        filename = f"premier_league_values_{scrape_date}.parquet"
        df.to_parquet(filename, index=False)
        print(f"Data successfully saved to {filename}")
        