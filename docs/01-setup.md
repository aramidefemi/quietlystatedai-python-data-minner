# Setup Guide

## Step 1: Install Python

**What is Python?** The programming language this tool uses.

**How to check if you have it:**
1. Open Terminal (Mac) or Command Prompt (Windows)
2. Type: `python --version`
3. If you see a version number (like "Python 3.9.0"), you're good!
4. If you see an error, you need to install it

**How to install:**
- **Mac**: Download from [python.org](https://www.python.org/downloads/)
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **Linux**: Usually already installed, or use: `sudo apt install python3`

## Step 2: Install MongoDB

**What is MongoDB?** The database where all your data is stored.

**How to install:**

### Mac (using Homebrew):
```bash
brew tap mongodb/brew
brew install mongodb-community
brew services start mongodb-community
```

### Windows:
1. Download from [mongodb.com/try/download/community](https://www.mongodb.com/try/download/community)
2. Run the installer
3. Choose "Complete" installation
4. MongoDB will start automatically

### Linux:
```bash
sudo apt install mongodb
sudo systemctl start mongodb
```

**How to check if it's working:**
- Open Terminal/Command Prompt
- Type: `mongosh` (or `mongo` on older versions)
- If you see a prompt, it's working!

## Step 3: Install Project Dependencies

**What are dependencies?** Extra tools the project needs to work.

1. Open Terminal/Command Prompt
2. Go to the project folder:
   ```bash
   cd /Users/mac/Desktop/projects/quietlystated
   ```
3. Install everything:
   ```bash
   pip install -r requirements.txt
   ```

**This installs:**
- `pymongo` - Connects to MongoDB
- `pytrends` - Gets Google Trends data
- `feedparser` - Reads RSS feeds
- `beautifulsoup4` - Scrapes web pages
- `fastapi` - Creates the web API
- And a few others

## Step 4: Configure Environment

**What is this?** Settings that tell the system where to find MongoDB.

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Open `.env` in a text editor

3. Set your MongoDB connection:
   ```
   MONGODB_URI=mongodb://localhost:27017/
   MONGODB_DB_NAME=quietlystated
   ```

   **What does this mean?**
   - `MONGODB_URI` - Where MongoDB is running (localhost = your computer)
   - `MONGODB_DB_NAME` - Name of your database

   **If MongoDB is on a different computer**, change `localhost` to that computer's address.

## Step 5: Test It Works

Run a simple test:
```bash
python cli.py weekly-report
```

If you see a report (even if empty), everything is working!

## Troubleshooting

**"Python not found"**
- Make sure Python is installed and in your PATH
- Try `python3` instead of `python`

**"MongoDB connection failed"**
- Make sure MongoDB is running: `mongosh`
- Check your `.env` file has the correct URI

**"Module not found"**
- Run `pip install -r requirements.txt` again
- Make sure you're in the project folder

## Optional: API Keys (For Later)

**You don't need these to start!** But if you want better AI insights later:

1. **OpenAI** (for GPT):
   - Sign up at [openai.com](https://openai.com)
   - Get API key from dashboard
   - Add to `.env`: `OPENAI_API_KEY=your_key_here`

2. **Anthropic** (for Claude):
   - Sign up at [anthropic.com](https://anthropic.com)
   - Get API key
   - Add to `.env`: `ANTHROPIC_API_KEY=your_key_here`

**Note**: The system works without these - it just uses simpler extraction methods.

