# Troubleshooting Guide

## Common Problems and Solutions

### Problem: "Python not found" or "python: command not found"

**What it means:** Python isn't installed or not in your PATH.

**Solutions:**
1. **Check if Python is installed:**
   ```bash
   python3 --version
   ```
   If this works, use `python3` instead of `python`.

2. **Install Python:**
   - Mac: Download from [python.org](https://www.python.org/downloads/)
   - Windows: Download from [python.org](https://www.python.org/downloads/)
   - Linux: `sudo apt install python3`

3. **Add to PATH:**
   - Mac/Linux: Usually automatic
   - Windows: Check "Add Python to PATH" during installation

---

### Problem: "MongoDB connection failed"

**What it means:** Can't connect to MongoDB database.

**Solutions:**

1. **Check if MongoDB is running:**
   ```bash
   mongosh
   ```
   If this fails, MongoDB isn't running.

2. **Start MongoDB:**
   - Mac: `brew services start mongodb-community`
   - Linux: `sudo systemctl start mongodb`
   - Windows: Check Services app, start MongoDB service

3. **Check your `.env` file:**
   ```
   MONGODB_URI=mongodb://localhost:27017/
   ```
   Make sure this matches where MongoDB is running.

4. **Check MongoDB is listening:**
   ```bash
   # Mac/Linux
   lsof -i :27017
   
   # Should show mongod process
   ```

---

### Problem: "Module not found" errors

**What it means:** A Python package isn't installed.

**Solutions:**

1. **Reinstall requirements:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Use pip3 if needed:**
   ```bash
   pip3 install -r requirements.txt
   ```

3. **Check you're in the right directory:**
   ```bash
   pwd
   # Should show: /Users/mac/Desktop/projects/quietlystated
   ```

4. **Use virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Mac/Linux
   # or
   venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

---

### Problem: "No data in weekly report"

**What it means:** Either no data was collected, or it wasn't processed.

**Solutions:**

1. **Check if data exists:**
   ```bash
   mongosh
   use quietlystated
   db.raw_trends.countDocuments()
   db.raw_articles.countDocuments()
   ```

2. **If counts are 0, fetch data:**
   ```bash
   python cli.py fetch-trends
   python cli.py fetch-alerts
   python cli.py fetch-articles
   ```

3. **If data exists but no signals:**
   ```bash
   python cli.py enrich-signals --days 30
   ```

4. **If signals exist but no insights:**
   ```bash
   python cli.py aggregate-insights --days 30
   ```

5. **Check date ranges:**
   - Report compares last 7 days vs previous 7 days
   - If you only have 3 days of data, it might be empty
   - Try `--days 30` to process more data

---

### Problem: "Google Trends rate limit" or "Too many requests"

**What it means:** Google is blocking too many requests.

**Solutions:**

1. **Wait and retry:**
   - Google may block for 1-2 hours
   - Try again later

2. **Reduce keywords:**
   - Edit `config/keywords.json`
   - Remove some terms temporarily

3. **Add delays:**
   - The code already waits 1 second between requests
   - You can increase this in `sources/google_trends.py`:
     ```python
     time.sleep(2)  # Change from 1 to 2 seconds
     ```

4. **Use VPN or different IP:**
   - Sometimes IP-based blocking
   - Try from different network

---

### Problem: "RSS feed not working" or "Feed parser error"

**What it means:** Can't read an RSS feed.

**Solutions:**

1. **Check the URL:**
   - Open the URL in a browser
   - Should see XML or RSS content
   - If you see HTML, it's not an RSS feed

2. **Find correct RSS URL:**
   - Look for RSS icon on blog
   - Try `/rss`, `/feed`, `/atom.xml`
   - Check blog's documentation

3. **Test the feed:**
   ```bash
   curl "https://blogname.com/rss"
   ```
   Should return XML, not HTML error page

4. **Check if feed requires authentication:**
   - Some feeds need login
   - These won't work (use public feeds only)

---

### Problem: "Article text extraction failed" or empty articles

**What it means:** Can't get full article text from webpage.

**Solutions:**

1. **Check if article has text in MongoDB:**
   ```bash
   mongosh
   use quietlystated
   db.raw_articles.findOne({}, {text: 1})
   ```

2. **If text is empty:**
   - The website might block scrapers
   - RSS feed might not have full content
   - Website structure might be unusual

3. **Workarounds:**
   - Some blogs provide full content in RSS (better)
   - Try different RSS feed if available
   - Accept that some articles will have limited text

4. **Check website robots.txt:**
   - Some sites block scraping
   - Respect their rules

---

### Problem: "No signals extracted from articles"

**What it means:** Statistics extraction found nothing.

**Solutions:**

1. **Check if articles contain numbers:**
   - Look at raw articles
   - Do they mention percentages, statistics?
   - Some articles are just opinion pieces

2. **Check extraction patterns:**
   - Current patterns look for: `15%`, `from X to Y`, `up by X%`
   - If articles use different formats, they won't match

3. **Test extraction manually:**
   ```python
   from processing.stats_extractor import extract_stat_candidates
   
   text = "Sales increased by 15% this quarter."
   candidates = extract_stat_candidates(text)
   print(candidates)
   ```

4. **Add custom patterns:**
   - Edit `processing/stats_extractor.py`
   - Add regex patterns for your use case

---

### Problem: "API server won't start" or "Port already in use"

**What it means:** Port 8000 is already taken.

**Solutions:**

1. **Find what's using port 8000:**
   ```bash
   # Mac/Linux
   lsof -i :8000
   
   # Windows
   netstat -ano | findstr :8000
   ```

2. **Kill the process:**
   ```bash
   # Mac/Linux
   kill -9 <PID>
   
   # Windows
   taskkill /PID <PID> /F
   ```

3. **Use different port:**
   ```bash
   uvicorn api.main:app --port 8001
   ```

---

### Problem: "Cron job not running"

**What it means:** Scheduled tasks aren't executing.

**Solutions:**

1. **Check cron is running:**
   ```bash
   # Mac/Linux
   sudo systemctl status cron
   ```

2. **Check your crontab:**
   ```bash
   crontab -l
   ```

3. **Check paths in cron:**
   - Cron doesn't use your PATH
   - Use full paths:
     ```bash
     0 9 * * * /usr/bin/python3 /full/path/to/cli.py fetch-trends
     ```

4. **Check cron logs:**
   ```bash
   # Mac
   grep CRON /var/log/system.log
   
   # Linux
   grep CRON /var/log/syslog
   ```

5. **Test command manually:**
   - Run the exact command from crontab
   - Make sure it works outside cron first

---

### Problem: "MongoDB running out of space"

**What it means:** Database is getting too large.

**Solutions:**

1. **Check database size:**
   ```bash
   mongosh
   use quietlystated
   db.stats()
   ```

2. **Delete old data:**
   ```python
   from datetime import datetime, timedelta
   from db.mongo_client import get_db
   
   db = get_db()
   cutoff = datetime.utcnow() - timedelta(days=90)
   
   # Delete old raw data (keep processed)
   db.raw_trends.delete_many({"pulled_at": {"$lt": cutoff}})
   db.raw_articles.delete_many({"fetched_at": {"$lt": cutoff}})
   ```

3. **Set up automatic cleanup:**
   - Add to cron: Run cleanup script monthly

---

### Problem: "LLM integration not working"

**What it means:** AI features aren't enabled or configured.

**Solutions:**

1. **Check if API key is set:**
   ```bash
   cat .env | grep API_KEY
   ```

2. **Verify API key is valid:**
   - Test with simple API call
   - Check account has credits

3. **Check code is using LLM:**
   - Current version uses stubs
   - Need to implement LLM calls (see `05-advanced.md`)

4. **Check error messages:**
   - API might be rate limited
   - Check API status page
   - Verify billing is set up

---

## Getting More Help

### Check Logs

**Application logs:**
- Look for `.log` files in project directory
- Check terminal output when running commands

**MongoDB logs:**
- Mac: `/usr/local/var/log/mongodb/mongo.log`
- Linux: `/var/log/mongodb/mongod.log`
- Windows: Check MongoDB installation directory

### Debug Mode

**Run with verbose output:**
```bash
python -v cli.py fetch-trends
```

**Check MongoDB queries:**
```python
from db.mongo_client import get_db

db = get_db()
# Enable logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Components

**Test MongoDB connection:**
```python
from db.mongo_client import get_db
db = get_db()
db.command("ping")  # Should return {"ok": 1}
```

**Test RSS feed:**
```python
import feedparser
feed = feedparser.parse("https://blogname.com/rss")
print(feed.entries[0].title)
```

**Test Google Trends:**
```python
from pytrends.request import TrendReq
pytrends = TrendReq(hl="en-GB", tz=360)
pytrends.build_payload(["test keyword"], geo="GB", timeframe="now 7-d")
print(pytrends.interest_over_time())
```

---

## Still Stuck?

1. **Review the relevant documentation:**
   - Setup issues → `01-setup.md`
   - Configuration issues → `02-configuration.md`
   - Usage issues → `04-usage.md`

2. **Check the code:**
   - Look at error messages carefully
   - Check file paths are correct
   - Verify environment variables

3. **Start fresh:**
   - Sometimes a clean install helps
   - Delete MongoDB database and re-import
   - Reinstall Python packages

4. **Check system requirements:**
   - Python 3.8+
   - MongoDB 4.4+
   - Enough disk space
   - Internet connection

