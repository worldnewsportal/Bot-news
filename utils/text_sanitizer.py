import html
import re

def sanitize_html(text: str) -> str:
    if not text:
        return ""
    # Strip dangerous HTML tags but keep safe basic markup if needed
    clean = re.sub(r'<[^>]+>', '', text)
    clean = html.escape(clean)
    return clean.strip()

def clean_url(url: str) -> str:
    if not url:
        return ""
    # Strip tracking query params
    url = re.sub(r'utm_[^&]+&?', '', url)
    url = re.sub(r'\?&?$', '', url)
    return url.strip()
