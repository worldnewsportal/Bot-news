import urllib.parse
from models.article import Article
from models.summary import AISummary
from utils.text_sanitizer import sanitize_html

# 1️⃣ ضع رابط Adsterra المباشر الخاص بك هنا
ADSTERRA_DIRECT_LINK = "https://www.effectivecpmnetwork.com/awzbbi353?key=16d6ee5ad7058950ed0a6c70dec83b95"

# 2️⃣ ضع مفتاح ShrinkMe API الخاص بك هنا (من موقع ShrinkMe -> قسم Tools -> Developer API)
SHRINKME_API_KEY = "2801f08b278886e58899df2fef0dad30bdbe1d8d"

def get_shrinkme_url(original_url: str) -> str:
    """تحويل الرابط فورياً إلى رابط ShrinkMe ربحي عبر ميزة Quick Link المضمونة"""
    if not SHRINKME_API_KEY or SHRINKME_API_KEY in ["2801f08b278886e58899df2fef0dad30bdbe1d8d", "2801f08b278886e58899df2fef0dad30bdbe1d8d"]:
        return original_url
    
    # صيغة Quick Link الرسمية لموقع ShrinkMe
    encoded_url = urllib.parse.quote(original_url)
    return f"https://shrinkme.io/st?api={SHRINKME_API_KEY}&url={encoded_url}"

class TelegramFormatter:
    @classmethod
    def format_message(cls, article: Article, summary: AISummary) -> str:
        pub_date_str = article.pub_date.strftime("%Y-%m-%d %H:%M UTC")
        
        # تحويل رابط الخبر إلى رابط ShrinkMe المربح
        final_article_url = get_shrinkme_url(article.url)

        # تنسيق النقاط الرئيسية باللغتين
        kp_list = []
        for en, ar in zip(summary.key_points_en, summary.key_points_ar):
            kp_list.append(f"• {sanitize_html(en)}\n  🔹 {sanitize_html(ar)}")
        key_points_str = "\n".join(kp_list)

        keywords_str = " ".join([f"#{kw.replace(' ', '')}" for kw in summary.keywords])

        # سطر الإعلان المباشر لـ Adsterra
        ad_banner = f"🎁 <a href='{ADSTERRA_DIRECT_LINK}'>شاهد أهم عروض وتقنيات اليوم المميزة</a>"

        msg = (
            f"📰 <b>{sanitize_html(summary.title_en)}</b>\n"
            f"🇸🇦 <b>{sanitize_html(summary.title_ar)}</b>\n\n"
            f"🌍 <b>Region / المنطقة:</b> {sanitize_html(summary.country)}\n"
            f"🏷 <b>Category / التصنيف:</b> {sanitize_html(summary.category_en)} | {sanitize_html(summary.category_ar)}\n"
            f"📰 <b>Source / المصدر:</b> {sanitize_html(article.source)}\n"
            f"📅 <b>Date / التاريخ:</b> {pub_date_str}\n\n"
            f"🇬🇧 <b>Summary (English):</b>\n{sanitize_html(summary.summary_en)}\n\n"
            f"🇸🇦 <b>الملخص (بالعربية):</b>\n{sanitize_html(summary.summary_ar)}\n\n"
            f"⭐ <b>Key Points / النقاط الرئيسية:</b>\n{key_points_str}\n\n"
            f"❗ <b>Why It Matters / أهمية الخبر:</b>\n"
            f"• {sanitize_html(summary.why_it_matters_en)}\n"
            f"• {sanitize_html(summary.why_it_matters_ar)}\n\n"
            f"{keywords_str}\n\n"
            f"{ad_banner}\n\n"
            f"🔗 <a href='{final_article_url}'>Read Full Article / اقرأ المقال كاملاً على {sanitize_html(article.source)}</a>"
        )
        return msg
