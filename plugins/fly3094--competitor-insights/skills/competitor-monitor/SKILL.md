---
name: competitor-monitor
description: "Monitor competitors automatically: track pricing changes, new features, marketing campaigns, and get AI-powered insights. Never miss competitive moves."
---

# Competitor Monitor 👁️

Automatically track your competitors' moves: pricing changes, new features, marketing campaigns, and get AI-powered competitive intelligence.

## What It Does

- 💰 **Price Tracking**: Monitor competitor pricing changes
- 🚀 **Feature Detection**: Get alerted on new features
- 📢 **Marketing Intelligence**: Track campaigns and messaging
- 📊 **Comparison Reports**: Side-by-side competitor analysis
- ⚠️ **Smart Alerts**: Get notified on important changes
- 🤖 **AI Insights**: Understand competitive threats and opportunities

## Installation

```bash
clawhub install competitor-monitor
```

## Commands

### Add Competitor
```
Add competitor: https://competitor.com
Name: Competitor Inc
Industry: SaaS
```

### Start Monitoring
```
Start monitoring all competitors
```

### Get Report
```
Generate competitor analysis report for last week
```

### Price Comparison
```
Compare pricing across all competitors
```

### Feature Tracker
```
Show new features launched by competitors this month
```

### Market Insights
```
What are the key competitive trends in my market?
```

## Configuration

### Environment Variables

```bash
# Monitoring interval
export MONITOR_INTERVAL_HOURS="24"

# Alert method
export ALERT_METHOD="email"  # email|telegram|slack

# What to track
export TRACK_PRICING="true"
export TRACK_FEATURES="true"
export TRACK_MARKETING="true"

# Alert settings
export EMAIL_ADDRESS="your@email.com"
export TELEGRAM_BOT_TOKEN="your_bot_token"
export SLACK_WEBHOOK_URL="your_webhook_url"
```

### Competitor List

Create `competitors.json`:
```json
{
  "competitors": [
    {
      "name": "Competitor A",
      "url": "https://competitor-a.com",
      "pricing_url": "https://competitor-a.com/pricing",
      "industry": "SaaS",
      "size": "medium"
    },
    {
      "name": "Competitor B",
      "url": "https://competitor-b.com",
      "pricing_url": "https://competitor-b.com/pricing",
      "industry": "SaaS",
      "size": "large"
    }
  ]
}
```

## Output Examples

### Weekly Competitor Report
```
📊 Competitor Intelligence Report
Week of Mar 1-7, 2026

🔍 Key Changes This Week:

[Competitor A]
• Pricing: Basic plan increased from $29 to $39 (+34%)
• New Feature: AI-powered analytics dashboard
• Marketing: Launched "Spring Sale" campaign

[Competitor B]
• Pricing: No changes
• New Feature: Mobile app update (v3.2)
• Marketing: New case study published

📈 Price Comparison:

Service          You    Comp A    Comp B    Market Avg
Basic Plan      $29    $39       $25       $31
Pro Plan        $79    $99       $69       $82
Enterprise     $199   $249      $179      $209

💡 AI Insights:

1. Competitor A's price increase creates opportunity
   - They're positioning as premium
   - You can capture price-sensitive customers

2. AI analytics trend growing
   - 2/3 competitors now offer AI features
   - Consider accelerating AI roadmap

3. Mobile experience gap
   - Competitor B improved mobile app
   - Your mobile experience needs attention

🎯 Recommended Actions:

1. Launch "Competitor A Switch" campaign
   - Target their priced-out customers
   - Offer migration assistance

2. Accelerate AI feature development
   - Match or exceed their AI capabilities
   - Highlight your unique AI advantages

3. Prioritize mobile improvements
   - Schedule mobile UX audit
   - Plan Q2 mobile updates
```

### Price Alert
```
⚠️ Price Change Alert!

Competitor: Competitor A
Change: Basic plan $29 → $39 (+34%)
Effective: March 5, 2026

Impact Analysis:
• They're now 34% more expensive than you
• Opportunity to capture price-sensitive customers
• Consider "Price Lock" promotion

Suggested Action:
Launch campaign targeting their customers with:
- Special migration discount
- Price comparison landing page
- Case studies showing better value
```

### Feature Tracking
```
🚀 New Features Detected

[Competitor A] - March 3, 2026
Feature: AI-Powered Analytics Dashboard
Description: "Get instant insights from your data with AI"
Impact: HIGH
Your Status: In Development (Q2 release)

[Competitor B] - March 1, 2026
Feature: Mobile App v3.2
Description: "Improved performance and new UI"
Impact: MEDIUM
Your Status: Planned (Q3 release)

📊 Feature Comparison:

Feature              You    Comp A    Comp B
AI Analytics        🟡     ✅        ❌
Mobile App          ✅     ✅        ✅
API Access          ✅     ✅        ✅
SSO                 ✅     ❌        ✅
Custom Reports      ✅     ✅        ❌

Legend: ✅ Available  🟡 In Dev  ❌ Not Available
```

## Monitoring Capabilities

### What We Track

**Pricing:**
- Plan prices and changes
- Discount offers
- Free trial terms
- Enterprise pricing

**Features:**
- New feature announcements
- Product updates
- Feature deprecations
- API changes

**Marketing:**
- Website messaging changes
- New landing pages
- Ad campaigns
- Content marketing

**Company:**
- Funding announcements
- Team changes
- Press releases
- Job postings

### How It Works

1. **Web Scraping**: Monitor competitor websites
2. **RSS Feeds**: Track blogs and announcements
3. **Social Media**: Monitor Twitter, LinkedIn
4. **News Alerts**: Google Alerts integration
5. **AI Analysis**: Understand impact and trends

## Integration with Other Skills

### social-insights
```
Competitor social media performance
→ Compare engagement rates
→ Identify successful strategies
```

### seo-content-pro
```
Competitor content analysis
→ Identify content gaps
→ Generate better content
```

### email-automation
```
Competitor email campaigns
→ Track their email strategy
→ Get alerts on new campaigns
```

## Use Cases

### Startup vs Enterprise
- Track enterprise competitors' moves
- Identify market opportunities
- Position as agile alternative

### SaaS Companies
- Monitor pricing changes
- Track feature releases
- Compare growth metrics

### E-commerce
- Track competitor pricing
- Monitor promotions
- Analyze product launches

### Agencies
- Monitor competitor services
- Track pricing changes
- Identify service gaps

## Pricing Integration

This skill powers LobsterLabs competitive intelligence:
- **Basic Monitoring:** $299/month (up to 5 competitors)
- **Professional:** $599/month (up to 15 competitors)
- **Enterprise:** $1,499/month (unlimited competitors)

Contact: PayPal 492227637@qq.com

## Tips for Best Results

1. **Start Small**: Monitor 3-5 key competitors first
2. **Set Clear Goals**: What intelligence matters most?
3. **Review Weekly**: Make competitor analysis a habit
4. **Act on Insights**: Intelligence without action is useless
5. **Stay Ethical**: Monitor public info only

## Troubleshooting

### No Data Collected
- Verify competitor URLs are correct
- Check internet connection
- Ensure monitoring interval has passed

### Alerts Not Working
- Verify alert method configuration
- Check email/Telegram/Slack settings
- Test alert system

### Inaccurate Pricing
- Some sites use dynamic pricing
- Verify with manual check
- Report issues for improvement

## Changelog

### 1.0.0 (2026-03-07)
- Initial release
- Price tracking
- Feature detection
- Marketing monitoring
- AI-powered insights
- Smart alerts
- Weekly reports
