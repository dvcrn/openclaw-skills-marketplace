---
name: tweet-crafter
description: "Drafts engaging tweets in copy-paste friendly code blocks and generates companion blog posts for various OpenClaw projects and announcements. Integrates with Agent Swarm and enforces ClawHub link best practices."
---

# Tweet Crafter for OpenClaw

## Description

Drafts engaging tweets in copy-paste friendly code blocks and generates companion blog posts for various OpenClaw projects and announcements. Integrates with Agent Swarm and enforces ClawHub link best practices.

# Tweet Crafter Skill

This skill streamlines the process of creating social media content, specifically tweets, and accompanying blog posts for your OpenClaw projects and journey. It ensures tweets are formatted for easy sharing, adheres to character limits, and intelligently links to relevant resources (like ClawHub skill pages).


## Usage

This skill will expose one primary function:

- `tweet_crafter.draft_content(tweet_prompt: str, blog_context: str, skill_name: str = None, github_repo: str = None, clawhub_link: str = None, mentions: list = [], hashtags: list = [], character_limit: int = 280) -> dict`:
    Drafts a tweet and a companion blog post. Requires a `tweet_prompt` and `blog_context`. Optionally takes `skill_name`, `github_repo`, `clawhub_link`, `mentions`, and `hashtags`.
    Returns a dictionary with the drafted tweet (as a string in a code block) and the blog post content.


## Commands

This section would detail direct OpenClaw CLI commands to invoke the skill's functions. These will be implemented in `scripts/tweet_crafter.py`.


## Purpose

To automate and standardize the creation of marketing and update content for OpenClaw skills and projects, making it easy to share your progress and achievements across social media and blogs.


## Features

-   **Intelligent Tweet Drafting**: Leverages Agent Swarm to craft engaging and concise tweets.
-   **Code Block Output**: Presents drafted tweets in a code block for easy copy-pasting, preventing formatting issues.
-   **ClawHub Link Enforcement**: Automatically includes ClawHub links for skills where applicable.
-   **Companion Blog Post Generation**: Creates a short blog post to expand on the tweet's announcement.
-   **Customizable Content**: Allows specification of mentions, hashtags, and context.


## Configuration (`config.json`)

This skill might have configuration options for default tweet lengths, common hashtags, or even preferred LLMs for drafting if not handled directly by Agent Swarm. (Currently empty, can be extended.)
