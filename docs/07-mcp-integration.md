# MCP Integration with Claude

Connect QuietlyStated to Claude Desktop so you can ask Claude questions about your trends and insights!

## What is MCP?

**MCP (Model Context Protocol)** is a way for Claude to connect to external tools and data sources. Think of it like giving Claude access to your QuietlyStated database so it can answer questions about your trends.

## What You Can Do

Once connected, you can ask Claude things like:
- "What are the top trends this week?"
- "Show me insights about TikTok Shop"
- "What statistics changed significantly?"
- "Find articles about email marketing"

Claude will use the MCP server to query your QuietlyStated data and give you intelligent answers.

## Setup

### Step 1: Make Sure Everything Works

First, make sure QuietlyStated is working:
```bash
python cli.py weekly-report
```

If this works, you're good to go!

### Step 2: Find Claude Desktop Config

**Mac:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

### Step 3: Edit the Config File

1. Open the config file in a text editor
2. If it doesn't exist, create it
3. Add this configuration:

```json
{
  "mcpServers": {
    "quietlystated": {
      "command": "python",
      "args": [
        "/full/path/to/quietlystated/mcp_server.py"
      ],
      "env": {
        "MONGODB_URI": "mongodb://localhost:27017/",
        "MONGODB_DB_NAME": "quietlystated"
      }
    }
  }
}
```

**Important:** Replace `/full/path/to/quietlystated` with your actual project path!

**Example (Mac):**
```json
{
  "mcpServers": {
    "quietlystated": {
      "command": "python",
      "args": [
        "/Users/mac/Desktop/projects/quietlystated/mcp_server.py"
      ],
      "env": {
        "MONGODB_URI": "mongodb://localhost:27017/",
        "MONGODB_DB_NAME": "quietlystated"
      }
    }
  }
}
```

### Step 4: Restart Claude Desktop

1. Quit Claude Desktop completely
2. Reopen Claude Desktop
3. You should see "quietlystated" in the available tools

### Step 5: Test It

In Claude, try asking:
- "What insights do you have from QuietlyStated?"
- "Show me the weekly report"
- "What are the top search terms?"

Claude should be able to access your data!

## Available Tools

The MCP server exposes these tools to Claude:

### `get_insights`
Get recent insights
- **Parameters:**
  - `topic` (optional) - Filter by topic
  - `limit` (default: 10) - Number of results
  - `days` (default: 7) - Days to look back

### `get_signals`
Get processed signals (extracted statistics)
- **Parameters:**
  - `topic` (optional) - Filter by topic
  - `limit` (default: 20) - Number of results
  - `days` (default: 7) - Days to look back

### `get_weekly_report`
Get weekly trend report (this week vs last week)
- **Parameters:** None

### `get_top_terms`
Get top search terms by interest and growth
- **Parameters:**
  - `limit` (default: 10) - Number of results

### `get_top_topics`
Get top topics from articles and alerts
- **Parameters:**
  - `limit` (default: 10) - Number of results

### `get_notable_stats`
Get notable statistics with significant changes
- **Parameters:**
  - `threshold` (default: 5.0) - Minimum % change

### `search_articles`
Search articles by keyword or source
- **Parameters:**
  - `keyword` (optional) - Search term
  - `source` (optional) - Filter by source
  - `limit` (default: 10) - Number of results

## Troubleshooting

### "MCP server not found"

**Check:**
1. Is the path to `mcp_server.py` correct?
2. Does Python work? Try: `python --version`
3. Is MongoDB running? Try: `mongosh`

**Fix:**
- Use absolute path (full path from root)
- Make sure Python is in your PATH
- Start MongoDB if it's not running

### "Connection failed"

**Check:**
1. Are MongoDB environment variables correct?
2. Is MongoDB accessible?

**Fix:**
- Update `MONGODB_URI` in the config if MongoDB is on a different machine
- Test MongoDB connection: `mongosh`

### "No tools available"

**Check:**
1. Did you restart Claude Desktop after editing config?
2. Are there any errors in Claude Desktop logs?

**Fix:**
- Restart Claude Desktop completely
- Check Claude Desktop logs for errors
- Verify the config JSON is valid (use a JSON validator)

### "Python not found"

**Fix:**
- Use full path to Python: `"/usr/bin/python3"` or `"C:\\Python\\python.exe"`
- Or use `python3` instead of `python` in the command

## Example Queries

Once connected, try these in Claude:

**Basic queries:**
- "What insights do you have?"
- "Show me the weekly report"
- "What are the top trends?"

**Filtered queries:**
- "Show me insights about TikTok Shop"
- "What signals do you have for email marketing?"
- "Find articles about retention"

**Analysis queries:**
- "What statistics changed significantly this week?"
- "Which topics are growing fastest?"
- "What search terms are trending up?"

**Comparison queries:**
- "Compare this week to last week"
- "What's different about TikTok Shop trends?"

## Advanced: Custom Tools

Want to add more tools? Edit `mcp_server.py` and add new tool handlers in the `_call_tool` method.

## Security Note

The MCP server only reads from your database - it doesn't modify anything. It's safe to use!

---

**Need help?** Check `docs/06-troubleshooting.md` for general troubleshooting tips.

