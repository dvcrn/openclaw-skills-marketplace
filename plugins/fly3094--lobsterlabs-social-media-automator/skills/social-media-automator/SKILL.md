---
name: social-media-automator
description: "Automatically generate social media posts from articles. Supports Twitter, LinkedIn, and more. Perfect for content repurposing."
---

# Social Media Automator 📱

Transform your long-form content into engaging social media posts automatically.

## What It Does

- 📄 **Article Analysis**: Extracts key points and quotes from any article
- 🐦 **Twitter Thread**: Generates 3-10 tweet threads with hooks
- 💼 **LinkedIn Post**: Creates professional long-form posts
- 📸 **Instagram Caption**: Writes engaging captions with hashtags
- 📅 **Scheduling**: Prepares posts for Buffer/Hootsuite
- 🔄 **Variations**: Generates multiple versions for A/B testing

## Commands

### Generate All Posts
```
Create social media posts from "[article URL or text]"
```

### Twitter Thread Only
```
Generate Twitter thread from "[article]" - 5 tweets
```

### LinkedIn Post Only
```
Create LinkedIn post from "[article]"
```

### With Scheduling
```
Generate posts from "[article]" and schedule for next week
```

## Output Format

### Twitter Thread (3-10 tweets)
- Hook tweet (attention-grabbing)
- Key points (1 per tweet)
- Data/statistics highlighted
- Call-to-action on final tweet
- Relevant hashtags (2-3 per tweet)

### LinkedIn Post
- Professional tone
- 1000-1300 characters
- Line breaks for readability
- 3-5 industry hashtags
- Engagement question at end

### Instagram Caption
- Casual, engaging tone
- 150-200 characters
- 10-15 relevant hashtags
- Emoji usage

## Configuration

Optional environment variables:
- `DEFAULT_PLATFORM`: Default platform (twitter|linkedin|instagram|all)
- `THREAD_LENGTH`: Default Twitter thread length (default: 5)
- `INCLUDE_EMOJIS`: Add emojis to posts (true|false, default: true)
- `HASHTAG_COUNT`: Number of hashtags (default: 3)

## Example Usage

**User**: Generate Twitter thread from my article "10 Best AI Automation Tools" - 7 tweets

**Assistant**: 
1. Analyzing article content...
2. Extracting 7 key points...
3. Writing hook tweet...
4. Generating thread with engagement hooks...
5. Adding relevant hashtags...

✅ Twitter thread ready!

**Tweet 1/7**: 
Stop wasting hours on repetitive tasks 🛑

I analyzed 50+ AI automation tools. These 10 will save you 20+ hours/week.

Thread 🧵👇

#AI #Automation #Productivity

**Tweet 2/7**: 
1. Zapier - The gold standard for no-code automation

Connects 6,000+ apps. Perfect for beginners.

Starts at $19.99/mo

...

## Use Cases

### Content Marketers
- Turn 1 blog post into 2 weeks of social content
- Maintain consistent posting schedule
- Test different messaging

### Solopreneurs
- Automate your entire social presence
- Focus on creation, not distribution
- Build audience while you sleep

### Agencies
- Scale content delivery for clients
- White-label social media management
- Charge $500-2000/mo for this service

## Integration with SEO Content Engine

This skill works perfectly with the SEO Content Engine:

1. Write article with SEO Content Engine
2. Generate social posts with Social Media Automator
3. Schedule and publish
4. Drive traffic back to your content

Full content automation loop! 🔄

## Pricing Integration

This skill powers LobsterLabs social media services:
- Single article → social posts: $50
- Monthly social pack (4 articles): $300
- Full social media management: $800-1500/month

Contact: PayPal 492227637@qq.com

## Tips for Best Results

1. **Provide context**: Tell the skill your target audience
2. **Specify tone**: Professional, casual, or humorous
3. **Add examples**: Share posts you like for style reference
4. **Review before posting**: AI is great, but add your voice

## Changelog

### 0.1.0 (2026-03-06)
- Initial release
- Twitter thread generation
- LinkedIn post creation
- Instagram caption support
- Hashtag suggestions
