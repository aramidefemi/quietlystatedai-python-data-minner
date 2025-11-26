# Plan: Move Configuration to MongoDB

## 🎯 Goal
Store all configuration (`keywords.json`, `feeds.json`, `topics.json`) in MongoDB instead of JSON files, allowing dynamic updates without code changes.

## 📋 Current State

### Config Files
1. **`config/keywords.json`** - Google Trends search terms
   - Regions (NG, ZA, GB, FR, US, CA)
   - Groups (fashion, beauty, drinks, etc.)
   - Terms per group
   - Timeframe settings

2. **`config/feeds.json`** - RSS feeds
   - Blog feeds (Shopify, Klaviyo, etc.)
   - Google Alerts feeds
   - Source names and URLs

3. **`config/topics.json`** - Topic classification
   - Topic keywords
   - Pattern matching

## 🏗️ Proposed Architecture

### 1. New MongoDB Collections

#### Collection: `config_keywords`
```javascript
{
  _id: ObjectId("..."),
  config_type: "keywords",
  version: 1,
  updated_at: ISODate("2025-11-19"),
  updated_by: "system",
  active: true,  // Support for multiple versions
  
  // Configuration data
  regions: ["NG", "ZA", "GB", "FR", "US", "CA"],
  timeframe: "now 7-d",
  groups: [
    {
      name: "fashion",
      enabled: true,
      terms: ["cargo pants", "linen trousers", ...]
    },
    {
      name: "beauty",
      enabled: true,
      terms: ["press on nails", "lip gloss", ...]
    }
  ]
}
```

#### Collection: `config_feeds`
```javascript
{
  _id: ObjectId("..."),
  config_type: "feeds",
  version: 1,
  updated_at: ISODate("2025-11-19"),
  active: true,
  
  // Configuration data
  feeds: [
    {
      source: "shopify_blog",
      url: "https://www.shopify.com/blog/rss",
      type: "rss",
      enabled: true,
      priority: 1  // For future use
    },
    {
      source: "google_alerts_ecommerce_trends",
      url: "https://www.google.com/alerts/feeds/...",
      type: "rss",
      keyword: "ecommerce trends",
      enabled: true,
      priority: 1
    }
  ]
}
```

#### Collection: `config_topics`
```javascript
{
  _id: ObjectId("..."),
  config_type: "topics",
  version: 1,
  updated_at: ISODate("2025-11-19"),
  active: true,
  
  // Configuration data
  topics: {
    "fashion": ["dress", "clothing", "apparel", ...],
    "beauty_products": ["skincare", "makeup", ...],
    "drinks": ["wine", "beer", "beverage", ...],
    // ... more topics
  }
}
```

### 2. Configuration Manager Module

**File**: `config/config_manager.py`

```python
class ConfigManager:
    """Centralized configuration management."""
    
    def __init__(self):
        self.db = get_db()
        self._cache = {}  # In-memory cache
    
    def get_keywords_config(self) -> Dict:
        """Get active keywords configuration."""
        # Check cache first
        # Load from DB
        # Fallback to file if DB is empty
    
    def get_feeds_config(self) -> Dict:
        """Get active feeds configuration."""
    
    def get_topics_config(self) -> Dict:
        """Get active topics configuration."""
    
    def update_keywords(self, data: Dict) -> bool:
        """Update keywords config in DB."""
    
    def add_feed(self, feed: Dict) -> bool:
        """Add new RSS feed."""
    
    def remove_feed(self, source_name: str) -> bool:
        """Remove/disable RSS feed."""
    
    def add_keyword_term(self, group: str, term: str) -> bool:
        """Add term to group."""
```

### 3. Migration Strategy

#### Phase 1: Dual Mode (Backward Compatible)
- Read from MongoDB **first**
- Fallback to JSON files if DB is empty
- Keep JSON files as defaults/backups
- Zero breaking changes

#### Phase 2: CLI for Config Management
- Add CLI commands to manage configs
- Easy migration from files → DB

#### Phase 3: API Endpoints
- REST API for config CRUD
- Web UI (future)

## 🔄 Implementation Steps

### Step 1: Create Config Manager
✓ Create `config/config_manager.py`
✓ Implement loading with fallback logic
✓ Add caching for performance
✓ Handle versioning

### Step 2: Update Data Sources
✓ Update `sources/google_trends.py` to use ConfigManager
✓ Update `sources/blogs.py` to use ConfigManager
✓ Update `sources/google_alerts.py` to use ConfigManager
✓ Update `processing/topic_tagger.py` to use ConfigManager

### Step 3: Add CLI Commands
✓ `cli.py config init` - Load JSON files into MongoDB
✓ `cli.py config show [keywords|feeds|topics]` - Display configs
✓ `cli.py config add-feed <source> <url>` - Add feed
✓ `cli.py config add-term <group> <term>` - Add keyword
✓ `cli.py config disable-feed <source>` - Disable feed
✓ `cli.py config export` - Export to JSON (backup)

### Step 4: Add API Endpoints
✓ `GET /api/config/keywords` - Get keywords config
✓ `PUT /api/config/keywords` - Update keywords
✓ `GET /api/config/feeds` - List feeds
✓ `POST /api/config/feeds` - Add feed
✓ `DELETE /api/config/feeds/{source}` - Remove feed
✓ `GET /api/config/topics` - Get topics

### Step 5: Migration Script
✓ One-time script to load existing JSON → MongoDB
✓ Validate data integrity
✓ Keep JSON as backup

## ⚠️ Considerations

### Pros ✅
1. **Dynamic Updates**: Change configs without redeploying
2. **Version Control**: Track who changed what and when
3. **Audit Trail**: History of config changes
4. **API Access**: Manage configs via REST API
5. **Validation**: Enforce schema at DB level
6. **Rollback**: Revert to previous versions easily
7. **Multi-Environment**: Different configs per env

### Cons ⚠️
1. **Complexity**: More moving parts
2. **Dependency**: Requires MongoDB connection always
3. **Migration**: Need to migrate existing setups
4. **Testing**: More test coverage needed
5. **Debugging**: Config issues harder to spot
6. **Bootstrapping**: Need seed data mechanism

### Mitigations 🛡️
1. **Fallback**: Always fallback to JSON files
2. **Caching**: Cache configs in memory
3. **Validation**: Strong schema validation
4. **Logging**: Log all config loads/updates
5. **Backup**: Auto-export to JSON periodically
6. **CLI First**: Easy CLI for all operations

## 🎯 Recommended Approach

### Option A: Conservative (Recommended)
1. Keep JSON files as source of truth
2. Load into MongoDB on startup (if empty)
3. ConfigManager reads from DB with JSON fallback
4. Provide CLI to sync JSON → MongoDB
5. API endpoints for viewing only (no editing initially)

**Pros**: Safe, backward compatible, easy rollback
**Cons**: Still need to edit JSON for now

### Option B: Aggressive
1. Migrate all configs to MongoDB immediately
2. Remove JSON files (backup only)
3. All edits via API/CLI
4. MongoDB is single source of truth

**Pros**: Full benefits immediately
**Cons**: Riskier, more to build upfront

## 📊 Effort Estimate

### Small (1-2 hours)
- Config manager with fallback
- Load JSON → MongoDB on startup
- Update sources to use ConfigManager

### Medium (3-4 hours)
- Add basic CLI commands
- API endpoints for viewing
- Testing & validation

### Large (5-6 hours)
- Full CRUD API endpoints
- Versioning & audit trail
- Migration scripts
- Comprehensive testing

## 🚦 My Recommendation

**Start with Option A (Conservative)**:

1. **Phase 1** (1-2 hours):
   - Create ConfigManager with fallback
   - Auto-load JSON → MongoDB on first run
   - Update all sources to use ConfigManager
   - Test everything still works

2. **Phase 2** (1 hour):
   - Add CLI command: `cli.py config sync`
   - Add CLI command: `cli.py config show`
   - Test manual config edits in MongoDB work

3. **Phase 3** (2 hours - optional):
   - Add API endpoints for viewing
   - Add simple CRUD via API
   - Web UI (future)

## 🤔 Questions for You

Before I implement:

1. **Which approach?** Conservative (A) or Aggressive (B)?
2. **Priority?** What config do you change most often?
3. **CLI vs API?** Which do you prefer for editing configs?
4. **Versioning?** Do you want to track who changed what?
5. **Validation?** How strict should config validation be?

Let me know your preferences and I'll implement accordingly! 🚀

