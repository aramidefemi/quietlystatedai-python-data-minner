# MCP Field Name Fix

## The Problem

The `get_top_topics` tool was failing with error: `'current_count'`

This was a KeyError caused by mismatched field names between the analytics functions and the MCP server.

## Root Cause

The analytics functions in `analytics/trends_reports.py` return data structures with specific field names:

### `get_top_topics()` returns:
- `count_current` (not `current_count`)
- `count_previous` (not `previous_count`)

### `get_top_terms()` returns:
- `avg_current` (not `current_avg`)
- `avg_previous` (not `previous_avg`)

## The Fix

Updated `mcp_server.py` to use the correct field names in these methods:

1. **`_get_top_topics()`**:
   - Changed `topic['current_count']` → `topic['count_current']`
   
2. **`_get_top_terms()`**:
   - Changed `term['current_avg']` → `term['avg_current']`
   
3. **`_get_weekly_report()`**:
   - Changed `term['current_avg']` → `term['avg_current']`
   - Changed `topic['current_count']` → `topic['count_current']`

## Files Modified

- `/Users/mac/Desktop/projects/quietlystated/mcp_server.py`
  - Line 228: Fixed terms in weekly report
  - Line 237: Fixed topics in weekly report
  - Line 258: Fixed terms in get_top_terms
  - Line 280: Fixed topics in get_top_topics

## Testing

After restarting Claude Desktop, these queries should now work:

1. **"Get top topics"** - Should show topics by count and growth
2. **"Show me the weekly report"** - Should include terms and topics without errors
3. **"What are the top 15 topics?"** - Should return formatted list

## Status

✅ **Fixed!** The MCP server has been restarted with the corrected field names.

**Next Step:** Restart Claude Desktop to connect to the updated server.

