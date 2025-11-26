"""MCP server for QuietlyStated - Connect to Claude."""
import asyncio
import json
import sys
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from db.mongo_client import get_db
from db.models import Insight, ProcessedSignal, RawArticle, RawTrend
from analytics.trends_reports import get_top_terms, get_top_topics, get_notable_stats


class MCPServer:
    """Model Context Protocol server for QuietlyStated."""
    
    def __init__(self):
        self.db = get_db()
    
    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP JSON-RPC request."""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        # Notifications (no id) should not be responded to
        if request_id is None:
            if method and method.startswith("notifications/"):
                return None  # Silently ignore notifications
        
        try:
            if method == "initialize":
                result = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "serverInfo": {
                        "name": "quietlystated",
                        "version": "1.0.0"
                    }
                }
            elif method == "tools/list":
                result = {
                    "tools": [
                        {
                            "name": "get_weekly_report",
                            "description": "Get weekly trend report comparing this week vs last week",
                            "inputSchema": {
                                "type": "object"
                            }
                        },
                        {
                            "name": "get_insights",
                            "description": "Get recent insights. Optional params: topic (string), limit (number), days (number)",
                            "inputSchema": {
                                "type": "object"
                            }
                        },
                        {
                            "name": "get_signals",
                            "description": "Get processed signals. Optional params: topic (string), limit (number), days (number)",
                            "inputSchema": {
                                "type": "object"
                            }
                        },
                        {
                            "name": "get_top_terms",
                            "description": "Get top search terms. Optional param: limit (number)",
                            "inputSchema": {
                                "type": "object"
                            }
                        },
                        {
                            "name": "get_top_topics",
                            "description": "Get top topics. Optional param: limit (number)",
                            "inputSchema": {
                                "type": "object"
                            }
                        },
                        {
                            "name": "get_notable_stats",
                            "description": "Get notable statistics. Optional param: threshold (number, default 5.0)",
                            "inputSchema": {
                                "type": "object"
                            }
                        },
                        {
                            "name": "search_articles",
                            "description": "Search articles. Optional params: keyword (string), source (string), limit (number)",
                            "inputSchema": {
                                "type": "object"
                            }
                        }
                    ]
                }
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                result = await self._call_tool(tool_name, arguments)
            else:
                result = {"error": f"Unknown method: {method}"}
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32000,
                    "message": str(e)
                }
            }
    
    async def _call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call and return MCP-formatted result."""
        # Call the appropriate tool method to get text content
        if tool_name == "get_insights":
            text_result = await self._get_insights(
                topic=arguments.get("topic"),
                limit=int(arguments.get("limit", 10)),
                days=int(arguments.get("days", 7))
            )
        elif tool_name == "get_signals":
            text_result = await self._get_signals(
                topic=arguments.get("topic"),
                limit=int(arguments.get("limit", 20)),
                days=int(arguments.get("days", 7))
            )
        elif tool_name == "get_weekly_report":
            text_result = await self._get_weekly_report()
        elif tool_name == "get_top_terms":
            text_result = await self._get_top_terms(limit=int(arguments.get("limit", 10)))
        elif tool_name == "get_top_topics":
            text_result = await self._get_top_topics(limit=int(arguments.get("limit", 10)))
        elif tool_name == "get_notable_stats":
            text_result = await self._get_notable_stats(threshold=float(arguments.get("threshold", 5.0)))
        elif tool_name == "search_articles":
            text_result = await self._search_articles(
                keyword=arguments.get("keyword"),
                source=arguments.get("source"),
                limit=int(arguments.get("limit", 10))
            )
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Return MCP-formatted response with text content
        return {
            "content": [
                {
                    "type": "text",
                    "text": text_result
                }
            ]
        }
    
    async def _get_insights(self, topic: Optional[str], limit: int, days: int) -> str:
        """Get insights formatted as readable text."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = {"created_at": {"$gte": cutoff}}
        if topic:
            query["topic"] = topic
        
        insights = list(self.db.insights.find(query).sort("created_at", -1).limit(limit))
        
        if not insights:
            return f"No insights found in the last {days} days" + (f" for topic '{topic}'" if topic else "")
        
        lines = [f"📊 Found {len(insights)} insights:\n"]
        for i, insight in enumerate(insights, 1):
            lines.append(f"\n{i}. **{insight.get('title', 'Untitled')}**")
            lines.append(f"   Topic: {insight.get('topic', 'N/A')}")
            lines.append(f"   Summary: {insight.get('summary', 'N/A')}")
            lines.append(f"   Implication: {insight.get('implication', 'N/A')}")
            if insight.get('target_audience'):
                lines.append(f"   For: {insight.get('target_audience')}")
        
        return "\n".join(lines)
    
    async def _get_signals(self, topic: Optional[str], limit: int, days: int) -> str:
        """Get processed signals formatted as text."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = {"created_at": {"$gte": cutoff}}
        if topic:
            query["topic"] = topic
        
        signals = list(self.db.processed_signals.find(query).sort("created_at", -1).limit(limit))
        
        if not signals:
            return f"No signals found in the last {days} days" + (f" for topic '{topic}'" if topic else "")
        
        lines = [f"📈 Found {len(signals)} signals:\n"]
        for i, signal in enumerate(signals, 1):
            entity = signal.get('entity', 'Unknown')
            metric = signal.get('metric', 'metric')
            value = signal.get('value_now', 'N/A')
            unit = signal.get('unit', '')
            topic_name = signal.get('topic', 'N/A')
            context = signal.get('context_sentence', '')
            
            lines.append(f"\n{i}. [{topic_name}] {entity}: {metric} = {value}{unit}")
            if context:
                lines.append(f"   Context: {context[:150]}...")
        
        return "\n".join(lines)
    
    async def _get_weekly_report(self) -> str:
        """Get weekly comparison report formatted as text."""
        now = datetime.utcnow()
        current_end = now
        current_start = now - timedelta(days=7)
        previous_end = current_start
        previous_start = previous_end - timedelta(days=7)
        
        terms = get_top_terms(current_start, current_end, previous_start, previous_end, limit=10)
        topics = get_top_topics(current_start, current_end, previous_start, previous_end, limit=10)
        stats = get_notable_stats(current_start, current_end, threshold=5.0)
        
        lines = ["📊 **WEEKLY REPORT**\n"]
        lines.append(f"Current Week: {current_start.strftime('%Y-%m-%d')} to {current_end.strftime('%Y-%m-%d')}")
        lines.append(f"Previous Week: {previous_start.strftime('%Y-%m-%d')} to {previous_end.strftime('%Y-%m-%d')}\n")
        
        lines.append("\n🔥 **TOP TERMS BY INTEREST:**")
        for i, term in enumerate(terms["top_by_avg"][:5], 1):
            lines.append(f"{i}. {term['term']}: {term['avg_current']:.1f} avg interest")
        
        lines.append("\n📈 **FASTEST GROWING TERMS:**")
        for i, term in enumerate(terms["top_by_growth"][:5], 1):
            growth = term.get('growth_pct', 0)
            lines.append(f"{i}. {term['term']}: +{growth:.1f}% growth")
        
        lines.append("\n🏷️  **TOP TOPICS:**")
        for i, topic in enumerate(topics["top_by_count"][:5], 1):
            lines.append(f"{i}. {topic['topic']}: {topic['count_current']} mentions")
        
        lines.append("\n💡 **NOTABLE STATS:**")
        for i, stat in enumerate(stats[:5], 1):
            lines.append(f"{i}. {stat['entity']}: {stat['metric']} = {stat['value']}{stat.get('unit', '')}")
        
        return "\n".join(lines)
    
    async def _get_top_terms(self, limit: int) -> str:
        """Get top search terms formatted as text."""
        now = datetime.utcnow()
        current_end = now
        current_start = now - timedelta(days=7)
        previous_end = current_start
        previous_start = previous_end - timedelta(days=7)
        
        terms = get_top_terms(current_start, current_end, previous_start, previous_end, limit=limit)
        
        lines = [f"🔍 **TOP {limit} SEARCH TERMS**\n"]
        lines.append("**By Interest:**")
        for i, term in enumerate(terms["top_by_avg"][:limit], 1):
            lines.append(f"{i}. {term['term']}: {term['avg_current']:.1f} avg interest")
        
        lines.append("\n**By Growth:**")
        for i, term in enumerate(terms["top_by_growth"][:limit], 1):
            growth = term.get('growth_pct', 0)
            lines.append(f"{i}. {term['term']}: +{growth:.1f}% growth")
        
        return "\n".join(lines)
    
    async def _get_top_topics(self, limit: int) -> str:
        """Get top topics formatted as text."""
        now = datetime.utcnow()
        current_end = now
        current_start = now - timedelta(days=7)
        previous_end = current_start
        previous_start = previous_end - timedelta(days=7)
        
        topics = get_top_topics(current_start, current_end, previous_start, previous_end, limit=limit)
        
        lines = [f"🏷️  **TOP {limit} TOPICS**\n"]
        lines.append("**By Count:**")
        for i, topic in enumerate(topics["top_by_count"][:limit], 1):
            lines.append(f"{i}. {topic['topic']}: {topic['count_current']} mentions")
        
        lines.append("\n**By Growth:**")
        for i, topic in enumerate(topics["top_by_growth"][:limit], 1):
            growth = topic.get('growth_pct', 0)
            lines.append(f"{i}. {topic['topic']}: +{growth:.1f}% growth")
        
        return "\n".join(lines)
    
    async def _get_notable_stats(self, threshold: float) -> str:
        """Get notable statistics formatted as text."""
        now = datetime.utcnow()
        current_end = now
        current_start = now - timedelta(days=7)
        
        stats = get_notable_stats(current_start, current_end, threshold=threshold)
        
        if not stats:
            return f"No notable stats found with threshold >= {threshold}"
        
        lines = [f"💡 **NOTABLE STATS** (threshold: {threshold})\n"]
        for i, stat in enumerate(stats, 1):
            entity = stat['entity']
            metric = stat['metric']
            value = stat['value']
            unit = stat.get('unit', '')
            context = stat.get('context', '')
            
            lines.append(f"\n{i}. **{entity}**")
            lines.append(f"   {metric}: {value}{unit}")
            if context:
                lines.append(f"   Context: {context[:120]}...")
        
        return "\n".join(lines)
    
    async def _search_articles(self, keyword: Optional[str], source: Optional[str], limit: int) -> str:
        """Search articles formatted as text."""
        query = {}
        if source:
            query["source_origin"] = source
        
        articles = list(self.db.raw_articles.find(query).sort("published_at", -1).limit(limit))
        
        if keyword:
            articles = [
                a for a in articles
                if keyword.lower() in a.get("title", "").lower() or keyword.lower() in a.get("text", "").lower()
            ][:limit]
        
        if not articles:
            filters = []
            if keyword:
                filters.append(f"keyword '{keyword}'")
            if source:
                filters.append(f"source '{source}'")
            filter_str = " and ".join(filters) if filters else "any criteria"
            return f"No articles found matching {filter_str}"
        
        lines = [f"📰 **FOUND {len(articles)} ARTICLES**\n"]
        for i, article in enumerate(articles, 1):
            title = article.get("title", "Untitled")
            source_name = article.get("source_origin", "Unknown")
            url = article.get("url", "")
            published = article.get("published_at")
            date_str = published.strftime("%Y-%m-%d") if published else "Unknown date"
            data_points = article.get("data_points", [])
            
            lines.append(f"\n{i}. **{title}**")
            lines.append(f"   Source: {source_name} | Date: {date_str}")
            lines.append(f"   URL: {url}")
            if data_points:
                lines.append(f"   Key Data:")
                for dp in data_points[:2]:
                    lines.append(f"   • {dp[:100]}...")
        
        return "\n".join(lines)


async def main():
    """Main server loop - reads from stdin, writes to stdout."""
    server = MCPServer()
    
    # Read initialization
    init_line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
    if init_line:
        init_request = json.loads(init_line.strip())
        response = await server.handle_request(init_request)
        if response is not None:
            print(json.dumps(response), flush=True)
    
    # Main loop
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
            
            request = json.loads(line)
            response = await server.handle_request(request)
            if response is not None:
                print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            continue
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32000,
                    "message": str(e)
                }
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    asyncio.run(main())

