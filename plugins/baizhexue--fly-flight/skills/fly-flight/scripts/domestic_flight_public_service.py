#!/usr/bin/env python3
"""Query China domestic flights from public Tongcheng pages and expose a local HTTP service."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, quote, urlparse
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "assets" / "data"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8766
PUBLIC_PROVIDER_URL_TEMPLATE = "https://www.ly.com/flights/itinerary/oneway/{departure}-{arrival}?date={departure_date}"
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122 Safari/537.36"


def load_json(path: Path) -> dict[str, str]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


CITY_CODES = load_json(DATA_DIR / "domestic_city_codes.json")
AIRPORT_ALIASES = load_json(DATA_DIR / "airport_aliases.json")


@dataclass(frozen=True)
class Place:
    raw: str
    query: str
    code: str
    resolved_as: str


SORT_MODES = {"price", "departure", "arrival", "duration"}


def canonicalize_place(value: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError("地点不能为空")
    if len(cleaned) == 3 and cleaned.isalpha():
        return cleaned.upper()
    for suffix in ("特别行政区", "自治区", "自治州", "省", "市"):
        if cleaned.endswith(suffix):
            cleaned = cleaned[: -len(suffix)]
            break
    return cleaned.replace(" ", "")


def resolve_place(value: str) -> Place:
    normalized = canonicalize_place(value)
    if len(normalized) == 3 and normalized.isalpha():
        code = normalized.upper()
        return Place(raw=value, query=normalized, code=code, resolved_as="iata")
    if normalized in AIRPORT_ALIASES:
        code = AIRPORT_ALIASES[normalized]
        return Place(raw=value, query=normalized, code=code, resolved_as="airport")
    if normalized in CITY_CODES:
        code = CITY_CODES[normalized]
        return Place(raw=value, query=normalized, code=code, resolved_as="city")
    raise ValueError(f"无法识别地点“{value}”。请改用常见城市名、具体机场名，或直接提供三字码。")


def validate_date(value: str) -> str:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("日期必须是 YYYY-MM-DD 格式") from exc
    return value


def fetch_html(url: str, timeout: int) -> str:
    request = Request(url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", "ignore")


def extract_state_from_html(html: str) -> dict[str, Any]:
    script_path = ROOT / "scripts" / "extract_tongcheng_state.js"
    completed = subprocess.run(
        ["node", str(script_path)],
        input=html,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        error = completed.stderr.strip() or completed.stdout.strip() or "unknown extractor error"
        raise RuntimeError(f"公开页面解析失败: {error}")
    return json.loads(completed.stdout)


def parse_time_duration(value: str) -> str:
    if not value:
        return ""
    return value.replace("小时", "h").replace("分钟", "m")


def duration_minutes(value: str) -> int:
    if not value:
        return 10**9
    hours = 0
    minutes = 0
    if "h" in value:
        left, _, rest = value.partition("h")
        hours = int(left or 0)
        value = rest
    if "m" in value:
        minutes = int(value.replace("m", "") or 0)
    return hours * 60 + minutes


def time_sort_value(date_value: str | None, time_value: str | None) -> str:
    return f"{date_value or '9999-99-99'}T{time_value or '99:99'}"


def simplify_flight(item: dict[str, Any]) -> dict[str, Any]:
    ticket_price = item.get("flightPrice")
    if not ticket_price:
        prices = item.get("productPrices") or {}
        ticket_price = next(iter(prices.values()), None)

    return {
        "airline_code": item.get("airCompanyCode"),
        "airline_name": item.get("airCompanyName"),
        "flight_no": item.get("flightNo"),
        "equipment": item.get("equipmentName"),
        "is_codeshare": False,
        "departure_code": item.get("originAirportCode"),
        "departure_name": item.get("originAirportShortName") or item.get("oapname"),
        "departure_date": (item.get("flyOffTime") or "").split(" ")[0],
        "departure_time": item.get("flyOffOnlyTime"),
        "arrival_code": item.get("arriveAirportCode"),
        "arrival_name": item.get("arriveAirportShortName") or item.get("aapname"),
        "arrival_date": (item.get("arrivalTime") or "").split(" ")[0],
        "arrival_time": item.get("arrivalOnlyTime"),
        "duration": parse_time_duration(item.get("spantime", "")),
        "segments": int(item.get("stopNum", 0)) + 1,
        "ticket_price": ticket_price,
        "raw": item,
    }


def matches_airline(flight: dict[str, Any], airline: str | None) -> bool:
    if not airline:
        return True
    query = airline.strip().lower()
    return query in (flight.get("airline_code") or "").lower() or query in (
        flight.get("airline_name") or ""
    ).lower()


def filter_flights(
    flights: list[dict[str, Any]],
    *,
    direct_only: bool,
    preferred_departure_airport: str | None,
    preferred_arrival_airport: str | None,
    airline: str | None,
) -> list[dict[str, Any]]:
    departure_code = resolve_place(preferred_departure_airport).code if preferred_departure_airport else None
    arrival_code = resolve_place(preferred_arrival_airport).code if preferred_arrival_airport else None

    filtered = flights
    if direct_only:
        filtered = [flight for flight in filtered if int(flight.get("segments") or 0) <= 1]
    if departure_code:
        filtered = [flight for flight in filtered if flight.get("departure_code") == departure_code]
    if arrival_code:
        filtered = [flight for flight in filtered if flight.get("arrival_code") == arrival_code]
    if airline:
        filtered = [flight for flight in filtered if matches_airline(flight, airline)]
    return filtered


def sort_flights(flights: list[dict[str, Any]], sort_by: str) -> list[dict[str, Any]]:
    if sort_by == "departure":
        return sorted(
            flights,
            key=lambda item: (
                time_sort_value(item.get("departure_date"), item.get("departure_time")),
                item.get("ticket_price") is None,
                item.get("ticket_price", 0),
            ),
        )
    if sort_by == "arrival":
        return sorted(
            flights,
            key=lambda item: (
                time_sort_value(item.get("arrival_date"), item.get("arrival_time")),
                item.get("ticket_price") is None,
                item.get("ticket_price", 0),
            ),
        )
    if sort_by == "duration":
        return sorted(
            flights,
            key=lambda item: (
                duration_minutes(item.get("duration") or ""),
                item.get("ticket_price") is None,
                item.get("ticket_price", 0),
            ),
        )
    return sorted(flights, key=lambda item: (item.get("ticket_price") is None, item.get("ticket_price", 0)))


def normalize_leg_response(
    state_payload: dict[str, Any],
    origin: Place,
    destination: Place,
    departure_date: str,
    limit: int,
    *,
    sort_by: str,
    direct_only: bool,
    preferred_departure_airport: str | None,
    preferred_arrival_airport: str | None,
    airline: str | None,
) -> dict[str, Any]:
    flights = [simplify_flight(item) for item in (state_payload.get("flightLists") or [])]
    flights = [item for item in flights if item.get("flight_no")]
    flights = filter_flights(
        flights,
        direct_only=direct_only,
        preferred_departure_airport=preferred_departure_airport,
        preferred_arrival_airport=preferred_arrival_airport,
        airline=airline,
    )
    flights = sort_flights(flights, sort_by=sort_by)
    trimmed = flights[:limit]

    return {
        "provider_reference": state_payload.get("cid"),
        "route": {
            "from": {"input": origin.raw, "query": origin.query, "code": origin.code, "resolved_as": origin.resolved_as},
            "to": {"input": destination.raw, "query": destination.query, "code": destination.code, "resolved_as": destination.resolved_as},
            "date": departure_date,
        },
        "count": len(trimmed),
        "total_found": len(flights),
        "sort_by": sort_by,
        "filters": {
            "direct_only": direct_only,
            "preferred_departure_airport": preferred_departure_airport,
            "preferred_arrival_airport": preferred_arrival_airport,
            "airline": airline,
        },
        "flights": trimmed,
    }


def fetch_state_payload(
    origin: Place,
    destination: Place,
    departure_date: str,
    *,
    timeout: int,
    sample_state: str | None,
) -> dict[str, Any]:
    if sample_state:
        with open(sample_state, "r", encoding="utf-8") as handle:
            return json.load(handle)
    url = PUBLIC_PROVIDER_URL_TEMPLATE.format(
        departure=quote(origin.code),
        arrival=quote(destination.code),
        departure_date=quote(departure_date),
    )
    html = fetch_html(url, timeout=timeout)
    return extract_state_from_html(html)


def run_search(args: argparse.Namespace) -> dict[str, Any]:
    origin = resolve_place(args.origin)
    destination = resolve_place(args.destination)
    departure_date = validate_date(args.date)
    if args.sort_by not in SORT_MODES:
        raise ValueError(f"sort_by 仅支持: {', '.join(sorted(SORT_MODES))}")

    outbound_state = fetch_state_payload(
        origin,
        destination,
        departure_date,
        timeout=args.timeout,
        sample_state=args.sample_state,
    )
    outbound = normalize_leg_response(
        outbound_state,
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        limit=args.limit,
        sort_by=args.sort_by,
        direct_only=args.direct_only,
        preferred_departure_airport=args.preferred_departure_airport,
        preferred_arrival_airport=args.preferred_arrival_airport,
        airline=args.airline,
    )

    payload: dict[str, Any] = {
        "provider": "tongcheng-public-page",
        "reason": "success",
        "trip_type": "round-trip" if args.return_date else "one-way",
        "outbound": outbound,
    }

    if args.return_date:
        return_date = validate_date(args.return_date)
        return_state = fetch_state_payload(
            destination,
            origin,
            return_date,
            timeout=args.timeout,
            sample_state=args.return_sample_state or args.sample_state,
        )
        payload["return"] = normalize_leg_response(
            return_state,
            origin=destination,
            destination=origin,
            departure_date=return_date,
            limit=args.limit,
            sort_by=args.return_sort_by or args.sort_by,
            direct_only=args.direct_only,
            preferred_departure_airport=args.return_preferred_departure_airport,
            preferred_arrival_airport=args.return_preferred_arrival_airport,
            airline=args.airline,
        )
    return payload


class FlightHandler(BaseHTTPRequestHandler):
    server_version = "DomesticFlightSearchPublic/1.0"

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            self.send_json(200, {"ok": True, "service": "fly-flight"})
            return
        if parsed.path != "/search":
            self.send_json(404, {"ok": False, "error": "not_found"})
            return

        params = parse_qs(parsed.query, keep_blank_values=False)
        try:
            args = argparse.Namespace(
                origin=self.require_param(params, "from"),
                destination=self.require_param(params, "to"),
                date=self.require_param(params, "date"),
                limit=int(params.get("limit", ["10"])[0]),
                timeout=int(params.get("timeout", ["20"])[0]),
                sort_by=params.get("sort_by", ["price"])[0],
                return_sort_by=params.get("return_sort_by", [""])[0] or None,
                return_date=params.get("return_date", [""])[0] or None,
                direct_only=params.get("direct_only", ["0"])[0] in {"1", "true", "yes"},
                airline=params.get("airline", [""])[0] or None,
                preferred_departure_airport=params.get("preferred_departure_airport", [""])[0] or None,
                preferred_arrival_airport=params.get("preferred_arrival_airport", [""])[0] or None,
                return_preferred_departure_airport=params.get("return_preferred_departure_airport", [""])[0] or None,
                return_preferred_arrival_airport=params.get("return_preferred_arrival_airport", [""])[0] or None,
                sample_state=params.get("sample_state", [None])[0],
                return_sample_state=params.get("return_sample_state", [None])[0],
            )
            payload = run_search(args)
            self.send_json(200, {"ok": True, "data": payload})
        except Exception as exc:  # noqa: BLE001
            self.send_json(400, {"ok": False, "error": str(exc)})

    def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
        return

    @staticmethod
    def require_param(params: dict[str, list[str]], key: str) -> str:
        values = params.get(key)
        if not values or not values[0].strip():
            raise ValueError(f"缺少参数: {key}")
        return values[0]

    def send_json(self, status: int, payload: dict[str, Any]) -> None:
        body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def serve(args: argparse.Namespace) -> None:
    server = ThreadingHTTPServer((args.host, args.port), FlightHandler)
    print(
        json.dumps(
            {
                "ok": True,
                "host": args.host,
                "port": args.port,
                "search_example": f"http://{args.host}:{args.port}/search?from=北京&to=上海&date=2026-03-20&sort_by=price&direct_only=1",
            },
            ensure_ascii=False,
        )
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    search = subparsers.add_parser("search", help="Query flights and print JSON.")
    search.add_argument("--from", dest="origin", required=True, help="出发城市、机场名或三字码")
    search.add_argument("--to", dest="destination", required=True, help="到达城市、机场名或三字码")
    search.add_argument("--date", required=True, help="出发日期，格式 YYYY-MM-DD")
    search.add_argument("--return-date", help="返程日期，格式 YYYY-MM-DD")
    search.add_argument("--limit", type=int, default=10, help="最多返回多少条")
    search.add_argument("--timeout", type=int, default=20, help="页面抓取超时秒数")
    search.add_argument("--sort-by", default="price", help="排序方式: price/departure/arrival/duration")
    search.add_argument("--return-sort-by", help="返程排序方式，默认沿用 --sort-by")
    search.add_argument("--direct-only", action="store_true", help="仅保留直飞")
    search.add_argument("--airline", help="按航司代码或名称过滤，例如 MU / 东航")
    search.add_argument("--preferred-departure-airport", help="限定去程起飞机场，如 北京首都 / PKX")
    search.add_argument("--preferred-arrival-airport", help="限定去程到达机场，如 上海虹桥 / PVG")
    search.add_argument("--return-preferred-departure-airport", help="限定返程起飞机场")
    search.add_argument("--return-preferred-arrival-airport", help="限定返程到达机场")
    search.add_argument("--sample-state", help="使用本地 JSON 样例状态代替真实网页抓取")
    search.add_argument("--return-sample-state", help="返程使用本地 JSON 样例状态代替真实网页抓取")
    search.add_argument("--pretty", action="store_true", help="格式化输出 JSON")

    serve_parser = subparsers.add_parser("serve", help="Start a local HTTP service.")
    serve_parser.add_argument("--host", default=DEFAULT_HOST, help=f"监听地址，默认 {DEFAULT_HOST}")
    serve_parser.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"监听端口，默认 {DEFAULT_PORT}")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "search":
            payload = run_search(args)
            print(json.dumps(payload, ensure_ascii=False, indent=2 if args.pretty else None))
            return 0
        if args.command == "serve":
            serve(args)
            return 0
    except BrokenPipeError:
        return 0
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1

    parser.error("未知命令")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
