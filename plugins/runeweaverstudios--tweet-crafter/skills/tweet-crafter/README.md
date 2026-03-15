# Tweet Crafter for OpenClaw

This OpenClaw skill helps you draft compelling tweets and accompanying blog posts about your OpenClaw projects and journey. It's designed to ensure your social media presence is impactful and consistent.

## Features

-   **Automated Tweet Drafting**: Provide a prompt, and the skill will craft an engaging tweet.
-   **ClawHub Link Integration**: Easily include links to your ClawHub skills.
-   **Companion Blog Post**: Get a full blog post to expand on your tweet's announcement.
-   **Copy-Paste Ready Output**: Tweets are presented in markdown code blocks for easy sharing.

## Installation

To install this skill:

1.  Clone this repository into your OpenClaw workspace.
2.  Ensure you have Agent Swarm (workspace/skills/agent-swarm or clawhub install agent-swarm) configured and enabled for intelligent LLM routing. (Update clawhub link when new ClawHub instance is live.)

## Usage

Use the `tweet_crafter.draft_content` command. For example:

```python
tweet_crafter.draft_content(
    tweet_prompt="Draft a tweet about my new skill!",
    blog_context="My new skill automates X and Y, saving users Z time.",
    skill_name="MyNewSkill",
    clawhub_link="https://clawhub.ai/YourOrg/mynewskill",
    mentions=["@YourFriend", "@OpenClawAI"],
    hashtags=["#CoolSkill", "#Automation"]
)
```
