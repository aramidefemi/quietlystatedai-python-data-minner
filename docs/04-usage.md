# Usage Guide

## Quick Start

Once everything is set up, here's how to use QuietlyStated day-to-day.

---

## Daily Workflow

### Step 1: Collect Data

Run these commands to fetch new data:

```bash
# Get Google Trends data
python cli.py fetch-trends

# Get Google Alerts
python cli.py fetch-alerts

# Get blog articles
python cli.py fetch-articles
```

**How long does this take?**
- Trends: 1-2 minutes (depends on how many keywords)
- Alerts: 10-30 seconds (depends on how many feeds)
- Articles: 1-5 minutes (depends on how many blogs)

**When should I run these?**
- Once per day is usually enough
- Or before important meetings
- You can automate with cron (see below)

### Step 2: Process Data

After collecting, extract signals and generate insights:

```bash
# Extract statistics from articles/alerts
python cli.py enrich-signals --days 7

# Generate insights from signals
python cli.py aggregate-insights --days 7
```

**What does `--days 7` mean?**
- Only process data from the last 7 days
- Change to `--days 30` for a month
- Default is 7 days

**How long does this take?**
- enrich-signals: 30 seconds - 2 minutes
- aggregate-insights: 10-30 seconds

### Step 3: Get Your Report

```bash
python cli.py weekly-report
```

**What you'll see:**
- Top search terms (by popularity and growth)
- Top topics (by signal count and growth)
- Notable statistics (big changes)

**Example output:**
```
============================================================
QUIETLYSTATED WEEKLY REPORT
============================================================

📈 TOP SEARCH TERMS
------------------------------------------------------------

Top by Average Interest:
  1. press on nails: 65.3 (was 58.2)
  2. cargo pants: 72.1 (was 70.5)
  3. same day delivery: 45.8 (was 42.1)

Top by Growth:
  1. press on nails: +12.2%
  2. same day delivery: +8.8%
  3. cargo pants: +2.3%

🏷️  TOP TOPICS
------------------------------------------------------------

Top by Signal Count:
  1. tiktok_shop: 15 signals
  2. email_sms: 12 signals
  3. retention: 8 signals

📊 NOTABLE STATISTICS
------------------------------------------------------------

  1. tiktok_shop - sales
     +23.5% - Gen Z consumers
     TikTok Shop sales increased 23.5% among Gen Z consumers...
```

---

## Individual Commands Explained

### Fetch Commands

**`fetch-trends`**
- What: Gets Google Trends data
- Needs: `config/keywords.json` configured
- Output: Data in `raw_trends` collection
- Frequency: Daily

**`fetch-alerts`**
- What: Gets Google Alerts via RSS
- Needs: Google Alert RSS URLs in `config/feeds.json`
- Output: Data in `raw_alerts` collection
- Frequency: Daily

**`fetch-articles`**
- What: Scrapes blog articles
- Needs: Blog RSS URLs in `config/feeds.json`
- Output: Data in `raw_articles` collection
- Frequency: Daily

### Processing Commands

**`enrich-signals`**
- What: Extracts statistics from articles/alerts
- Options: `--days N` (default: 7)
- Output: Data in `processed_signals` collection
- Frequency: After fetching new data

**`aggregate-insights`**
- What: Creates insights from signals
- Options: `--days N` (default: 7)
- Output: Data in `insights` collection
- Frequency: After enriching signals

### Report Commands

**`weekly-report`**
- What: Prints a text report to console
- Shows: Trends, topics, notable stats
- Frequency: Whenever you need it

---

## Using the API

### Start the Server

```bash
uvicorn api.main:app --reload
```

The server runs at: `http://localhost:8000`

### View API Documentation

Open in browser: `http://localhost:8000/docs`

You'll see an interactive page where you can:
- See all endpoints
- Test them directly
- See example responses

### Common API Calls

**Get recent insights:**
```
GET http://localhost:8000/insights?limit=10
```

**Get insights for a topic:**
```
GET http://localhost:8000/insights?topic=tiktok_shop&limit=5
```

**Get insights since a date:**
```
GET http://localhost:8000/insights?since=2024-01-01T00:00:00Z
```

**Get signals:**
```
GET http://localhost:8000/signals?topic=email_sms&limit=20
```

**Get an article with its signals:**
```
GET http://localhost:8000/sources/articles/{article_id}
```

### Using from Code

**Python example:**
```python
import requests

response = requests.get("http://localhost:8000/insights?limit=5")
insights = response.json()

for insight in insights:
    print(insight["title"])
    print(insight["summary"])
```

**cURL example:**
```bash
curl "http://localhost:8000/insights?limit=5"
```

---

## Automation (Scheduling Jobs)

### Using Cron (Mac/Linux)

**What is cron?** A scheduler that runs commands at set times.

**Edit your crontab:**
```bash
crontab -e
```

**Add these lines:**
```bash
# Fetch data every morning at 9 AM
0 9 * * * cd /Users/mac/Desktop/projects/quietlystated && python cli.py fetch-trends
0 9 * * * cd /Users/mac/Desktop/projects/quietlystated && python cli.py fetch-alerts
0 9 * * * cd /Users/mac/Desktop/projects/quietlystated && python cli.py fetch-articles

# Process data at 10 AM
0 10 * * * cd /Users/mac/Desktop/projects/quietlystated && python cli.py enrich-signals
0 10 * * * cd /Users/mac/Desktop/projects/quietlystated && python cli.py aggregate-insights
```

**Cron format:** `minute hour day month weekday`

**Examples:**
- `0 9 * * *` = Every day at 9:00 AM
- `0 */6 * * *` = Every 6 hours
- `0 9 * * 1` = Every Monday at 9:00 AM

### Using Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (daily, weekly, etc.)
4. Set action: Start a program
5. Program: `python`
6. Arguments: `cli.py fetch-trends`
7. Start in: Your project folder path

### Using Job Scripts Directly

You can also run the job scripts directly:

```bash
python jobs/ingest_trends.py
python jobs/ingest_alerts.py
python jobs/scrape_blogs.py
python jobs/extract_signals.py
python jobs/aggregate_insights.py
```

These are the same as CLI commands but useful for cron.

---

## Troubleshooting

### "No data in report"

**Possible causes:**
1. Haven't fetched data yet → Run fetch commands
2. Haven't processed data → Run enrich-signals
3. Time window too narrow → Check date ranges

**Fix:**
```bash
# Fetch everything
python cli.py fetch-trends
python cli.py fetch-alerts
python cli.py fetch-articles

# Process it
python cli.py enrich-signals --days 30
python cli.py aggregate-insights --days 30

# Try report again
python cli.py weekly-report
```

### "MongoDB connection error"

**Check:**
1. Is MongoDB running? → `mongosh`
2. Is `.env` file correct?
3. Is MongoDB URI right?

**Fix:**
```bash
# Start MongoDB (Mac/Linux)
brew services start mongodb-community

# Or (Linux)
sudo systemctl start mongodb
```

### "No signals extracted"

**Possible causes:**
1. Articles don't contain statistics
2. Stats extractor patterns don't match
3. Text extraction failed

**Check:**
- Look at raw articles in MongoDB
- Check if they have text content
- Verify articles contain numbers/percentages

### "API not responding"

**Check:**
1. Is server running? → Look for "Uvicorn running on..."
2. Is port 8000 free?
3. Check for errors in terminal

**Fix:**
```bash
# Kill existing server
pkill -f uvicorn

# Start fresh
uvicorn api.main:app --reload
```

---

## Best Practices

1. **Fetch regularly** - At least once per day
2. **Process after fetching** - Don't skip enrich-signals
3. **Check your config** - Make sure keywords/feeds are current
4. **Monitor storage** - MongoDB can grow large over time
5. **Backup MongoDB** - Use `mongodump` regularly

---

## Next Steps

- Read `05-advanced.md` for customization
- Check `06-troubleshooting.md` for common issues
- Review `03-how-it-works.md` to understand internals

