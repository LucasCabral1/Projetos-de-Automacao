import os
import sqlite3
import requests
import datetime
import time
from dotenv import load_dotenv
import feedparser ### NOVO ###
from email.utils import mktime_tz, parsedate_tz ### NOVO ###

load_dotenv()

# --- CONFIGURATION ---
API_KEY = os.getenv("API_KEY")
DB_NAME = "my_journal.db"
TOPICS = ["sports", "technology", "business", "general"]
RSS_FEEDS = [
    {
        "name": "iclnoticias.com.br", 
        "url": "https://iclnoticias.com.br/feed/",
        "topic": "politics"
    },
    {
        "name": "meutimao.com.br", 
        "url": "https://www.meutimao.com.br/rss/",
        "topic": "sports"
    },
    {
        "name": "brasildefato.com.br", 
        "url": "https://www.brasildefato.com.br/feed/",
        "topic": "politics"
    },
    {
        "name": "www.cartacapital.com.br", 
        "url": "https://www.cartacapital.com.br/feed/",
        "topic": "politics"
    }
]
NEWS_LIMIT_PER_TOPIC = 10
DAYS_TO_KEEP_ARTICLES = 30
# ---------------------

def setup_database(db_name):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            source_name TEXT,
            url TEXT NOT NULL UNIQUE,
            published_at TEXT NOT NULL,
            topic TEXT NOT NULL,
            downloaded_at TEXT NOT NULL,
            generic_news BOOLEAN
        )
        """)
        
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error during setup: {e}")
    finally:
        if conn:
            conn.close()

def fetch_news(api_key, query_value, limit, search_type='topic'):
    """
    Busca notícias por 'topic' (usando top-headlines) ou 'site' (usando search).
    """
    params = {
        'token': api_key,
        'lang': 'pt',
        'country': 'br',
        'max': limit,
    }

    if search_type == 'topic':
        base_url = "https://gnews.io/api/v4/top-headlines"
        params['category'] = query_value
    elif search_type == 'site':
        base_url = "https://gnews.io/api/v4/search"
        params['q'] = f'site:{query_value}'
    else:
        print(f"Tipo de busca inválido: {search_type}")
        return []

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status() 
        data = response.json()
        
        return data.get('articles', [])
            
    except requests.exceptions.RequestException as e:
        print(f"HTTP Request failed: {e}")
        return []
    except Exception as e:
        print(f"An error occurred during fetch: {e}")
        return []

def format_rss_time_to_iso(time_string):
    try:
        time_tuple_with_tz = parsedate_tz(time_string)
        timestamp = mktime_tz(time_tuple_with_tz)
        dt_object = datetime.datetime.fromtimestamp(timestamp)
        return dt_object.isoformat()
    except Exception:
        return datetime.datetime.now().isoformat()

def fetch_news_from_rss(feed_url, limit):
    try:
        feed = feedparser.parse(feed_url)
        articles_list = []
        
        for entry in feed.entries[:limit]:
            
            published_time = entry.get('published', datetime.datetime.now().isoformat())
            
            if not published_time.endswith('Z') and '+' not in published_time:
                 published_time_iso = format_rss_time_to_iso(published_time)
            else:
                 published_time_iso = published_time

            article = {
                'title': entry.get('title'),
                'source': {'name': feed.feed.get('title', 'RSS Source')},
                'url': entry.get('link'),
                'publishedAt': published_time_iso
            }
            articles_list.append(article)
            
        return articles_list
        
    except Exception as e:
        print(f"An error occurred during RSS fetch: {e}")
        return []

def save_articles_to_db(db_name, articles, topic, generic=True):
    if not articles:
        return

    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        current_time = datetime.datetime.now().isoformat()
        articles_to_insert = []
        
        for article in articles:
            title = article.get('title')
            source_name = article.get('source', {}).get('name')
            url = article.get('url')
            published_at = article.get('publishedAt')
            
            if all([title, url, published_at]):
                articles_to_insert.append(
                    (title, source_name, url, published_at, topic, current_time, generic)
                )

        cursor.executemany("""
        INSERT OR IGNORE INTO articles 
            (title, source_name, url, published_at, topic, downloaded_at, generic_news)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, articles_to_insert)
        
        conn.commit()
        print(f"  > Saved {cursor.rowcount} new articles for '{topic}'.")
        
    except sqlite3.Error as e:
        print(f"Database error during save: {e}")
    finally:
        if conn:
            conn.close()

def delete_old_articles(db_name, days_old):
    try:
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_old)
        cutoff_date_str = cutoff_date.isoformat()

        cursor.execute("""
        DELETE FROM articles 
        WHERE published_at < ?
        """, (cutoff_date_str,))
        
        conn.commit()
        print(f"\nCleaning database: Deleted {cursor.rowcount} articles older than {days_old} days.")
        
    except sqlite3.Error as e:
        print(f"Database error during delete: {e}")
    finally:
        if conn:
            conn.close()

def main():
    print("Starting MyJournal...")
    setup_database(DB_NAME)
    
    print("Fetching news articles...")
    for topic in TOPICS:
        print(f"- Fetching topic: '{topic}'")
        articles = fetch_news(API_KEY, topic, NEWS_LIMIT_PER_TOPIC)
        save_articles_to_db(DB_NAME, articles, topic)
        time.sleep(1) 
    
    print("\nFetching news from specific sites (RSS)...")
    for rss in RSS_FEEDS:
        print(f"- Fetching from RSS: '{rss["name"]}'")
        articles = fetch_news_from_rss(rss["url"], NEWS_LIMIT_PER_TOPIC)
        save_articles_to_db(DB_NAME, articles, rss["topic"], generic=False)
        time.sleep(1)
        
    print("\nFetching news from specific sites...")


    delete_old_articles(DB_NAME, DAYS_TO_KEEP_ARTICLES)
    
    print("\nMyJournal run complete.")

if __name__ == "__main__":
    main()