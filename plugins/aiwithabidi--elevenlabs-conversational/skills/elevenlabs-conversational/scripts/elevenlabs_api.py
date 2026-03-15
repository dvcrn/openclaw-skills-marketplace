#!/usr/bin/env python3
"""ElevenLabs Conversational AI integration for OpenClaw agents."""

import argparse
import json
import os
import sys
from urllib.request import Request, urlopen
from urllib.error import HTTPError

BASE_URL = "https://api.elevenlabs.io/v1"


def get_api_key():
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        print("Error: ELEVENLABS_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return key


def api_request(endpoint, method="GET", data=None, binary=False):
    url = f"{BASE_URL}{endpoint}"
    headers = {"xi-api-key": get_api_key()}
    body = None
    if data is not None:
        if isinstance(data, bytes):
            body = data
        else:
            headers["Content-Type"] = "application/json"
            body = json.dumps(data).encode()

    req = Request(url, data=body, headers=headers, method=method)
    try:
        with urlopen(req) as resp:
            if binary:
                return resp.read()
            return json.loads(resp.read().decode())
    except HTTPError as e:
        err = e.read().decode() if e.fp else ""
        print(f"API Error {e.code}: {err}", file=sys.stderr)
        sys.exit(1)


def resolve_voice_id(name_or_id):
    """Resolve voice name to voice ID."""
    voices = api_request("/voices")
    for v in voices.get("voices", []):
        if v["voice_id"] == name_or_id or v["name"].lower() == name_or_id.lower():
            return v["voice_id"]
    print(f"Error: Voice '{name_or_id}' not found. Use 'voices' command to list.", file=sys.stderr)
    sys.exit(1)


def cmd_voices(args):
    data = api_request("/voices")
    voices = data.get("voices", [])
    if not voices:
        print("No voices found.")
        return
    for v in voices:
        labels = v.get("labels", {})
        lang = labels.get("language", "?")
        cat = v.get("category", "?")
        print(f"  {v['name']} | ID: {v['voice_id']} | Category: {cat} | Language: {lang}")


def cmd_tts(args):
    voice_id = resolve_voice_id(args.voice)
    body = {
        "text": args.text,
        "model_id": args.model,
        "voice_settings": {
            "stability": args.stability,
            "similarity_boost": args.similarity,
            "style": args.style,
            "use_speaker_boost": True,
        },
    }
    audio = api_request(f"/text-to-speech/{voice_id}", method="POST", data=body, binary=True)
    with open(args.output, "wb") as f:
        f.write(audio)
    print(f"  Audio saved to {args.output} ({len(audio)} bytes)")


def cmd_tts_stream(args):
    voice_id = resolve_voice_id(args.voice)
    body = {
        "text": args.text,
        "model_id": args.model,
        "voice_settings": {
            "stability": args.stability,
            "similarity_boost": args.similarity,
            "style": args.style,
        },
    }
    url = f"{BASE_URL}/text-to-speech/{voice_id}/stream"
    headers = {"xi-api-key": get_api_key(), "Content-Type": "application/json"}
    req = Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
    try:
        with urlopen(req) as resp, open(args.output, "wb") as f:
            total = 0
            while True:
                chunk = resp.read(8192)
                if not chunk:
                    break
                f.write(chunk)
                total += len(chunk)
        print(f"  Streamed audio saved to {args.output} ({total} bytes)")
    except HTTPError as e:
        print(f"API Error {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


def cmd_list_agents(args):
    data = api_request("/convai/agents")
    agents = data.get("agents", [])
    if not agents:
        print("  No conversational AI agents found.")
        return
    for a in agents:
        print(f"  {a.get('name','?')} | ID: {a.get('agent_id','?')} | Status: {a.get('status','?')}")


def cmd_create_agent(args):
    body = {
        "name": args.name,
        "conversation_config": {
            "agent": {
                "prompt": {"prompt": args.prompt or "You are a helpful assistant."},
                "first_message": args.first_message or "Hello! How can I help you?",
                "language": args.language,
            },
            "tts": {
                "voice_id": resolve_voice_id(args.voice) if args.voice else None,
            },
        },
    }
    # Remove None voice_id
    if body["conversation_config"]["tts"]["voice_id"] is None:
        del body["conversation_config"]["tts"]

    result = api_request("/convai/agents/create", method="POST", data=body)
    print(f"  Agent created: {result.get('agent_id', 'N/A')}")
    print(json.dumps(result, indent=2))


def cmd_get_agent(args):
    result = api_request(f"/convai/agents/{args.agent_id}")
    print(json.dumps(result, indent=2))


def cmd_clone_voice(args):
    import email.mime.multipart
    import io
    import uuid

    boundary = uuid.uuid4().hex
    parts = []

    # Name field
    parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="name"\r\n\r\n{args.name}')
    if args.description:
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="description"\r\n\r\n{args.description}')

    # File fields
    for filepath in args.files:
        filename = os.path.basename(filepath)
        with open(filepath, "rb") as f:
            file_data = f.read()
        file_b64 = file_data  # We need raw bytes
        parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="files"; filename="{filename}"\r\nContent-Type: audio/mpeg\r\n\r\n')

    # Build multipart body manually
    body = b""
    for i, part in enumerate(parts):
        body += part.encode()
        # If this is a file part, append file data
        if 'filename="' in part:
            idx = parts.index(part)
            filepath = args.files[idx - (2 if args.description else 1)]
            with open(filepath, "rb") as f:
                body += f.read()
        body += b"\r\n"
    body += f"--{boundary}--\r\n".encode()

    url = f"{BASE_URL}/voices/add"
    req = Request(url, data=body, headers={
        "xi-api-key": get_api_key(),
        "Content-Type": f"multipart/form-data; boundary={boundary}",
    }, method="POST")
    try:
        with urlopen(req) as resp:
            result = json.loads(resp.read().decode())
            print(f"  Voice cloned: {result.get('voice_id', 'N/A')}")
    except HTTPError as e:
        print(f"API Error {e.code}: {e.read().decode()}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="ElevenLabs Conversational AI")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("voices", help="List voices")

    p_tts = sub.add_parser("tts", help="Text to speech")
    p_tts.add_argument("text")
    p_tts.add_argument("--voice", default="Rachel")
    p_tts.add_argument("--output", default="output.mp3")
    p_tts.add_argument("--model", default="eleven_multilingual_v2")
    p_tts.add_argument("--stability", type=float, default=0.5)
    p_tts.add_argument("--similarity", type=float, default=0.75)
    p_tts.add_argument("--style", type=float, default=0.0)

    p_tts_s = sub.add_parser("tts-stream", help="Streaming TTS")
    p_tts_s.add_argument("text")
    p_tts_s.add_argument("--voice", default="Rachel")
    p_tts_s.add_argument("--output", default="output.mp3")
    p_tts_s.add_argument("--model", default="eleven_multilingual_v2")
    p_tts_s.add_argument("--stability", type=float, default=0.5)
    p_tts_s.add_argument("--similarity", type=float, default=0.75)
    p_tts_s.add_argument("--style", type=float, default=0.0)

    sub.add_parser("list-agents", help="List conversational AI agents")

    p_ca = sub.add_parser("create-agent", help="Create conversational AI agent")
    p_ca.add_argument("--name", required=True)
    p_ca.add_argument("--voice")
    p_ca.add_argument("--prompt")
    p_ca.add_argument("--first-message")
    p_ca.add_argument("--language", default="en")

    p_ga = sub.add_parser("get-agent", help="Get agent details")
    p_ga.add_argument("agent_id")

    p_cv = sub.add_parser("clone-voice", help="Clone a voice")
    p_cv.add_argument("name")
    p_cv.add_argument("--files", nargs="+", required=True)
    p_cv.add_argument("--description")

    args = parser.parse_args()
    cmds = {
        "voices": cmd_voices, "tts": cmd_tts, "tts-stream": cmd_tts_stream,
        "list-agents": cmd_list_agents, "create-agent": cmd_create_agent,
        "get-agent": cmd_get_agent, "clone-voice": cmd_clone_voice,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
