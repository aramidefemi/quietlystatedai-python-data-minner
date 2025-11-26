# Bias Filtering System

## The Problem

Vendor blogs naturally exhibit bias when reporting statistics about their product category. For example:

- **Recharge** (subscription platform) → cherry-picks positive subscription/retention stats
- **Klaviyo** (email platform) → highlights exceptional email marketing results
- **Gorgias** (support platform) → showcases impressive customer service metrics

This creates **systematic bias** in the dataset, making insights unreliable.

## The Solution

A configurable bias detection system that filters out data points when:
1. **Source** has known bias (e.g., Recharge)
2. **Topic** matches their product (e.g., subscriptions)
3. **Keywords** indicate their domain (e.g., "LTV", "churn")

## How It Works

### 1. Bias Rules Configuration

Defined in `config/bias_rules.json`:

```json
{
  "rules": [
    {
      "source": "recharge_blog",
      "reason": "Recharge sells subscription software",
      "exclude_topics": ["retention", "subscription"],
      "exclude_keywords": ["subscription", "subscriber", "ltv", "churn"]
    }
  ]
}
```

### 2. Two-Layer Filtering

**Layer 1: Article Ingestion** (`sources/blogs.py`)
- Filters out entire articles if they contain biased keywords
- Saves storage and processing time
- Logs: `"X biased"` articles skipped

**Layer 2: Signal Extraction** (`jobs/extract_signals.py`)
- Filters individual signals by topic + keywords
- Catches any biased signals that slipped through
- Reports: `"X biased signals filtered"`

### 3. BiasChecker Class

Located in `processing/bias_checker.py`:

```python
bias_checker = BiasChecker()

# Check if a data point is biased
is_biased = bias_checker.is_biased(
    source_origin="recharge_blog",
    topic="retention",
    text="subscription rate increased by 23%"
)  # Returns: True
```

## Configuration

### Adding New Bias Rules

Edit `config/bias_rules.json`:

```json
{
  "source": "YOUR_SOURCE_NAME",
  "reason": "Why this source is biased",
  "exclude_topics": ["topic1", "topic2"],
  "exclude_keywords": ["keyword1", "keyword2"]
}
```

### MongoDB Integration

You can also add bias rules to MongoDB (future enhancement):

```bash
python cli.py config add-bias-rule recharge_blog \
  --topics retention,subscription \
  --keywords "subscriber,ltv,churn"
```

## Usage Examples

### Example 1: Recharge Blog

**Article**: "How subscriptions drive 90% LTV growth"

**Filter Action**: ✅ **BLOCKED**
- Source: `recharge_blog`
- Keywords: `"subscription"`, `"ltv"`
- Topic: `retention`

**Result**: Article not saved to database

### Example 2: Klaviyo Blog

**Signal**: "Email revenue up 45% with Klaviyo"

**Filter Action**: ✅ **BLOCKED**
- Source: `klaviyo_blog`
- Topic: `email_sms`
- Keywords: `"email"`, `"klaviyo"`

**Result**: Signal not extracted

### Example 3: Modern Retail (Neutral Source)

**Article**: "Recharge reports subscription growth"

**Filter Action**: ✅ **ALLOWED**
- Source: `modern_retail` (no bias rules)
- Even though it mentions Recharge, Modern Retail is neutral

**Result**: Article saved normally

## Impact

### Storage Savings
- Fewer biased articles stored
- Cleaner signal database
- More reliable insights

### Data Quality
- Eliminates vendor self-promotion
- Reduces cherry-picked statistics
- Increases trust in reports

### Transparency
- Clear logging of filtered content
- Explainable bias rules
- Audit trail in bias_rules.json

## Testing

### Test the bias checker:

```python
from processing.bias_checker import BiasChecker

checker = BiasChecker()

# Test 1: Biased source + topic
result = checker.is_biased(
    source_origin="recharge_blog",
    topic="retention"
)
assert result == True

# Test 2: Biased keywords
result = checker.is_biased(
    source_origin="recharge_blog",
    text="subscription churn decreased by 50%"
)
assert result == True

# Test 3: Neutral source
result = checker.is_biased(
    source_origin="modern_retail",
    topic="retention"
)
assert result == False
```

### Run the ingestion pipeline:

```bash
# Fetch articles with bias filtering
python cli.py fetch-articles

# Expected output:
#   recharge_blog: 2/15 saved (8 no data, 5 biased)

# Extract signals with bias filtering
python cli.py extract-signals

# Expected output:
#   📊 Signal Extraction Summary:
#   Total signals extracted: 45
#   Biased signals filtered: 12
#   New signals saved: 33
#   Bias filter rate: 26.7%
```

## Monitoring

### Check Filter Effectiveness

```bash
# View bias rules
cat config/bias_rules.json

# Check filtered articles count
grep "biased" logs/ingestion.log

# Analyze bias filter rate
python cli.py stats --bias
```

### Adjust Rules

If filter is too aggressive:
- Remove keywords
- Narrow exclude_topics

If filter is too lenient:
- Add more keywords
- Broaden exclude_topics

## Best Practices

1. **Start Conservative**: Add rules only for obvious vendor bias
2. **Monitor Impact**: Check bias filter rate after adding rules
3. **Document Reasons**: Always include a `"reason"` field
4. **Regular Review**: Audit bias rules quarterly
5. **Balance Quality**: Don't filter out all vendor content - they have valuable insights on non-product topics

## Future Enhancements

- [ ] ML-based bias detection (detect patterns automatically)
- [ ] Confidence scores (0-100% biased)
- [ ] Bias rule suggestions (auto-detect vendor topics)
- [ ] MongoDB-backed rules (dynamic updates)
- [ ] Bias analytics dashboard
- [ ] Per-article bias explanations

## Status

✅ **Implemented and Active**
- Bias rules configured for Recharge, Klaviyo, Gorgias
- Article-level filtering in blogs ingestion
- Signal-level filtering in extraction
- Logging and statistics

**Next**: Add more vendor-specific rules as needed

