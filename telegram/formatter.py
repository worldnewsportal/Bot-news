from models.article import Article
from models.summary import AISummary
from utils.text_sanitizer import sanitize_html

class TelegramFormatter:
    @staticmethod
    def format_message(article: Article, summary: AISummary) -> str:
        pub_date_str = article.pub_date.strftime("%Y-%m-%d %H:%M UTC")
        
        key_points_str = "\n".join([f"• {sanitize_html(kp)}" for kp in summary.key_points])
        keywords_str = " ".join([f"#{kw.replace(' ', '')}" for kw in summary.keywords])

        msg = (
            f"📰 <b>{sanitize_html(summary.title)}</b>\n\n"
            f"🌍 <b>Region:</b> {sanitize_html(summary.country)}\n"
            f"🏷 <b>Category:</b> {sanitize_html(summary.category)}\n"
            f"📰 <b>Source:</b> {sanitize_html(article.source)}\n"
            f"📅 <b>Published:</b> {pub_date_str}\n\n"
            f"📝 <b>Summary:</b>\n{sanitize_html(summary.summary)}\n\n"
            f"⭐ <b>Key Points:</b>\n{key_points_str}\n\n"
            f"❗ <b>Why This Matters:</b>\n{sanitize_html(summary.why_it_matters)}\n\n"
            f"{keywords_str}\n\n"
            f"🔗 <a href='{article.url}'>Read Full Article on {sanitize_html(article.source)}</a>"
        )
        return msg
