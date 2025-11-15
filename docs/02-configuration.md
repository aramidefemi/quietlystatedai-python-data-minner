# Configuration Guide

## Where to Put Your Settings

All configuration files are in the `config/` folder:
- `config/keywords.json` - What to search on Google Trends
- `config/feeds.json` - Which blogs and alerts to read
- `config/topics.json` - How to categorize content

## 1. Google Trends Keywords

**File**: `config/keywords.json`

**What is this?** Tells the system what search terms to track on Google Trends.

**How to edit:**
1. Open `config/keywords.json` in a text editor
2. You'll see something like:
   ```json
   {
     "regions": ["GB"],
     "timeframe": "now 7-d",
     "groups": [
       {
         "name": "beauty_products",
         "terms": ["press on nails", "acrylic nails", "lip gloss"]
       }
     ]
   }
   ```

**What to change:**

- **`regions`**: Which countries to track
  - `"GB"` = United Kingdom
  - `"US"` = United States
  - `"AU"` = Australia
  - Add more: `["GB", "US", "AU"]`

- **`timeframe`**: How far back to look
  - `"now 7-d"` = Last 7 days
  - `"now 1-m"` = Last month
  - `"now 1-y"` = Last year

- **`groups`**: Categories of search terms
  - `"name"`: A short name for this category (no spaces, use underscores)
  - `"terms"`: List of search terms to track

**Example for fashion brand:**
```json
{
  "regions": ["GB", "US"],
  "timeframe": "now 7-d",
  "groups": [
    {
      "name": "fashion_trends",
      "terms": ["cargo pants", "linen trousers", "sneakers", "loafers"]
    },
    {
      "name": "shopping_behavior",
      "terms": ["same day delivery", "click and collect", "free shipping"]
    }
  ]
}
```

**Tips:**
- Keep term groups to 5 terms or less (Google Trends limit)
- Use phrases people actually search for
- Group related terms together

## 2. Blog Feeds and Alerts

**File**: `config/feeds.json`

**What is this?** Tells the system which blogs and Google Alerts to read.

**How to edit:**
1. Open `config/feeds.json`
2. You'll see a list of sources:
   ```json
   [
     {
       "source": "shopify_blog",
       "url": "https://www.shopify.com/blog/rss",
       "type": "rss"
     }
   ]
   ```

**Adding a blog:**

1. Find the blog's RSS feed URL
   - Usually: `blogname.com/rss` or `blogname.com/feed`
   - Look for an RSS icon on the blog
   - Or add `/rss` or `/feed` to the blog URL

2. Add to the list:
   ```json
   {
     "source": "your_blog_name",
     "url": "https://blogname.com/rss",
     "type": "rss"
   }
   ```

**Adding Google Alerts:**

1. Set up a Google Alert at [google.com/alerts](https://www.google.com/alerts)
   - Enter your search term
   - Choose "RSS feed" as delivery method
   - Copy the RSS feed URL

2. Add to the list:
   ```json
   {
     "source": "google_alerts_your_topic",
     "url": "https://www.google.com/alerts/feeds/...",
     "type": "rss",
     "keyword": "your search term"
   }
   ```

**Important**: Google Alert sources must start with `"google_alerts_"`

**Example:**
```json
[
  {
    "source": "shopify_blog",
    "url": "https://www.shopify.com/blog/rss",
    "type": "rss"
  },
  {
    "source": "klaviyo_blog",
    "url": "https://www.klaviyo.com/blog/rss",
    "type": "rss"
  },
  {
    "source": "google_alerts_tiktok_shop",
    "url": "https://www.google.com/alerts/feeds/123456789/123456789",
    "type": "rss",
    "keyword": "tiktok shop ecommerce"
  }
]
```

## 3. Topic Categories

**File**: `config/topics.json`

**What is this?** Tells the system how to categorize articles and alerts.

**How it works:** The system looks for keywords in text and assigns topics.

**How to edit:**
1. Open `config/topics.json`
2. You'll see topics with keyword lists:
   ```json
   {
     "tiktok_shop": ["tiktok shop", "tt shop"],
     "email_sms": ["email", "newsletter", "klaviyo"]
   }
   ```

**Adding a topic:**

1. Choose a topic name (use underscores, no spaces)
2. List keywords that relate to that topic
3. The system counts how many times these words appear

**Example:**
```json
{
  "tiktok_shop": ["tiktok shop", "tt shop", "tiktok commerce"],
  "email_sms": ["email", "newsletter", "klaviyo", "sms", "text message"],
  "pricing": ["price", "pricing", "cost", "affordable", "expensive"],
  "your_topic": ["keyword1", "keyword2", "keyword3"]
}
```

**Tips:**
- Use lowercase keywords
- Include variations (e.g., "email" and "e-mail")
- More keywords = better matching

## Testing Your Configuration

After editing, test it:

```bash
# Test trends
python cli.py fetch-trends

# Test blogs
python cli.py fetch-articles

# Test alerts
python cli.py fetch-alerts
```

If you see no errors, your configuration is good!

## Common Questions

**Q: How many keywords can I track?**
A: Google Trends allows 5 terms per request. The system automatically chunks larger lists.

**Q: Can I use the same keyword in multiple groups?**
A: Yes, but it will create duplicate data. Better to organize by category.

**Q: What if a blog doesn't have RSS?**
A: The system will try to scrape the HTML, but RSS is more reliable.

**Q: How often should I update these files?**
A: As needed. Add new terms when trends change, add blogs as you discover them.

