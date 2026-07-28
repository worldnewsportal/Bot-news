from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Article(BaseModel):
    id: str
    title: str
    content: str
    description: str
    url: str
    canonical_url: str
    image_url: Optional[str] = None
    pub_date: datetime
    author: str = "Unknown"
    source: str
    source_credibility: float = 1.0
    language: str = "en"
    score: float = 0.0
