#!/usr/bin/env python3
"""Scrape upcoming metal concerts from concerts-metal.com broadcast pages."""

import argparse
import json
import re
import sys
import urllib.request

BROADCAST_URL = (
    "https://broadcast.concerts-metal.com/"
    "ie-998_000000_FF0000_b_ces__{country}.html"
)

COUNTRIES = {
    "AR": "Argentina", "AU": "Australia", "AT": "Austria", "BE": "Belgium",
    "BR": "Brazil", "BG": "Bulgaria", "CA": "Canada", "CL": "Chile",
    "CN": "China", "CO": "Colombia", "HR": "Croatia", "CZ": "Czech-Republic",
    "DK": "Denmark", "EE": "Estonia", "FI": "Finland", "FR": "France",
    "DE": "Germany", "GR": "Greece", "HU": "Hungary", "IS": "Iceland",
    "IN": "India", "ID": "Indonesia", "IE": "Ireland", "IL": "Israel",
    "IT": "Italy", "JP": "Japan", "LV": "Latvia", "LT": "Lithuania",
    "LU": "Luxembourg", "MY": "Malaysia", "MX": "Mexico", "NL": "Netherlands",
    "NZ": "New-Zealand", "NO": "Norway", "PE": "Peru", "PH": "Philippines",
    "PL": "Poland", "PT": "Portugal", "RO": "Romania", "RU": "Russia",
    "RS": "Serbia", "SG": "Singapore", "SK": "Slovakia", "SI": "Slovenia",
    "ZA": "South-Africa", "KR": "South-Korea", "ES": "Spain", "SE": "Sweden",
    "CH": "Switzerland", "TW": "Taiwan", "TH": "Thailand", "TR": "Turkey",
    "UA": "Ukraine", "GB": "United-Kingdom", "US": "United-States",
    "UY": "Uruguay", "VE": "Venezuela",
}


def fetch_html(country_name: str) -> str:
    url = BROADCAST_URL.format(country=country_name)
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:128.0) Gecko/20100101 Firefox/128.0",
    })
    with urllib.request.urlopen(req) as resp:
        return resp.read().decode("utf-8")


def parse_events(html: str) -> list[dict]:
    events = []
    blocks = html.split("row align-items-center")[1:]

    for block in blocks:
        # Event name
        title_match = re.search(r'itemprop="url" title="([^"]+)"', block)
        name = title_match.group(1) if title_match else ""

        # Event URL
        url_match = re.search(
            r'href="(https://en\.concerts-metal\.com/concert_[^"]+)"', block
        )
        url = url_match.group(1).replace("?i=1", "") if url_match else ""

        # Date and venue/city
        date_match = re.search(
            r'(\d{2}/\d{2}/\d{4}) @ (.+?)<br', block, re.DOTALL
        )
        if not date_match:
            continue

        raw_date = date_match.group(1)
        # Convert DD/MM/YYYY to YYYY-MM-DD
        day, month, year = raw_date.split("/")
        date = f"{year}-{month}-{day}"

        venue_city_raw = date_match.group(2)
        # Extract venue name (may be a link or plain text)
        venue_link = re.search(r'>([^<]+)</a>', venue_city_raw)
        # City is after the last >, or after comma
        city_match = re.search(r',\s*(.+)$', venue_city_raw)
        city = city_match.group(1).strip() if city_match else ""
        city = re.sub(r'<[^>]+>', '', city).strip()

        if venue_link:
            venue = venue_link.group(1).strip()
        else:
            # No link — venue might be plain text before comma
            plain = re.sub(r'<[^>]+>', '', venue_city_raw)
            parts = plain.split(",", 1)
            venue = parts[0].strip() if len(parts) > 1 else ""

        # Artists from <li> entries
        artists = []
        for li_match in re.finditer(
            r'<li>.*?<a\s+title="([^"]+)"[^>]*>[^<]*</a>\s*(.*?)</li>',
            block, re.DOTALL,
        ):
            artists.append(li_match.group(1).strip())

        events.append({
            "date": date,
            "artists": artists,
            "venue": venue,
            "city": city,
            "url": url,
        })

    return events


def main():
    parser = argparse.ArgumentParser(
        description="Search upcoming metal concerts from concerts-metal.com"
    )
    parser.add_argument(
        "--country", default="ES",
        help="ISO country code (e.g. ES, DE, US, GB). Default: ES",
    )
    parser.add_argument("--city", help="Filter by city name (case-insensitive)")
    parser.add_argument("--band", help="Filter by band name (case-insensitive)")
    parser.add_argument(
        "--list-countries", action="store_true",
        help="List supported country codes and exit",
    )
    args = parser.parse_args()

    if args.list_countries:
        for code, name in sorted(COUNTRIES.items()):
            print(f"  {code}  {name}")
        return

    code = args.country.upper()
    country_name = COUNTRIES.get(code)
    if not country_name:
        print(f"Error: Unknown country code '{code}'.", file=sys.stderr)
        print("Use --list-countries to see supported codes.", file=sys.stderr)
        sys.exit(1)

    try:
        html = fetch_html(country_name)
    except urllib.error.HTTPError as e:
        print(f"Error: HTTP {e.code} fetching {country_name} page.", file=sys.stderr)
        sys.exit(1)

    events = parse_events(html)

    if args.city:
        city_lower = args.city.lower()
        events = [e for e in events if city_lower in e["city"].lower()]

    if args.band:
        band_lower = args.band.lower()
        events = [
            e for e in events
            if any(band_lower in a.lower() for a in e["artists"])
        ]

    json.dump(events, sys.stdout, indent=2, ensure_ascii=False)
    print()


if __name__ == "__main__":
    main()
