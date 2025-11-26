# Social Media Post Generator

## Overview

Transform your trend insights into engaging social media content. This feature helps you create data-driven posts similar to @databutmakeittipsy - punchy, contextual, and backed by real statistics.

## What Makes Great Data Posts?

Looking at successful accounts like @databutmakeittipsy, we identified the key ingredients:

1. **Hook Headline**: Surprising or counterintuitive statement
   - Example: "gen z isn't drinking less because it's cool... it's because they're broke"

2. **Hard Data**: Specific statistics that prove the point
   - Example: "62% of under-35s drink, vs 72% 20 years ago"

3. **Context Layer**: The "why" behind the numbers
   - Example: Links to rent prices, student debt, $19 cocktails

4. **Actionable Insight**: What this means for your audience
   - Example: "brands better rethink their happy hour strategy"

5. **Casual Tone**: Meme-adjacent, relatable, not corporate
   - Example: "plot twist: gen z drinking less because they're broke"

## How It Works

### Data Sources

The generator pulls from your QuietlyStated database:
- **Stats**: Quantifiable data points from articles
- **Trends**: Google Trends weekly changes
- **Signals**: Extracted entity + metric combinations
- **Topics**: Categorized insights (fashion, drinks, dtc, etc.)

### Post Structure

**Multi-Slide Format** (Instagram/LinkedIn carousel):

**Slide 1: Hook**
- Bold statement that stops the scroll
- Counterintuitive or surprising angle
- Sets up the story

**Slide 2: The Stats**
- Key numbers and data points
- Visual data representation
- Compare "then vs now" or "this vs that"

**Slide 3: The Context**
- Why is this happening?
- What's driving this trend?
- The bigger picture

**Slide 4: The Takeaway**
- "What now?" for your audience
- Actionable insight
- Strategic implications

## Features

### 1. Post Generation Engine

```bash
python cli.py social generate --topic drinks --days 7
```

**What it does:**
- Pulls top signals from the past 7 days
- Identifies the most interesting stat + context combos
- Formats into 4-slide post structure
- Outputs draft copy

**Output example:**
```
📊 POST DRAFT: Gen Z Drinking Trends

Slide 1 (Hook):
"plot twist: gen z isn't drinking less because it's cool"

Slide 2 (Stats):
the stats:
• 62% of under-35s drink vs 72% in 2003
• alcohol sales up overall
• but gen z said "not with my rent prices"

Slide 3 (Context):
between entry-level jobs, student debt, and $19 cocktails,
the real buzzkill is the cost.

Slide 4 (Takeaway):
what now?
brands better rethink their happy hour strategy - more
chill, less chug. lower abv, cuter labels, and budget-
friendly bottles = the vibe.
```

### 2. Tone Matching (LLM Integration)

Uses Claude API to rewrite in your brand voice:
- Analyzes example posts you provide
- Matches tone, structure, and style
- Maintains data accuracy while adjusting voice

### 3. Topic Filters

Generate posts by topic:
```bash
# Fashion trends
python cli.py social generate --topic fashion

# DTC/ecommerce insights
python cli.py social generate --topic dtc

# Payment/checkout trends
python cli.py social generate --topic payment
```

### 4. Review Workflow

**Simple Web Dashboard** for your social media manager:
- View generated drafts
- Edit copy
- Approve for posting
- Export to Canva templates

### 5. Scheduling Integration

**Optional connections:**
- Buffer API
- Later API  
- Instagram Graph API
- Manual export (CSV/JSON)

## Usage Workflow

### For Your Social Media Manager

**Monday Morning Routine:**

1. **Generate Weekly Posts**
   ```bash
   python cli.py social generate --days 7 --count 5
   ```
   Outputs 5 post drafts based on the week's top insights

2. **Review Drafts**
   - Open the web dashboard (or review JSON files)
   - Edit headlines, adjust tone
   - Verify data accuracy

3. **Design in Canva**
   - Export approved copy
   - Use Canva templates for consistent branding
   - Add visual data charts

4. **Schedule**
   - Buffer/Later for posting schedule
   - Or direct publish via Instagram

**Time Saved:**
- ❌ Before: 4-6 hours researching trends + finding stats
- ✅ After: 1-2 hours reviewing + editing generated drafts

## Implementation Roadmap

### Phase 1: Core Engine (Week 1)
- [ ] `social/post_generator.py` module
- [ ] Template system for post structure
- [ ] CLI command: `social generate`
- [ ] Pull top signals by topic
- [ ] Format into 4-slide copy

### Phase 2: LLM Integration (Week 2)
- [ ] Claude API integration
- [ ] Few-shot prompt with example posts
- [ ] Tone matching algorithm
- [ ] A/B test different styles

### Phase 3: Review Interface (Week 3)
- [ ] Simple web dashboard (Flask/FastAPI)
- [ ] Edit/approve workflow
- [ ] Export formats (JSON, CSV, Markdown)
- [ ] Canva template generator

### Phase 4: Automation (Week 4)
- [ ] Auto-generate on schedule (Monday AM)
- [ ] Slack/email notifications
- [ ] Buffer/Later API integration
- [ ] Analytics tracking (which posts perform)

## Configuration

### Style Guide

Create `config/social_style.json`:

```json
{
  "tone": "casual_witty",
  "max_slides": 4,
  "stat_format": "bullets",
  "include_sources": false,
  "emoji_level": "minimal",
  "templates": [
    {
      "name": "stat_shock",
      "structure": ["surprising_hook", "data", "context", "action"]
    },
    {
      "name": "compare_contrast", 
      "structure": ["comparison_hook", "side_by_side_data", "why_different", "takeaway"]
    }
  ]
}
```

### Example Posts Library

Store successful post examples in `config/post_examples/`:
- Used for few-shot learning
- Tone matching reference
- Structure templates

## CLI Commands

```bash
# Generate 3 posts from this week's top insights
python cli.py social generate --days 7 --count 3

# Generate posts for specific topic
python cli.py social generate --topic drinks --count 2

# Preview without saving
python cli.py social preview --topic fashion

# List available topics
python cli.py social topics

# Show recent stats (for manual post creation)
python cli.py social stats --topic dtc --days 7
```

## Advanced Features

### Custom Templates

Create your own post templates:

```python
# social/templates/custom_template.py

def stat_shock_template(signal, context):
    """Surprising stat that challenges assumptions"""
    return {
        "slide_1": f"plot twist: {signal.entity} isn't {assumption}",
        "slide_2": format_stats(signal),
        "slide_3": explain_context(context),
        "slide_4": f"what now?\n{actionable_takeaway(signal)}"
    }
```

### Multi-Region Support

Generate posts for different markets:
```bash
# US market focus
python cli.py social generate --region US --topic fashion

# Nigerian market
python cli.py social generate --region NG --topic dtc
```

### Competitor Tracking

Compare your insights to competitor posts:
- Track what topics they're covering
- Identify gaps in your content
- Benchmark engagement

## Best Practices

1. **Always Verify Data**: Auto-generated posts should be reviewed by a human
2. **Update Templates**: Refresh every quarter as social trends evolve
3. **Test Different Tones**: A/B test casual vs professional
4. **Cite When Needed**: For sensitive topics, include source attribution
5. **Visual Consistency**: Use the same Canva template set

## Privacy & Ethics

- All data is from public sources
- Statistics are factual, not manipulated
- Context is preserved (no cherry-picking)
- Sources available on request

## FAQ

**Q: Will this replace my social media manager?**  
A: No - it augments their workflow. They still do strategy, editing, visual design, and community management. This handles the time-consuming research phase.

**Q: Can I customize the tone?**  
A: Yes! Provide example posts and the LLM adapts to your brand voice.

**Q: What if the generated post is wrong?**  
A: Always review before posting. The system pulls from verified sources, but context matters.

**Q: Can I generate posts in other languages?**  
A: Phase 2 will support multi-language generation based on region configs.

**Q: How do I measure success?**  
A: Track which topics/formats get the most engagement, then tune the generator to prioritize those patterns.

## Next Steps

1. Review this plan - does it match your needs?
2. Build Phase 1 (core engine + CLI)
3. Test with your social media manager
4. Iterate based on feedback
5. Add LLM integration for tone matching

---

**Ready to build this?** Let me know if you want to adjust the plan or start implementation!

