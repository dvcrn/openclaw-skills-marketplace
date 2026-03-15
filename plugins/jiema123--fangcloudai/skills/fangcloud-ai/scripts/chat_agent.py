#!/usr/bin/env python3
import os
import json
import urllib.request
import urllib.error
import sys
import argparse
import time
import random

def get_token():
    return os.environ.get("FANGCLOUD_USER_TOKEN")

def chat_agent(message, 
               agent_id=None, 
               session_id=None, 
               chat_type="ZSH_CHAT", 
               library_ids=None,
               stream=True):
    """
    General purpose function to chat with Fangcloud AI Agent.
    """
    token = get_token()
    if not token:
        raise ValueError("FANGCLOUD_USER_TOKEN not found in environment.")

    if not session_id:
        session_id = f"{int(time.time())}_{random.randint(1000, 9999)}"

    url = "https://open.fangcloud.com/api/v2/knowledge/chatStream"
    
    # Construct payload
    payload = {
        "messages": [{"role": "user", "content": message}],
        "sessionId": session_id,
        "chatType": chat_type
    }
    
    if agent_id:
        payload["knowledgeGptId"] = agent_id
    elif chat_type == "AI_LIBRARY" and library_ids:
        payload["libraryIds"] = library_ids
        payload["search"] = "true"
        payload["gptType"] = "deepseek"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    req = urllib.request.Request(
        url, 
        data=json.dumps(payload).encode('utf-8'), 
        headers=headers, 
        method="POST"
    )

    full_content = ""
    try:
        with urllib.request.urlopen(req) as response:
            for line in response:
                line = line.decode('utf-8').strip()
                if line.startswith("data:"):
                    line_data = line[5:].strip()
                    if not line_data or line_data == "[DONE]":
                        continue
                    try:
                        content_json = json.loads(line_data)
                        delta = content_json.get("choices", [{}])[0].get("delta", {})
                        if "content" in delta:
                            chunk = delta["content"]
                            full_content += chunk
                            if stream:
                                print(chunk, end="", flush=True)
                    except Exception:
                        continue
    except urllib.error.HTTPError as e:
        error_msg = e.read().decode('utf-8')
        print(f"\nHTTP Error: {e.code} {e.reason}\n{error_msg}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        return None

    if stream:
        print()
    return full_content

def main():
    parser = argparse.ArgumentParser(description="Chat with Fangcloud AI Agent.")
    parser.add_argument("message", help="The message to send to the agent")
    parser.add_argument("--agent-id", default="3776", help="Target Agent ID (default: 3776)")
    parser.add_argument("--session-id", help="Session ID for continuous conversation")
    parser.add_argument("--type", choices=["ZSH_CHAT", "AI_LIBRARY"], default="ZSH_CHAT", help="Chat Type")
    parser.add_argument("--libs", help="Comma separated Library IDs (for AI_LIBRARY type)")
    parser.add_argument("--no-stream", action="store_false", dest="stream", help="Disable streaming output")

    args = parser.parse_args()

    library_ids = args.libs.split(",") if args.libs else None
    
    chat_agent(
        message=args.message,
        agent_id=args.agent_id if args.type == "ZSH_CHAT" else None,
        session_id=args.session_id,
        chat_type=args.type,
        library_ids=library_ids,
        stream=args.stream
    )

if __name__ == "__main__":
    main()
