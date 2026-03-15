import os
import sys
import json
import argparse
import requests

BASE_URL = os.getenv("MEMOS_CLOUD_URL", "https://memos.memtensor.cn/api/openmem/v1")
API_KEY = os.getenv("MEMOS_API_KEY")

if not API_KEY:
    print(json.dumps({"error": "Configuration Error", "message": "MEMOS_API_KEY environment variable is not set."}), file=sys.stderr)
    sys.exit(1)

HEADERS = {
    "Authorization": f"Token {API_KEY}",
    "Content-Type": "application/json"
}

def _request(endpoint, data):
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    try:
        response = requests.post(url, headers=HEADERS, json=data, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        err_msg = f"HTTP {e.response.status_code}"
        try:
            err_msg += f" - {e.response.json().get('message', e.response.text)}"
        except ValueError:
            err_msg += f" - {e.response.text}"
        print(json.dumps({"error": "API Error", "message": err_msg, "status_code": e.response.status_code}), file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(json.dumps({"error": "Network Error", "message": str(e)}), file=sys.stderr)
        sys.exit(1)

def search_memory(user_id, query, conversation_id=None):
    payload = {
        "user_id": user_id,
        "query": query
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id
        
    return _request("/search/memory", payload)

def add_message(user_id, conversation_id, messages_json_str):
    try:
        messages = json.loads(messages_json_str)
    except json.JSONDecodeError:
        print(json.dumps({"error": "Validation Error", "message": "messages must be a valid JSON string"}), file=sys.stderr)
        sys.exit(1)
        
    payload = {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "messages": messages
    }
    return _request("/add/message", payload)

def delete_memory(memory_ids_str):
    if not memory_ids_str:
        print(json.dumps({"error": "Validation Error", "message": "memory_ids is required"}), file=sys.stderr)
        sys.exit(1)
        
    payload = {
        "memory_ids": [m.strip() for m in memory_ids_str.split(',')]
    }
    return _request("/delete/memory", payload)

def add_feedback(user_id, conversation_id, feedback_content, allow_knowledgebase_ids=None):
    payload = {
        "user_id": user_id,
        "conversation_id": conversation_id,
        "feedback_content": feedback_content
    }
    if allow_knowledgebase_ids:
        payload["allow_knowledgebase_ids"] = [kb.strip() for kb in allow_knowledgebase_ids.split(',')]
    return _request("/add/feedback", payload)

def main():
    parser = argparse.ArgumentParser(description="MemOS Cloud Server API Client")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Search Memory
    p_search = subparsers.add_parser("search", help="Search memory")
    p_search.add_argument("user_id", help="User ID")
    p_search.add_argument("query", help="Search query string")
    p_search.add_argument("--conversation-id", help="Optional conversation ID")

    # Add Message
    p_add = subparsers.add_parser("add_message", help="Add a message memory")
    p_add.add_argument("user_id", help="User ID")
    p_add.add_argument("conversation_id", help="Conversation ID")
    p_add.add_argument("messages", help="Messages as a JSON string. e.g. '[{\"role\":\"user\",\"content\":\"hello\"}]'")

    # Delete Memory
    p_del = subparsers.add_parser("delete", help="Delete memory")
    p_del.add_argument("memory_ids", help="Comma-separated list of memory IDs to delete (Required)")

    # Add Feedback
    p_fb = subparsers.add_parser("add_feedback", help="Add feedback")
    p_fb.add_argument("user_id", help="User ID")
    p_fb.add_argument("conversation_id", help="Conversation ID")
    p_fb.add_argument("feedback_content", help="Feedback content text")
    p_fb.add_argument("--allow-knowledgebase-ids", help="Comma-separated list of knowledgebase IDs")

    args = parser.parse_args()

    try:
        if args.command == "search":
            result = search_memory(args.user_id, args.query, args.conversation_id)
        elif args.command == "add_message":
            result = add_message(args.user_id, args.conversation_id, args.messages)
        elif args.command == "delete":
            result = delete_memory(args.memory_ids)
        elif args.command == "add_feedback":
            result = add_feedback(args.user_id, args.conversation_id, args.feedback_content, args.allow_knowledgebase_ids)
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"error": "Unexpected Error", "message": str(e)}), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()