import datetime
import sqlite3
from zoneinfo import ZoneInfo 
import pandas as pd
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func 
from typing import Optional, List
from sqlalchemy.dialects.sqlite import insert as sqlite_insert

from core.helpers import  parse_datetime
from core.models import Article, engine



SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def load_all_articles_as_df():
    session = SessionLocal()
    try:

        query = session.query(
            Article.id.label("ID"),
            Article.title.label("Título"),
            Article.url.label("URL"),
            Article.source_name.label("Fonte"),
            Article.topic.label("Tópico"),
            func.strftime('%Y-%m-%d %H:%M:%S', Article.published_at).label("published_at"),
            Article.generic_news
        ).order_by(Article.published_at.desc())

        df = pd.read_sql(query.statement, session.bind)
        return df
        
    except Exception as e:
        print(f"Ocorreu um erro ao ler o banco de dados para DataFrame: {e}")
        return pd.DataFrame(columns=[
            "ID", "Título", "URL", "Fonte", "Tópico", 
            "published_at", "generic_news"
        ])
    finally:
        session.close()

def get_articles_with_filters(
    topics: Optional[List[str]] = None,
    sources: Optional[List[str]] = None,
    title_search: Optional[str] = None,
    generic_news: Optional[bool] = None
):
    session = SessionLocal()
    try:
        query = session.query(Article)

        if topics:
            query = query.filter(Article.topic.in_(topics))
        
        if sources:
            query = query.filter(Article.source_name.in_(sources))
        
        if title_search:
            query = query.filter(func.lower(Article.title).like(f"%{title_search.lower()}%"))
            
        if generic_news is not None:
            query = query.filter(Article.generic_news == generic_news)
            
        articles = query.order_by(Article.published_at.desc()).all()
        
        return articles
        
    except Exception as e:
        print(f"Ocorreu um erro ao consultar o DB com ORM: {e}")
        return []
    finally:
        session.close()
        
def save_articles_to_db(articles, topic, generic=True):
    if not articles:
        return

    current_time = datetime.datetime.now(ZoneInfo("America/Sao_Paulo"))
    

    articles_to_insert = []

    for article in articles:
        title = article.get('title')
        url = article.get('url')
        published_at = article.get('publishedAt')

        
        if not all([title, url, published_at]):
            continue

        source = article.get('source')

            
        published_at_brazil = parse_datetime(published_at)

        article_data = {
            'title': title,
            'source_name': source['name'] if source and 'name' in source else 'Unknown',
            'url': url,
            'published_at': published_at_brazil,
            'topic': topic,
            'downloaded_at': current_time,
            'generic_news': generic
        }

        articles_to_insert.append(article_data)
        
    if(articles_to_insert == []):
        return

    with SessionLocal() as session:
        try:
            stmt = sqlite_insert(Article).values(articles_to_insert)
            stmt = stmt.on_conflict_do_nothing(index_elements=['url'])
            
            result = session.execute(stmt)
            session.commit()
            
            print(f"  > Saved {result.rowcount} new articles for '{topic}'.")
        except Exception as e:
            print(f"An error occurred during fetch: {e}")
        return []
                 
