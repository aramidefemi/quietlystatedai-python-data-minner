# Quick Reference Card

## 🚀 Essential Commands

```bash
# Fetch data
python cli.py fetch-trends
python cli.py fetch-alerts
python cli.py fetch-articles

# Process data
python cli.py enrich-signals --days 7
python cli.py aggregate-insights --days 7

# Get report
python cli.py weekly-report

# Start API
uvicorn api.main:app --reload
```

## 📁 Configuration Files

| File | What It Does | Where to Edit |
|------|--------------|---------------|
| `config/keywords.json` | Google Trends search terms | Add your keywords here |
| `config/feeds.json` | Blog RSS feeds & Google Alerts | Add RSS URLs here |
| `config/topics.json` | Topic categories | Add topic keywords here |
| `.env` | Database connection | MongoDB URI here |

## 🔑 API Keys Needed?

**No API keys required for basic use!**

Optional (for AI features):
- OpenAI API key → Add to `.env` as `OPENAI_API_KEY`
- Anthropic API key → Add to `.env` as `ANTHROPIC_API_KEY`

## 📍 Where to Put Things

### Google Trends Keywords
**File:** `config/keywords.json`
```json
{
  "regions": ["GB"],
  "timeframe": "now 7-d",
  "groups": [
    {
      "name": "your_category",
      "terms": ["keyword 1", "keyword 2"]
    }
  ]
}
```

### Blog RSS Feeds
**File:** `config/feeds.json`
```json
[
  {
    "source": "blog_name",
    "url": "https://blog.com/rss",
    "type": "rss"
  }
]
```

### Google Alerts
1. Create alert at [google.com/alerts](https://www.google.com/alerts)
2. Choose "RSS feed" delivery
3. Copy RSS URL
4. Add to `config/feeds.json`:
```json
{
  "source": "google_alerts_topic_name",
  "url": "https://www.google.com/alerts/feeds/...",
  "type": "rss",
  "keyword": "your search term"
}
```

### Topics
**File:** `config/topics.json`
```json
{
  "topic_name": ["keyword1", "keyword2", "keyword3"]
}
```

## 🗄️ MongoDB Collections

- `sources` - Where data came from
- `raw_trends` - Google Trends data
- `raw_alerts` - Google Alerts
- `raw_articles` - Blog articles
- `processed_signals` - Extracted statistics
- `insights` - Final summaries

## 🔄 Daily Workflow

1. **Morning (9 AM):** Fetch data
   ```bash
   python cli.py fetch-trends
   python cli.py fetch-alerts
   python cli.py fetch-articles
   ```

2. **Afternoon (10 AM):** Process data
   ```bash
   python cli.py enrich-signals
   python cli.py aggregate-insights
   ```

3. **Before meeting:** Get report
   ```bash
   python cli.py weekly-report
   ```

## 🌐 API Endpoints

Base URL: `http://localhost:8000`

- `GET /insights` - List insights
- `GET /insights?topic=tiktok_shop` - Filter by topic
- `GET /signals` - List signals
- `GET /sources/articles` - List articles
- `GET /docs` - Interactive API docs

## ⚙️ Environment Variables

**File:** `.env`

```
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB_NAME=quietlystated
OPENAI_API_KEY=optional
ANTHROPIC_API_KEY=optional
```

## 🐛 Quick Fixes

**"Python not found"** → Use `python3` instead

**"MongoDB connection failed"** → Start MongoDB: `brew services start mongodb-community`

**"No data in report"** → Run fetch commands first, then enrich-signals

**"Module not found"** → Run `pip install -r requirements.txt`

**"Port 8000 in use"** → Use different port: `uvicorn api.main:app --port 8001`

## 📅 Cron Schedule Example

```bash
# Edit crontab
crontab -e

# Add these lines (runs daily at 9 AM)
0 9 * * * cd /path/to/quietlystated && python cli.py fetch-trends
0 9 * * * cd /path/to/quietlystated && python cli.py fetch-alerts
0 9 * * * cd /path/to/quietlystated && python cli.py fetch-articles
0 10 * * * cd /path/to/quietlystated && python cli.py enrich-signals
0 10 * * * cd /path/to/quietlystated && python cli.py aggregate-insights
```

## 📚 Documentation

- **Start here:** `docs/00-overview.md`
- **Setup:** `docs/01-setup.md`
- **Configuration:** `docs/02-configuration.md`
- **How it works:** `docs/03-how-it-works.md`
- **Usage:** `docs/04-usage.md`
- **Advanced:** `docs/05-advanced.md`
- **Troubleshooting:** `docs/06-troubleshooting.md`

## ✅ Checklist

- [ ] Python installed
- [ ] MongoDB installed and running
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file configured
- [ ] `config/keywords.json` has your keywords
- [ ] `config/feeds.json` has your RSS feeds
- [ ] Tested with `python cli.py weekly-report`

---

**Need help?** Check `docs/06-troubleshooting.md`

