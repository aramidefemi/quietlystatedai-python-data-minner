# Advanced Topics

## Customizing LLM Integration

### Current State

The system currently uses **stub implementations** for LLM-based extraction:
- Simple regex and keyword matching
- Basic template generation
- Works but not as smart as AI

### Adding OpenAI

**File to edit:** `processing/llm_signals.py`

**Find this function:**
```python
def extract_structured_signals(text: str, source_id: Any, origin_type: str, topic: str) -> List[ProcessedSignal]:
```

**Replace with:**
```python
import openai

def extract_structured_signals(text: str, source_id: Any, origin_type: str, topic: str) -> List[ProcessedSignal]:
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    prompt = f"""
    Extract structured signals from this text about {topic}.
    
    Text: {text}
    
    Return JSON array with:
    - entity: what/who the stat is about
    - metric: what is being measured
    - value_now: the numeric value
    - unit: percent, dollars, etc.
    - context_sentence: the full sentence
    """
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    # Parse response and create ProcessedSignal objects
    # ... (implementation details)
```

**Similar changes needed in:** `processing/llm_insights.py`

### Adding Anthropic (Claude)

Similar process but use:
```python
import anthropic

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
```

---

## Database Management

### Viewing Data

**Using MongoDB Shell:**
```bash
mongosh
use quietlystated
db.raw_articles.find().limit(5)
db.processed_signals.find().sort({created_at: -1}).limit(10)
```

**Using Python:**
```python
from db.mongo_client import get_db

db = get_db()
articles = list(db.raw_articles.find().limit(5))
for article in articles:
    print(article["title"])
```

### Cleaning Old Data

**Delete old raw data:**
```python
from datetime import datetime, timedelta
from db.mongo_client import get_db

db = get_db()
cutoff = datetime.utcnow() - timedelta(days=90)

# Delete old trends
db.raw_trends.delete_many({"pulled_at": {"$lt": cutoff}})

# Delete old articles
db.raw_articles.delete_many({"fetched_at": {"$lt": cutoff}})
```

### Backup

**Export database:**
```bash
mongodump --uri="mongodb://localhost:27017/" --db=quietlystated --out=./backup
```

**Restore:**
```bash
mongorestore --uri="mongodb://localhost:27017/" --db=quietlystated ./backup/quietlystated
```

---

## Custom Processing

### Adding New Stat Patterns

**File:** `processing/stats_extractor.py`

**Add new regex pattern:**
```python
# Pattern for currency: "$1.5M" or "£500K"
currency_pattern = r'[£$€](\d+(?:\.\d+)?)([MK]?)'
for match in re.finditer(currency_pattern, text):
    # Process match
```

### Custom Topic Detection

**File:** `processing/topic_tagger.py`

**Add ML-based classification:**
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Train classifier
# Use for better topic detection
```

---

## Performance Optimization

### Indexing MongoDB

**Add indexes for faster queries:**
```python
from db.mongo_client import get_db

db = get_db()

# Index on common query fields
db.processed_signals.create_index("topic")
db.processed_signals.create_index("created_at")
db.raw_articles.create_index("published_at")
db.insights.create_index([("topic", 1), ("created_at", -1)])
```

### Caching

**Add Redis for caching:**
```python
import redis

r = redis.Redis(host='localhost', port=6379)

def get_cached_insights(topic):
    cache_key = f"insights:{topic}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    # ... fetch from DB and cache
```

---

## Extending Data Sources

### Adding New Source Type

**Example: Twitter/X scraping:**

1. Create `sources/twitter.py`:
```python
def fetch_and_store_tweets(config_path: str = "config/twitter.json"):
    # Implementation
    pass
```

2. Add to `config/feeds.json` or create `config/twitter.json`

3. Add job script: `jobs/ingest_twitter.py`

4. Add CLI command in `cli.py`

### Adding API Sources

**Example: Reddit API:**

```python
import praw  # Python Reddit API Wrapper

def fetch_reddit_posts(subreddit: str):
    reddit = praw.Reddit(
        client_id=os.getenv("REDDIT_CLIENT_ID"),
        client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
        user_agent="QuietlyStated/1.0"
    )
    
    for submission in reddit.subreddit(subreddit).hot(limit=10):
        # Process and store
        pass
```

---

## Custom Analytics

### Adding New Report Types

**File:** `analytics/trends_reports.py`

**Add function:**
```python
def get_custom_report(start: datetime, end: datetime) -> dict:
    """
    Your custom analysis here.
    """
    # Aggregate data
    # Calculate metrics
    # Return structured dict
    return {}
```

**Add CLI command:**
```python
@cli.command()
def custom_report():
    """Your custom report."""
    # Call your function
    # Print results
    pass
```

---

## Deployment

### Running on a VPS

**Requirements:**
- VPS with Python and MongoDB
- Domain name (optional)
- SSL certificate (for HTTPS)

**Steps:**
1. Copy project to VPS
2. Install dependencies
3. Configure `.env` with production MongoDB
4. Set up systemd service for API:
   ```ini
   [Unit]
   Description=QuietlyStated API
   
   [Service]
   ExecStart=/usr/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
   WorkingDirectory=/path/to/quietlystated
   
   [Install]
   WantedBy=multi-user.target
   ```
5. Set up nginx reverse proxy
6. Configure cron for jobs

### Docker Deployment

**Create `Dockerfile`:**
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0"]
```

**Create `docker-compose.yml`:**
```yaml
version: '3'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MONGODB_URI=mongodb://mongo:27017/
    depends_on:
      - mongo
  
  mongo:
    image: mongo:latest
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
```

---

## Monitoring

### Logging

**Add logging:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('quietlystated.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
logger.info("Starting ingestion...")
```

### Health Checks

**Add to API:**
```python
@app.get("/health")
def health_check():
    try:
        db = get_db()
        db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except:
        return {"status": "unhealthy", "database": "disconnected"}
```

---

## Security

### API Authentication

**Add API keys:**
```python
from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403)
    return api_key
```

### Environment Variables

**Never commit:**
- API keys
- Database passwords
- Secret tokens

**Always use `.env` file** (already in `.gitignore`)

---

## Contributing

### Code Style

- Use type hints
- Write docstrings
- Follow PEP 8
- Keep functions small and focused

### Testing

**Add tests:**
```python
# tests/test_stats_extractor.py
def test_extract_percentages():
    text = "Sales increased by 15%"
    candidates = extract_stat_candidates(text)
    assert len(candidates) > 0
```

**Run tests:**
```bash
pytest tests/
```

