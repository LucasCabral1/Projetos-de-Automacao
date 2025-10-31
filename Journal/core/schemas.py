# core/schemas.py

from pydantic import BaseModel, ConfigDict
from typing import Optional

class Article(BaseModel):
    id: int
    title: str
    source_name: Optional[str] = None
    url: str
    published_at: str
    topic: str
    generic_news: bool
    
    model_config = ConfigDict(from_attributes=True)