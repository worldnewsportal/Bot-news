from models.article import Article
from models.summary import AISummary
from utils.text_sanitizer import sanitize_html

class TelegramFormatter:
    @staticmethod
    def format_message(article: Article, summary: AISummary) -> str:
        pub_date_str = article.pub_date.strftime("%Y-%m-%d %H:%M UTC")
        
        # تنسيق النقاط الرئيسية باللغتين
        kp_list = []
        for en, ar in zip(summary.key_points_en, summary.key_points_ar):
            kp_list.append(f"• {sanitize_html(en)}\n  🔹 {sanitize_html(ar)}")
        key_points_str = "\n".join(kp_list)

        keywords_str = " ".join([f"#{kw.replace(' ', '')}" for kw in summary.keywords])

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
            f"🔗 <a href='{article.url}'>Read Full Article / اقرأ المقال كاملاً على {sanitize_html(article.source)}</a>"
        )
        return msg
