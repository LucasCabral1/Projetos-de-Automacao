from fastapi import FastAPI, Query
from typing import Optional, List


from core.database import get_articles_with_filters 
from core.schemas import Article 

app = FastAPI(
    title="MyJournal API",
    description="API para acessar os artigos coletados pelo MyJournal.",
    version="1.0.0"
)

@app.get("/articles/", response_model=List[Article])
def read_articles(
    topics: Optional[List[str]] = Query(None),
    sources: Optional[List[str]] = Query(None),
    search: Optional[str] = Query(None, alias="title_search"),
    generic: Optional[bool] = Query(None, alias="generic_news")
):
    articles_data = get_articles_with_filters(
        topics=topics,
        sources=sources,
        title_search=search,
        generic_news=generic
    )
    return articles_data

# ... (o resto da sua API) ...