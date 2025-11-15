# How It Works

## The Big Picture

QuietlyStated has 4 main parts that work together:

1. **Ingestion** - Collects data from the internet
2. **Storage** - Saves everything in MongoDB
3. **Processing** - Finds important information
4. **Output** - Gives you reports and insights

Let's break each part down:

---

## Part 1: Ingestion (Collecting Data)

**What it does:** Goes out and gets data from different places.

### Google Trends (`sources/google_trends.py`)

**How it works:**
1. Reads your keywords from `config/keywords.json`
2. Connects to Google Trends (no API key needed - it's free!)
3. For each keyword, gets:
   - Search interest over time (how popular it is)
   - Related queries (what else people search for)
4. Saves everything to MongoDB in the `raw_trends` collection

**What you need:** Nothing! Just configure keywords.

**Rate limits:** Google may slow you down if you request too much. The code waits 1 second between requests.

### Google Alerts (`sources/google_alerts.py`)

**How it works:**
1. Reads RSS feed URLs from `config/feeds.json`
2. For each Google Alert feed:
   - Fetches the RSS feed (like reading a newspaper)
   - Gets each news item (title, snippet, link, date)
   - Saves to MongoDB in the `raw_alerts` collection

**What you need:** 
- Set up Google Alerts at [google.com/alerts](https://www.google.com/alerts)
- Choose "RSS feed" delivery
- Copy the RSS URL to `config/feeds.json`

**No API key needed** - RSS feeds are public.

### Blog Scraping (`sources/blogs.py`)

**How it works:**
1. Reads blog RSS feeds from `config/feeds.json`
2. For each blog:
   - Fetches the RSS feed (list of recent posts)
   - For each post:
     - Gets the full article text (visits the webpage)
     - Extracts the main content (removes ads, menus, etc.)
     - Saves to MongoDB in the `raw_articles` collection

**What you need:** Just RSS feed URLs in `config/feeds.json`

**How it extracts text:** Uses BeautifulSoup to find the main article content, ignoring navigation and ads.

---

## Part 2: Storage (MongoDB)

**What it does:** Keeps all your data organized.

### Collections (Like Folders)

1. **`sources`** - Metadata about where data came from
2. **`raw_trends`** - Google Trends data
3. **`raw_alerts`** - Google Alerts news items
4. **`raw_articles`** - Blog articles
5. **`processed_signals`** - Extracted statistics and metrics
6. **`insights`** - Final summaries and recommendations

**Why separate?** 
- Raw data = what you collected (never changes)
- Processed data = what you extracted (can be regenerated)
- Insights = what you learned (can be improved)

---

## Part 3: Processing (Finding Important Stuff)

**What it does:** Reads the raw data and finds what matters.

### Statistics Extraction (`processing/stats_extractor.py`)

**How it works:**
- Uses patterns (regex) to find numbers in text:
  - Percentages: "sales up 15%"
  - Changes: "from 10% to 20%"
  - Comparisons: "down by 5%"
- Extracts the sentence containing the number
- Returns "candidates" - possible important statistics

**Example:**
- Text: "Sales increased by 15% this quarter."
- Finds: "15%" in context "Sales increased by 15% this quarter."

### Topic Tagging (`processing/topic_tagger.py`)

**How it works:**
- Loads topics from `config/topics.json`
- Counts how many times each topic's keywords appear in text
- Assigns the most common topic

**Example:**
- Text mentions "email", "newsletter", "klaviyo" 5 times
- Text mentions "tiktok shop" 2 times
- Result: Topic = "email_sms"

### Signal Extraction (`processing/llm_signals.py`)

**How it works:**
1. Takes statistics candidates from `stats_extractor`
2. For each candidate:
   - Extracts the number (e.g., 15%)
   - Tries to identify what it's about (entity: "sales", metric: "growth")
   - Creates a structured signal

**Current version:** Uses simple rules (heuristics)
- Looks for keywords like "sales", "revenue", "growth"
- Extracts entity from text before the metric

**Future version:** Will use AI (LLM) for better extraction
- Understands context better
- Identifies entities and metrics more accurately
- **TODO:** Replace with OpenAI/Anthropic API calls

### Insight Generation (`processing/llm_insights.py`)

**How it works:**
1. Groups signals by topic
2. For each topic with enough signals:
   - Creates a title
   - Writes a summary
   - Suggests implications
   - Links to source signals

**Current version:** Uses simple templates
- "Found X signals related to Y"
- Basic aggregation of numbers

**Future version:** Will use AI (LLM) for better insights
- More natural language
- Better connections between signals
- Actionable recommendations
- **TODO:** Replace with OpenAI/Anthropic API calls

---

## Part 4: Output (Getting Your Results)

**What it does:** Gives you the information in useful ways.

### CLI Commands (`cli.py`)

**Available commands:**
- `fetch-trends` - Run Google Trends collection
- `fetch-alerts` - Run Google Alerts collection
- `fetch-articles` - Run blog scraping
- `enrich-signals` - Process raw data into signals
- `aggregate-insights` - Generate insights from signals
- `weekly-report` - Print a summary report

**How to use:** Just run `python cli.py [command]`

### API (`api/main.py`)

**What it is:** A web server that answers questions about your data.

**Endpoints:**
- `GET /insights` - List insights (filter by topic, date, limit)
- `GET /insights/{id}` - Get one insight
- `GET /signals` - List signals (filter by topic, date, limit)
- `GET /signals/{id}` - Get one signal
- `GET /sources/articles` - List articles
- `GET /sources/articles/{id}` - Get article with signals/insights

**How to start:**
```bash
uvicorn api.main:app --reload
```

Then visit: `http://localhost:8000/docs` for interactive API docs.

### Analytics (`analytics/trends_reports.py`)

**What it does:** Compares time periods to find what changed.

**Functions:**
- `get_top_terms()` - Top search terms by interest and growth
- `get_top_topics()` - Top topics by count and growth
- `get_notable_stats()` - Statistics with big changes

**Used by:** The `weekly-report` CLI command

---

## The Flow (Step by Step)

**Daily workflow:**

1. **Morning:** Run ingestion jobs
   ```bash
   python cli.py fetch-trends
   python cli.py fetch-alerts
   python cli.py fetch-articles
   ```

2. **Afternoon:** Process the data
   ```bash
   python cli.py enrich-signals
   python cli.py aggregate-insights
   ```

3. **Before meeting:** Get report
   ```bash
   python cli.py weekly-report
   ```

**What happens behind the scenes:**

1. Ingestion → Raw data in MongoDB
2. Processing → Signals extracted
3. Aggregation → Insights generated
4. Analytics → Reports created

**You can automate this** with cron (see `04-usage.md`)

---

## Data Flow Diagram

```
Internet Sources
    ↓
[Ingestion Layer]
    ↓
MongoDB (Raw Data)
    ↓
[Processing Layer]
    ↓
MongoDB (Signals & Insights)
    ↓
[API / CLI]
    ↓
You!
```

---

## Key Concepts

**Upsert:** Update if exists, insert if new. Prevents duplicates.

**Chunking:** Breaking large lists into smaller pieces (Google Trends limit: 5 terms).

**Rate Limiting:** Waiting between requests to avoid being blocked.

**Stub:** Placeholder code that works but will be improved later (LLM integration).

**Collection:** MongoDB's word for a table/database of documents.

