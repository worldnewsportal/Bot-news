# 🚀 Production-Ready AI Telegram News Bot

An enterprise-grade, fully automated, serverless Telegram News Bot running 100% on **GitHub Actions**. It collects 800+ articles every 10 hours, deduplicates items, ranks news by global impact, synthesizes summaries using multi-provider AI fallback (Gemini & OpenRouter), and posts structured updates with images to Telegram.

---

## 🌟 Key Features

- **Zero-Server Maintenance**: Runs completely inside GitHub Actions.
- **Smart AI Model Router**: Priority fallback: `Gemini 1.5 Flash` ➔ `Gemma 4` ➔ `OpenRouter Dynamic Free Models`. Never fails due to quota limits.
- **Deduplication Engine**: Jaccard index similarity & canonical URL hashing.
- **Top 100 Ranking**: Dynamic scoring based on source credibility, recency decay, breaking news keywords, and content depth.
- **Persistent Git Cache**: Automatically commits `data/published_cache.json` back to GitHub so news items are never re-posted across runs.
- **Telegram Safety**: HTML tag sanitization and dynamic delay throttles to prevent Telegram HTTP 429 rate limits.

---

## 🔑 Required Environment Secrets

Configure these in your GitHub Repository under **Settings -> Secrets and variables -> Actions**:

| Secret Key | Required? | Description |
| :--- | :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | **Yes** | Telegram Bot API Token from @BotFather |
| `TELEGRAM_CHAT_ID` | **Yes** | Target Channel or Group Chat ID (e.g. `@mychannel` or `-100123456789`) |
| `GEMINI_API_KEY` | **Recommended** | Primary AI Summarizer API key from Google AI Studio |
| `OPENROUTER_API_KEY` | **Recommended** | Secondary AI Summarizer API key for OpenRouter models |
| `NEWSAPI_KEY` | Optional | Optional key for NewsAPI integration |

---

## 🚀 Deployment Instructions

1. **Fork or Clone this repository**:
   ```bash
   git clone https://github.com/your-username/telegram-news-bot.git
   cd telegram-news-bot
