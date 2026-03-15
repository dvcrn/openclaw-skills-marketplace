#!/usr/bin/env python3
import argparse, base64, json, mimetypes, os
import requests
from collections import defaultdict


def file_to_data_url(path: str) -> str:
    mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def normalize_segments(obj):
    segs = obj.get("segments") or obj.get("meta_info", {}).get("segments") or []
    out = []
    for s in segs:
        out.append({
            "start": s.get("start") or s.get("start_time") or s.get("start_ms"),
            "end": s.get("end") or s.get("end_time") or s.get("end_ms"),
            "speaker": s.get("speaker") or s.get("speaker_id") or "UNKNOWN",
            "content": s.get("content") or s.get("text") or "",
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-key", default=os.getenv("MOSS_API_KEY"))
    ap.add_argument("--endpoint", default="https://studio.mosi.cn/v1/audio/transcriptions")
    ap.add_argument("--model", default="moss-transcribe-diarize")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--audio-url")
    src.add_argument("--file")
    src.add_argument("--audio-data")
    ap.add_argument("--max-new-tokens", type=int, default=2048)
    ap.add_argument("--temperature", type=float, default=0)
    ap.add_argument("--meta-info", action="store_true")
    ap.add_argument("--out", default="transcribe_result.json")
    args = ap.parse_args()

    if not args.api_key:
        raise SystemExit("Missing API key. Set --api-key or MOSS_API_KEY")

    if args.audio_url:
        audio_data = args.audio_url
    elif args.file:
        audio_data = file_to_data_url(args.file)
    else:
        audio_data = args.audio_data

    payload = {
        "model": args.model,
        "audio_data": audio_data,
        "sampling_params": {
            "max_new_tokens": args.max_new_tokens,
            "temperature": args.temperature,
        },
        "meta_info": args.meta_info,
    }

    headers = {
        "Authorization": f"Bearer {args.api_key}",
        "Content-Type": "application/json",
    }

    r = requests.post(args.endpoint, headers=headers, json=payload, timeout=300)
    try:
        data = r.json()
    except Exception:
        raise SystemExit(f"Non-JSON response ({r.status_code}): {r.text[:300]}")

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    segs = normalize_segments(data)

    seg_path = args.out.replace('.json', '.segments.txt')
    with open(seg_path, "w", encoding="utf-8") as f:
        for s in segs:
            f.write(f"[{s['start']} - {s['end']}] {s['speaker']}: {s['content']}\n")

    by = defaultdict(list)
    for s in segs:
        by[s["speaker"]].append(s["content"])
    by_path = args.out.replace('.json', '.by_speaker.txt')
    with open(by_path, "w", encoding="utf-8") as f:
        for spk, parts in by.items():
            f.write(f"## {spk}\n")
            f.write("\n".join(parts) + "\n\n")

    print(json.dumps({
        "status": r.status_code,
        "result": args.out,
        "segments": seg_path,
        "by_speaker": by_path,
        "segment_count": len(segs),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
