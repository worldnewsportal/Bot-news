from pydantic import BaseModel, Field
from typing import List

class AISummary(BaseModel):
    title_en: str = Field(description="Professional English headline")
    title_ar: str = Field(description="عنوان خبري احترافي باللغة العربية")
    summary_en: str = Field(description="Detailed 150-250 word summary in English")
    summary_ar: str = Field(description="ملخص تفصيلي وافي باللغة العربية (150-250 كلمة)")
    key_points_en: List[str] = Field(description="3 to 5 detailed key points in English")
    key_points_ar: List[str] = Field(description="3 إلى 5 نقاط تفصيلية بالعربية")
    why_it_matters_en: str = Field(description="Why this matters in English")
    why_it_matters_ar: str = Field(description="أهمية الخبر وسياقه باللغة العربية")
    category_en: str = Field(description="Category in English")
    category_ar: str = Field(description="التصنيف باللغة العربية")
    country: str = Field(description="Primary country or region affected")
    keywords: List[str] = Field(description="3 to 5 relevant hashtags")
