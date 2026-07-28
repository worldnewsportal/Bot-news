from pydantic import BaseModel, Field
from typing import List

class AISummary(BaseModel):
    title: str = Field(description="Professional journalistic headline")
    summary: str = Field(description="Accurate 150-300 word summary")
    key_points: List[str] = Field(description="3 to 5 key takeaways")
    why_it_matters: str = Field(description="Context and global significance")
    category: str = Field(description="Assigned category")
    country: str = Field(description="Primary country or region affected")
    keywords: List[str] = Field(description="3 to 5 relevant tags")
