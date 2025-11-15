# QuietlyStated

A simple tool that watches the internet for trends and tells you what's important for your business.

## What Does This Do?

Imagine you have a smart assistant that:
- Watches what people are searching for on Google
- Reads news articles and blog posts about your industry
- Finds important numbers and facts (like "sales up 15%")
- Summarizes everything into easy-to-read insights

**Before a meeting**, you can ask: "What changed this week?" and get a quick summary of what matters.

## Who Is This For?

Perfect for:
- Ecommerce brand managers
- Marketers who need quick trend updates
- Business owners who want to stay informed
- Anyone who needs data-backed insights before meetings

## What You Need to Get Started

1. **A computer** (Mac, Windows, or Linux)
2. **Python** (free programming language - easy to install)
3. **MongoDB** (free database - stores your data)
4. **Internet connection**

**Good news:** You don't need any special accounts or API keys to start! Everything works with free services.

## Quick Start

### 1. Install Everything

Follow the step-by-step guide in `docs/01-setup.md`. It walks you through:
- Installing Python
- Installing MongoDB
- Setting up the project

### 2. Tell It What to Watch

Edit these files to customize what the system tracks:

- **`config/keywords.json`** - What to search on Google Trends
  - Example: "press on nails", "cargo pants", "same day delivery"

- **`config/feeds.json`** - Which blogs and news feeds to read
  - Example: Shopify blog, Klaviyo blog, your Google Alerts

- **`config/topics.json`** - How to categorize content
  - Example: "tiktok_shop", "email_sms", "retention"

See `docs/02-configuration.md` for detailed instructions.

### 3. Run It Daily

**Morning (fetch new data):**
```bash
python cli.py fetch-trends
python cli.py fetch-alerts
python cli.py fetch-articles
```

**Afternoon (process the data):**
```bash
python cli.py enrich-signals
python cli.py aggregate-insights
```

**Before meetings (get your report):**
```bash
python cli.py weekly-report
```

## What You'll See

When you run `weekly-report`, you'll get:

- **Top Search Terms** - What's popular, what's growing
- **Top Topics** - What subjects are trending in news/blogs
- **Notable Statistics** - Important numbers that changed

Example:
```
📈 TOP SEARCH TERMS
  1. press on nails: 65.3 (was 58.2) - up 12.2%
  2. cargo pants: 72.1 (was 70.5) - up 2.3%

🏷️ TOP TOPICS
  1. tiktok_shop: 15 signals
  2. email_sms: 12 signals

📊 NOTABLE STATISTICS
  TikTok Shop sales increased 23.5% among Gen Z consumers...
```

## How It Works (Simple Version)

1. **Collects Data** - Automatically fetches:
   - Google Trends (what people search for)
   - Google Alerts (news mentions)
   - Blog posts (from websites you choose)

2. **Finds Important Stuff** - Reads everything and finds:
   - Important numbers (like "sales up 15%")
   - Topics (like "TikTok Shop" or "email marketing")
   - Trends (what's going up or down)

3. **Creates Insights** - Summarizes everything into:
   - Short summaries
   - Actionable recommendations
   - Easy-to-read reports

4. **You Access It** - Via:
   - Command line (simple text commands)
   - Web API (if you want to build something on top)

## Optional: Make It Smarter

The basic version works great, but you can make it smarter by adding AI:

- **OpenAI** (ChatGPT) - Better at understanding context
- **Anthropic** (Claude) - Alternative AI option

**You don't need this to start!** The system works fine without it. See `docs/05-advanced.md` if you want to add AI later.

## Automation (Set It and Forget It)

You can schedule everything to run automatically:

- Every morning at 9 AM: Fetch new data
- Every morning at 10 AM: Process the data
- You just check the report when you need it

See `docs/04-usage.md` for how to set this up (it's easier than it sounds!).

## Need Help?

**📚 Full documentation is in the `docs/` folder!**

Start here:
- **`docs/README.md`** - Documentation index (where to find everything)
- **`docs/00-overview.md`** - What is QuietlyStated? (more details)
- **`docs/01-setup.md`** - Step-by-step installation
- **`docs/02-configuration.md`** - How to configure (where to put keywords, feeds, etc.)
- **`docs/QUICK-REFERENCE.md`** - Quick command cheat sheet
- **`docs/06-troubleshooting.md`** - Common problems and solutions

All documentation is written in simple, non-technical language. If you can follow a recipe, you can follow these guides!

## Project Structure (For Reference)

If you're curious about how it's organized:

```
quietlystated/
  api/              # Web API (optional - for advanced users)
  config/           # Your settings (keywords, feeds, topics)
  db/               # Database connection
  sources/          # Data collection (trends, alerts, blogs)
  processing/       # Finding important information
  analytics/        # Creating reports
  jobs/             # Scripts you can run
  docs/             # All the documentation
```

## Common Questions

**Q: Do I need to know how to code?**
A: No! Just follow the setup guide and run the commands. It's like using a recipe.

**Q: How much does it cost?**
A: Free! All the basic services are free. Only AI features cost money (and those are optional).

**Q: Can I run this on my laptop?**
A: Yes! That's exactly what it's designed for.

**Q: How often should I run it?**
A: Once per day is usually enough. You can automate it so you don't have to remember.

**Q: What if something breaks?**
A: Check `docs/06-troubleshooting.md` - it covers most common problems.

## License

MIT License — You’re welcome to use, modify, or share this for personal or educational projects.  
**However:** Commercial use without permission is prohibited. This is my intellectual property.  
If you attempt to steal or sell this for profit without a proper license, I reserve the right to take legal action.

---

**Ready to start?** Open `docs/01-setup.md` and follow along! 🚀
