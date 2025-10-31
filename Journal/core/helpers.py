
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from dateutil import parser


def find_rss_feed(site_url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }
        
        response = requests.get(site_url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        rss_link = soup.find(
            'link', 
            rel='alternate', 
            type='application/rss+xml'
        )
        
        if not rss_link:
             rss_link = soup.find(
                'link', 
                rel='alternate', 
                type='application/atom+xml'
            )

        if rss_link and rss_link.get('href'):
            feed_url = rss_link.get('href')
            
            if not feed_url.startswith(('http://', 'https://')):
                feed_url = urljoin(site_url, feed_url)
            
            print(f"get url from: {feed_url}")
            return feed_url

    except requests.exceptions.RequestException as e:
        print(f"Unable to get {site_url}: {e}")
        
    
    common_paths = ['/feed/', '/rss/', '/feed', '/rss.xml', '/feed.xml']
    
    for path in common_paths:
        test_url = urljoin(site_url, path)
        
        try:
            test_response = requests.head(test_url, headers=headers, timeout=5, allow_redirects=True)
            if test_response.status_code == 200:
                print(f"get url from: {test_url}")
                return test_url
        except requests.exceptions.RequestException:
            continue

    return None

def parse_datetime(date_string: str | None) -> datetime | None:
    if not date_string or not isinstance(date_string, str):
        return None
        
    try:
        return parser.parse(date_string)
        
    except (parser.ParserError, ValueError):
        print(f"error to parse date: {date_string}")
        return None