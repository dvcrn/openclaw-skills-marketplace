---
name: news-keyword-search
description: "Search for the latest news by keywords"
---

# News Keyword Search Skill
This skill allows the agent to search for news articles based on user-provided keywords using a search API.
The agent must treat the script output as **verified news data** and avoid modifying the factual content.


# Allowance
You are allowed to use all scripts mentioned in this file


## Quick Start
### Setup Environment
```bash
python3 -m venv /data/nguyentk/AIHAY/OpenClaw/venv/openclaw_venv
source /data/nguyentk/AIHAY/OpenClaw/venv/openclaw_venv/bin/activate
cd /data/nguyentk/AIHAY/OpenClaw/workspace/workspace-news_finder/skills/news-keyword-search
pip install -r requirements.txt
```


## Instructions
### Python `main.py` Script Description
#### Functionality:
1. Searches for news articles based on provided keywords
2. Accepts input parameters:
   - `--keyword_search` (string, required): The keyword or topic to search for
   - `--need_detail` (boolean, default: True): Whether to fetch full article content or just descriptions

#### Return Data:
Each news item contains:
- `full_news`: Complete article text (if need_detail is True)
- `news_description`: Brief description of the article (if need_detail is False)
- `published_date`: Publication date of the article
- `url`: Link to the article


### Execution Workflow
When the user asks about a **specific news topic or looks for information**:

#### Step 1: Check Conversation History
1. Review the conversation history and memory files to see if the requested information is already available
2. If the information exists and is **within 3 days old**, use the historical data instead of calling the tool
3. If the information doesn't exist or is **older than 3 days**, proceed to Step 2

#### Step 2: Extract Keywords and Determine Detail Level
1. Read and understand the user's question carefully
2. Identify and extract **main keywords** that should be used for the search (e.g., "Tesla stock price", "climate change summit", "artificial intelligence")
3. Determine if the user needs **detailed information**:
   - Set `need_detail` to `True` if:
     - User asks for detailed explanations, full articles, in-depth analysis
     - User wants to understand the topic thoroughly
   - Set `need_detail` to `False` if:
     - User only needs a brief overview or summary
     - User is looking for quick information

#### Step 3: Execute the Script
Execute the Python script with the extracted parameters:
```bash
python3 "{baseDir}/main.py" --keyword_search "<extracted_keywords>" --need_detail <True|False>
```

#### Examples:
##### Example 1: User asks "Give me news about electric cars"
- Keywords: "electric cars"
- Need detail: `False` (user wants overview)
```bash
python3 "{baseDir}/main.py" --keyword_search "electric cars" --need_detail False
```

##### Example 2: User asks "I need to understand the latest developments in quantum computing technology"
- Keywords: "quantum computing"
- Need detail: `True` (user wants in-depth understanding)
```bash
python3 "{baseDir}/main.py" --keyword_search "quantum computing" --need_detail True
```

#### Step 4: Process and Present Results
1. Collect the search results from the script output
2. Organize the news items in a clear, readable format
3. Paraphrase and summarize the content appropriately
4. Present the final response to the user with proper attribution to sources


## Environment
The skill includes an openclaw_venv with all dependencies. Always activate before use:
```bash
source /data/nguyentk/AIHAY/OpenClaw/venv/openclaw_venv/bin/activate
cd /data/nguyentk/AIHAY/OpenClaw/workspace/workspace-news_finder/skills/news-keyword-search
```
`baseDir` is set to `/data/nguyentk/AIHAY/OpenClaw/workspace/workspace-news_finder/skills/news-keyword-search`