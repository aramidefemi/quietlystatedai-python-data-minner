"""Command-line interface for QuietlyStated."""
import click
import json
from datetime import datetime, timedelta
from sources.google_trends import fetch_and_store_trends
from sources.google_alerts import fetch_and_store_alerts
from sources.blogs import fetch_and_store_articles
from jobs.extract_signals import enrich_signals
from jobs.aggregate_insights import aggregate_insights
from analytics.trends_reports import get_top_terms, get_top_topics, get_notable_stats
from db.mongo_client import close_connection
from config.config_manager import ConfigManager


@click.group()
def cli():
    """QuietlyStated CLI - Trend Intelligence System"""
    pass


@cli.group()
def config():
    """Manage configuration in MongoDB"""
    pass


@cli.command()
def fetch_trends():
    """Fetch and store Google Trends data."""
    click.echo("Fetching Google Trends data...")
    fetch_and_store_trends()
    click.echo("Done!")


@cli.command()
def fetch_alerts():
    """Fetch and store Google Alerts data."""
    click.echo("Fetching Google Alerts data...")
    fetch_and_store_alerts()
    click.echo("Done!")


@cli.command()
def fetch_articles():
    """Fetch and store blog articles."""
    click.echo("Fetching blog articles...")
    fetch_and_store_articles()
    click.echo("Done!")


@cli.command()
@click.option("--days", default=7, help="Process documents from last N days")
def enrich_signals_cmd(days):
    """Extract signals from raw documents."""
    click.echo(f"Extracting signals from last {days} days...")
    enrich_signals(days)
    click.echo("Done!")


@cli.command()
@click.option("--days", default=7, help="Generate insights for last N days")
def aggregate_insights_cmd(days):
    """Aggregate insights from signals."""
    click.echo(f"Generating insights for last {days} days...")
    aggregate_insights(days)
    click.echo("Done!")


@config.command("seed")
def config_seed():
    """Load JSON configs into MongoDB"""
    click.echo("🌱 Seeding MongoDB with JSON configs...")
    manager = ConfigManager()
    results = manager.seed_from_json()
    
    for config_name, success in results.items():
        if success:
            click.echo(f"  ✓ {config_name} loaded")
        else:
            click.echo(f"  ✗ {config_name} failed")
    
    click.echo("\n📊 Configuration Stats:")
    stats = manager.get_stats()
    click.echo(f"  Keywords: {stats['keywords']['total_terms']} terms in {stats['keywords']['groups']} groups across {stats['keywords']['regions']} regions")
    click.echo(f"  Feeds: {stats['feeds']['enabled']}/{stats['feeds']['total']} enabled")
    click.echo(f"  Topics: {stats['topics']['total']} topics")
    click.echo("\n✅ Done! Configs are now in MongoDB")


@config.command("show")
@click.argument("config_type", type=click.Choice(["keywords", "feeds", "topics", "all"]))
def config_show(config_type):
    """Show configuration from MongoDB"""
    manager = ConfigManager()
    
    if config_type in ["keywords", "all"]:
        click.echo("\n📊 KEYWORDS CONFIG")
        click.echo("="*60)
        kw_config = manager.get_keywords_config()
        click.echo(f"Regions: {', '.join(kw_config.get('regions', []))}")
        click.echo(f"Timeframe: {kw_config.get('timeframe', 'N/A')}")
        click.echo(f"\nGroups ({len(kw_config.get('groups', []))}):")
        for group in kw_config.get('groups', []):
            terms_count = len(group.get('terms', []))
            click.echo(f"  • {group['name']}: {terms_count} terms")
    
    if config_type in ["feeds", "all"]:
        click.echo("\n📰 FEEDS CONFIG")
        click.echo("="*60)
        feeds = manager.get_feeds_config()
        for feed in feeds:
            status = "✓" if feed.get("enabled", True) else "✗"
            keyword = f" ({feed['keyword']})" if feed.get('keyword') else ""
            click.echo(f"  {status} {feed['source']}{keyword}")
            click.echo(f"    {feed['url'][:70]}...")
    
    if config_type in ["topics", "all"]:
        click.echo("\n🏷️  TOPICS CONFIG")
        click.echo("="*60)
        topics = manager.get_topics_config()
        for topic, keywords in topics.items():
            click.echo(f"  • {topic}: {len(keywords)} keywords")
    
    click.echo()


@config.command("add-feed")
@click.argument("source")
@click.argument("url")
@click.option("--keyword", default=None, help="Keyword for Google Alerts")
def config_add_feed(source, url, keyword):
    """Add a new RSS feed"""
    manager = ConfigManager()
    success = manager.add_feed(source, url, keyword=keyword)
    
    if success:
        click.echo(f"✅ Added feed: {source}")
    else:
        click.echo(f"❌ Failed to add feed. Run 'config seed' first.")


@config.command("add-term")
@click.argument("group")
@click.argument("term")
def config_add_term(group, term):
    """Add a term to a keyword group"""
    manager = ConfigManager()
    success = manager.add_keyword_term(group, term)
    
    if success:
        click.echo(f"✅ Added '{term}' to '{group}' group")
    else:
        click.echo(f"❌ Failed to add term. Check if group exists.")


@cli.command()
def weekly_report():
    """Print weekly report comparing this week vs last week."""
    now = datetime.utcnow()
    current_end = now
    current_start = now - timedelta(days=7)
    previous_end = current_start
    previous_start = previous_end - timedelta(days=7)
    
    click.echo("\n" + "="*60)
    click.echo("QUIETLYSTATED WEEKLY REPORT")
    click.echo("="*60)
    
    # Top search terms
    click.echo("\n📈 TOP SEARCH TERMS")
    click.echo("-" * 60)
    terms_data = get_top_terms(current_start, current_end, previous_start, previous_end)
    
    click.echo("\nTop by Average Interest:")
    for i, term in enumerate(terms_data["top_by_avg"][:5], 1):
        click.echo(f"  {i}. {term['term']}: {term['avg_current']:.1f} (was {term['avg_previous']:.1f})")
    
    click.echo("\nTop by Growth:")
    for i, term in enumerate(terms_data["top_by_growth"][:5], 1):
        click.echo(f"  {i}. {term['term']}: {term['growth_pct']:+.1f}%")
    
    # Top topics
    click.echo("\n🏷️  TOP TOPICS")
    click.echo("-" * 60)
    topics_data = get_top_topics(current_start, current_end, previous_start, previous_end)
    
    click.echo("\nTop by Signal Count:")
    for i, topic in enumerate(topics_data["top_by_count"][:5], 1):
        click.echo(f"  {i}. {topic['topic']}: {topic['count_current']} signals")
    
    click.echo("\nTop by Growth:")
    for i, topic in enumerate(topics_data["top_by_growth"][:5], 1):
        click.echo(f"  {i}. {topic['topic']}: {topic['growth_pct']:+.1f}%")
    
    # Notable stats
    click.echo("\n📊 NOTABLE STATISTICS")
    click.echo("-" * 60)
    notable = get_notable_stats(current_start, current_end, threshold=5.0)
    
    for i, stat in enumerate(notable[:5], 1):
        click.echo(f"\n  {i}. {stat['topic']} - {stat['metric']}")
        click.echo(f"     {stat['value']:+.1f}% - {stat['entity']}")
        click.echo(f"     {stat['context'][:100]}...")
    
    click.echo("\n" + "="*60 + "\n")


if __name__ == "__main__":
    try:
        cli()
    finally:
        close_connection()

