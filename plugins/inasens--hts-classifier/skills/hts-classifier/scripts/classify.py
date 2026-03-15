#!/usr/bin/env python3
"""HTS Classifier — Look up US tariff codes and 2026 duty rates.

Usage:
    python3 classify.py --query "solar panels"
    python3 classify.py --hts "8541.40"
    python3 classify.py --query "steel pipe" --hts "7304.19"
"""

import argparse
import json
import logging
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

LOG_PATH = os.environ.get("HTS_LOG", "/tmp/hts-classifier.log")
logging.basicConfig(filename=LOG_PATH, level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("hts")

API_BASE = "https://ustariffrates.com/api/search"
D1_ACCOUNT = "4bb6787daeb7c36963ac7f1176a6a125"
D1_DB_ID = "b8185ee2-6ae8-4061-9f74-3e85f6ae8214"


def search_api(query: str) -> dict:
    """Search the public USTariffRates API."""
    url = f"{API_BASE}?{urllib.parse.urlencode({'q': query})}"
    req = urllib.request.Request(url, headers={"User-Agent": "openclaw-hts-classifier/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}", "results": []}
    except urllib.error.URLError as e:
        return {"error": f"Connection failed: {e.reason}", "results": []}
    except Exception as e:
        return {"error": str(e), "results": []}


def query_d1(sql: str) -> dict:
    """Fallback: query Cloudflare D1 directly if HTS_API_KEY is set."""
    api_key = os.environ.get("HTS_API_KEY")
    if not api_key:
        return {"error": "HTS_API_KEY not set", "results": []}

    url = (
        f"https://api.cloudflare.com/client/v4/accounts/{D1_ACCOUNT}"
        f"/d1/database/{D1_DB_ID}/query"
    )
    payload = json.dumps({"sql": sql}).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
            if data.get("success") and data.get("result"):
                rows = data["result"][0].get("results", [])
                return {"results": rows}
            return {"error": "D1 query returned no results", "results": []}
    except Exception as e:
        return {"error": f"D1 query failed: {e}", "results": []}


def search_by_query(query: str) -> dict:
    """Search by product description, with Ollama ranking when available."""
    result = search_api(query)

    if not result.get("results"):
        # Fallback to D1 if API returned nothing and we have a key
        if os.environ.get("HTS_API_KEY"):
            safe_q = query.replace("'", "''")
            sql = (
                f"SELECT * FROM hts_codes WHERE description LIKE '%{safe_q}%' "
                f"ORDER BY hts_code LIMIT 10"
            )
            result = query_d1(sql)

    # Try Ollama ranking — falls back silently to FTS5 order
    if result.get("results"):
        ranked = rank_with_ollama(query, result["results"])
        if ranked:
            result["results"] = ranked
            result["_ranked_by"] = OLLAMA_MODEL
        else:
            result["_ranked_by"] = "fts5"

    return result


def search_by_hts(code: str) -> dict:
    """Look up a specific HTS code."""
    result = search_api(code)
    if result.get("results"):
        # Filter to results whose HTS code starts with the queried prefix
        filtered = [
            r for r in result["results"]
            if r.get("hts_code", "").replace(".", "").startswith(code.replace(".", ""))
        ]
        if filtered:
            result["results"] = filtered
        return result

    # Fallback to D1
    if os.environ.get("HTS_API_KEY"):
        safe_code = code.replace("'", "''")
        sql = (
            f"SELECT * FROM hts_codes WHERE hts_code LIKE '{safe_code}%' "
            f"ORDER BY hts_code LIMIT 10"
        )
        return query_d1(sql)

    return result


OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen3:8b")
OLLAMA_TIMEOUT = int(os.environ.get("OLLAMA_TIMEOUT", "30"))

RANK_PROMPT = """You are a US Customs broker expert. Given a product query and a list of candidate HTS codes, rank them by relevance.

Product query: {query}

Candidates (JSON array):
{candidates}

Return a JSON object with a single key "ranked" containing an array of objects, each with:
- "hts_code": the code
- "confidence": 0.0-1.0 (how likely this is the correct classification)
- "reason": one-line explanation

Only include the top 5 most relevant. Return ONLY valid JSON, no markdown."""


def rank_with_ollama(query: str, results: list) -> list:
    """Rank FTS5 results using local Ollama. Returns ranked list or None on failure."""
    if not results:
        return None
    try:
        candidates = json.dumps([
            {"hts_code": r.get("hts_code", ""), "description": r.get("description", ""),
             "hierarchy": r.get("hierarchy", "")}
            for r in results[:15]  # cap input to 15 candidates
        ], indent=1)

        payload = json.dumps({
            "model": OLLAMA_MODEL,
            "prompt": RANK_PROMPT.format(query=query, candidates=candidates),
            "stream": False,
            "format": "json",
            "options": {"temperature": 0.1, "num_predict": 512},
        }).encode()

        req = urllib.request.Request(
            f"{OLLAMA_URL}/api/generate",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=OLLAMA_TIMEOUT) as resp:
            data = json.loads(resp.read().decode())

        content = data.get("response", "")
        if not content.strip():
            log.warning("Empty Ollama response for query=%s", query)
            return None
        parsed = json.loads(content)
        ranked = parsed.get("ranked", [])

        if not ranked:
            log.warning("Ollama returned empty ranking for query=%s", query)
            return None

        # Merge confidence/reason back into original results
        rank_map = {r["hts_code"]: r for r in ranked}
        enriched = []
        for r in results:
            code = r.get("hts_code", "")
            if code in rank_map:
                r["_confidence"] = rank_map[code].get("confidence", 0)
                r["_rank_reason"] = rank_map[code].get("reason", "")
                enriched.append(r)

        enriched.sort(key=lambda x: x.get("_confidence", 0), reverse=True)
        log.info("Ranked %d results for query=%s via %s", len(enriched), query, OLLAMA_MODEL)
        return enriched if enriched else None

    except Exception as e:
        log.error("Ollama ranking failed for query=%s: %s", query, e)
        return None


def format_result(data: dict) -> str:
    """Pretty-print the result as JSON."""
    return json.dumps(data, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Look up HTS tariff codes and 2026 US duty rates"
    )
    parser.add_argument(
        "--query", "-q", type=str, help="Product description to classify"
    )
    parser.add_argument(
        "--hts", "-c", type=str, help="HTS code to look up (e.g. 8541.40)"
    )
    parser.add_argument(
        "--raw", action="store_true", help="Output raw JSON (no formatting)"
    )
    args = parser.parse_args()

    if not args.query and not args.hts:
        parser.error("At least one of --query or --hts is required")

    results = {}

    if args.query:
        results["query_results"] = search_by_query(args.query)

    if args.hts:
        results["hts_results"] = search_by_hts(args.hts)

    # If only one type of search, flatten
    if args.query and not args.hts:
        results = results["query_results"]
    elif args.hts and not args.query:
        results = results["hts_results"]

    if args.raw:
        print(json.dumps(results))
    else:
        print(format_result(results))


if __name__ == "__main__":
    main()
