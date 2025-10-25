import requests
import pandas as pd
from bs4 import BeautifulSoup
import sys

TARGET_URL = "https://www.scrapethissite.com/pages/simple/"
OUTPUT_FILE = "dados_paises.csv"

def fetch_page(url):
    print(f"Fetching data from: {url}")
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}", file=sys.stderr)
        return None

def parse_countries_data(html_content):
    print("Parsing HTML content...")
    soup = BeautifulSoup(html_content, "html.parser")
    
    countries_data = []
    
    country_cards = soup.find_all("div", class_="col-md-4 country")
    
    if not country_cards:
        print("No country cards found. The site's HTML may have changed.")
        return []

    for card in country_cards:
        try:
            name = card.find("h3").text.strip()
            capital = card.find("span", class_="country-capital").text.strip()
            population_text = card.find("span", class_="country-population").text.strip()
            population = int(population_text)
            
            countries_data.append({
                "Nome": name,
                "Capital": capital,
                "Populacao": population
            })
            
        except (AttributeError, ValueError) as e:
            print(f"Error parsing a country. Skipping. Error: {e}")
            
    print(f"Total of {len(countries_data)} countries found and parsed.")
    return countries_data

def save_data_to_csv(data, filename):
    if not data:
        print("No data to save.")
        return

    try:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Data successfully saved to: {filename}")
        
    except IOError as e:
        print(f"Error saving CSV file: {e}", file=sys.stderr)
    except Exception as e:
        print(f"An unexpected error occurred while saving data: {e}", file=sys.stderr)

def main():
    html = fetch_page(TARGET_URL)
    
    if html is None:
        print("Failed to get HTML. Exiting script.")
        sys.exit(1)
        
    countries = parse_countries_data(html)
    
    if countries:
        save_data_to_csv(countries, OUTPUT_FILE)
    else:
        print("No data was extracted. CSV file will not be created.")

if __name__ == "__main__":
    main()