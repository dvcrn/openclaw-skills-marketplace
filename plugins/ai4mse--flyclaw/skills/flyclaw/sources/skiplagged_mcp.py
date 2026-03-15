"""Skiplagged MCP client — optional alternative to REST API.

Connects to Skiplagged MCP server (mcp.skiplagged.com) using the
Python MCP SDK.  Supports fareClass, maxStops, sortBy parameters
that the REST API handles via fare_class.

Requires: mcp>=1.26.0 (optional dependency).

The MCP server returns Markdown-formatted text tables, not JSON.
This module parses the Markdown to extract flight data.
"""

import asyncio
import logging
import re

from airport_manager import airport_manager

logger = logging.getLogger("flyclaw.skiplagged_mcp")

# Mapping from FlyClaw cabin names to MCP fareClass values
_FARE_CLASS_MAP = {
    "economy": "economy",
    "premium": "premium",
    "business": "business",
    "first": "first",
}

# Mapping from FlyClaw stops values to MCP maxStops values
_STOPS_MAP = {
    0: "none",
    1: "one",
    2: "many",
    "any": "many",
}

# Mapping from FlyClaw sort values to MCP sortBy values
_SORT_MAP = {
    "cheapest": "price",
    "fastest": "duration",
    None: None,
}


class SkiplaggedMCPClient:
    """MCP client for Skiplagged flight search."""

    def __init__(self, url: str = "https://mcp.skiplagged.com/mcp",
                 timeout: int = 15):
        self.url = url
        self.timeout = timeout

    def search_flights(
        self, origin: str, destination: str, date: str,
        *, cabin: str = "economy", stops: int | str = 0,
        sort: str | None = None, limit: int = 50,
    ) -> list[dict]:
        """Search flights via MCP sk_flights_search tool.

        Returns list of FlyClaw standard record dicts.
        """
        arguments = {
            "origin": origin.upper(),
            "destination": destination.upper(),
            "departureDate": date,
        }

        # Map cabin to fareClass
        fare_class = _FARE_CLASS_MAP.get(cabin, "economy")
        if fare_class != "economy":
            arguments["fareClass"] = fare_class

        # Map stops to maxStops
        max_stops = _STOPS_MAP.get(stops)
        if max_stops and max_stops != "many":
            arguments["maxStops"] = max_stops

        # Map sort
        sort_by = _SORT_MAP.get(sort)
        if sort_by:
            arguments["sortBy"] = sort_by

        try:
            raw_text = _run_async(
                self._call_tool("sk_flights_search", arguments)
            )
        except Exception as e:
            logger.warning("MCP call failed: %s", e)
            return []

        if not raw_text:
            return []

        records = self._parse_markdown_response(
            raw_text, origin.upper(), destination.upper()
        )
        return records[:limit]

    async def _call_tool(self, tool_name: str, arguments: dict) -> str | None:
        """Call MCP tool and return raw text response."""
        try:
            from mcp import ClientSession
            from mcp.client.streamable_http import streamablehttp_client
        except ImportError:
            logger.warning("mcp package not installed")
            return None

        try:
            async with streamablehttp_client(self.url) as (read, write, _):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    result = await session.call_tool(tool_name, arguments)

                    texts = []
                    for item in result.content:
                        if hasattr(item, "text"):
                            texts.append(item.text)
                    return "\n".join(texts) if texts else None
        except Exception as e:
            logger.warning("MCP connection/call error: %s", e)
            return None

    def _parse_markdown_response(
        self, text: str, origin: str, destination: str,
    ) -> list[dict]:
        """Parse MCP Markdown table response into standard records.

        MCP returns a Markdown table with columns:
        | Price | Duration | Stops | Type | Airlines | Segments | Booking |
        """
        records = []

        # Find table rows (skip header and separator)
        lines = text.split("\n")
        in_table = False
        for line in lines:
            line = line.strip()
            if not line.startswith("|"):
                in_table = False
                continue

            # Skip header and separator rows
            if "Price" in line and "Duration" in line:
                in_table = True
                continue
            if re.match(r"^\|[\s\-|]+\|$", line):
                continue

            if not in_table:
                continue

            record = self._parse_table_row(line, origin, destination)
            if record:
                records.append(record)

        return records

    def _parse_table_row(
        self, line: str, origin: str, destination: str,
    ) -> dict | None:
        """Parse a single Markdown table row into a standard record.

        Row format: | $price | duration | stops | type | airlines | segments | booking |
        """
        # Split by | and strip whitespace; drop leading/trailing empties
        parts = line.split("|")
        # parts[0] and parts[-1] are empty from leading/trailing |
        cells = [c.strip() for c in parts[1:-1]]

        if len(cells) < 6:
            return None

        try:
            # Cell 0: Price (e.g. "$280" or "$1,234")
            price_str = cells[0].replace("$", "").replace(",", "").strip()
            price = float(price_str) if price_str else None

            # Cell 1: Duration (e.g. "2h 45m" or "25h 30m")
            duration_minutes = self._parse_duration(cells[1])

            # Cell 2: Stops (e.g. "Nonstop", "1 stop", "2 stops")
            stops = self._parse_stops(cells[2])

            # Cell 4: Airlines (e.g. "China Eastern Airlines")
            airline = cells[4] if len(cells) > 4 else ""

            # Cell 5: Segments — extract times and airports
            segments_text = cells[5] if len(cells) > 5 else ""
            # Cell 6: Booking — contains #trip=FLIGHT_NUMBER
            booking_text = cells[6] if len(cells) > 6 else ""
            flight_info = self._parse_segments(segments_text, booking_text)

            flight_number = flight_info.get("flight_number", "")
            scheduled_departure = flight_info.get("departure")
            scheduled_arrival = flight_info.get("arrival")
            actual_origin = flight_info.get("origin", origin)
            actual_dest = flight_info.get("destination", destination)

            return {
                "flight_number": flight_number,
                "airline": airline,
                "origin_iata": actual_origin,
                "origin_city": airport_manager.get_display_name(actual_origin),
                "destination_iata": actual_dest,
                "destination_city": airport_manager.get_display_name(actual_dest),
                "scheduled_departure": scheduled_departure,
                "scheduled_arrival": scheduled_arrival,
                "actual_departure": None,
                "actual_arrival": None,
                "status": "",
                "aircraft_type": "",
                "delay_minutes": None,
                "price": price,
                "stops": stops,
                "duration_minutes": duration_minutes,
                "source": "skiplagged",
            }
        except Exception as e:
            logger.debug("Failed to parse MCP table row: %s", e)
            return None

    @staticmethod
    def _parse_duration(text: str) -> int | None:
        """Parse duration string like '2h 45m' or '25h 30m'."""
        if not text:
            return None
        match = re.search(r"(\d+)h\s*(\d+)m", text)
        if match:
            return int(match.group(1)) * 60 + int(match.group(2))
        match = re.search(r"(\d+)h", text)
        if match:
            return int(match.group(1)) * 60
        match = re.search(r"(\d+)m", text)
        if match:
            return int(match.group(1))
        return None

    @staticmethod
    def _parse_stops(text: str) -> int:
        """Parse stops string like 'Nonstop', '1 stop', '2 stops'."""
        text = text.strip().lower()
        if "nonstop" in text or "non-stop" in text:
            return 0
        match = re.search(r"(\d+)\s*stop", text)
        if match:
            return int(match.group(1))
        return 0

    @staticmethod
    def _parse_segments(text: str, booking_text: str = "") -> dict:
        """Parse segments cell to extract flight info.

        Example segment text:
        Outbound:<br/>PVG → NRT (2026-04-01 09:05:00+08:00 → 2026-04-01 12:50:00+09:00)

        booking_text contains the booking link with #trip=FLIGHT_NUMBER.

        For multi-segment, extracts first segment's flight number and
        first departure / last arrival.
        """
        info: dict = {}

        # Extract flight numbers from booking links: #trip=MU523 or #trip=BR721-BR102
        combined = text + " " + booking_text
        trip_match = re.search(r"#trip=([A-Z0-9\-]+)", combined)
        if trip_match:
            trip_parts = trip_match.group(1).split("-")
            info["flight_number"] = trip_parts[0] if trip_parts else ""

        # Extract departure/arrival times and airports
        # Pattern: ORIGIN → DEST (datetime → datetime)
        segment_pattern = re.compile(
            r"([A-Z]{3})\s*→\s*([A-Z]{3})\s*\("
            r"(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})[^)]*→\s*"
            r"(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})"
        )
        segments = segment_pattern.findall(text)

        if segments:
            first = segments[0]
            last = segments[-1]
            info["origin"] = first[0]
            info["destination"] = last[1]
            # Convert space-separated to ISO format
            info["departure"] = first[2].replace(" ", "T")
            info["arrival"] = last[3].replace(" ", "T")

        return info


def _run_async(coro):
    """Run async coroutine from sync context (ThreadPoolExecutor safe)."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()
