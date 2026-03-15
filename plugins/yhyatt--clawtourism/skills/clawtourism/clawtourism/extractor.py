"""TripExtractor — extracts structured data from email bodies using regex + heuristics.

Improvements:
- RTL Hebrew subject parsing
- Third-party ticketing platform support (aerocrs, amsalem, clubmed subdomains)
- Forwarded email chain traversal
- Subdomain matching for senders
"""

from __future__ import annotations

import re
from datetime import date
from typing import TYPE_CHECKING

from dateutil import parser as date_parser

from clawtourism.models import CruiseBooking, Flight, Hotel, Restaurant

if TYPE_CHECKING:
    from clawtourism.scanner import ForwardedEmail


class TripExtractor:
    """Extracts travel booking information from email text using regex and heuristics."""

    # Date patterns (full match patterns for dateutil parsing)
    DATE_PATTERNS = [
        # Dec 13 2025, Dec 13, 2025, December 13 2025
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
        r"\s+\d{1,2}(?:,?\s+|\s+)\d{4}",
        # 13 Dec 2025, 13-Dec-2025, 13 December 2025
        r"\d{1,2}[\s\-](?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|"
        r"Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
        r"[\s\-]\d{4}",
        # 12/02/2026, 12-02-2026
        r"\d{1,2}[/\-]\d{1,2}[/\-]\d{4}",
        # 2026-02-12
        r"\d{4}[/\-]\d{1,2}[/\-]\d{1,2}",
    ]

    # Booking reference patterns
    BOOKING_REF_PATTERNS = [
        r"(?:booking\s*(?:code|ref(?:erence)?|nr\.?|number)?|confirmation\s*(?:code|number)?|"
        r"reservation\s*(?:code|number)?)\s*[:#]?\s*([A-Z0-9]{5,12})",
        r"#\s*(\d{6,12})",
        r"(?:PNR|locator)\s*[:#]?\s*([A-Z0-9]{6})",
    ]

    # RTL Hebrew booking patterns (booking number BEFORE Hebrew label in RTL)
    RTL_BOOKING_PATTERNS = [
        # "327171557 :מספר הזמנה" — 9-digit booking number before Hebrew label
        r"(\d{6,12})\s*:\s*מספר\s+הזמנה",
        # "XXXXXX :קוד הזמנה" — alphanumeric booking code
        r"([A-Z0-9]{5,12})\s*:\s*קוד\s+הזמנה",
        # "67669352 :הזמנה" — simple booking pattern
        r"(\d{6,12})\s*:\s*הזמנה",
    ]

    # Flight number patterns
    FLIGHT_PATTERNS = [
        r"\b([A-Z][A-Z0-9])\s+(\d{1,4})\b",  # W4 7515, LY 123 (with space)
        r"\b([A-Z]{2})(\d{1,4})\b",  # W47515, LY123 (no space)
    ]

    # Airport code pattern
    AIRPORT_PATTERN = r"\b([A-Z]{3})\b"

    # Time pattern
    TIME_PATTERN = r"\b(\d{1,2}):(\d{2})\b"

    # Price patterns
    PRICE_PATTERNS = [
        r"[\$€£₪][\s]*(\d+(?:[,\.]\d{2,3})?)",
        r"(\d+(?:[,\.]\d{2,3})?)\s*(?:USD|EUR|GBP|ILS|דולר)",
    ]

    # Known airport codes (expanded)
    KNOWN_AIRPORTS = {
        "TLV", "ATH", "BCN", "FCO", "CDG", "LHR", "JFK", "EWR", "LAX",
        "MUC", "FRA", "AMS", "VIE", "IST", "DXB", "SIN", "HKG", "NRT",
        "LGW", "STN", "ORD", "SFO", "BOS", "MIA", "DFW", "PHX", "SEA",
        "GVA", "ZRH", "BRU", "MAD", "LIS", "OPO", "MXP", "LIN", "NAP",
        "SKG", "HER", "RHO", "JTR", "CHQ",  # Greek airports
        "SOF", "WAW", "PRG", "BUD", "OTP", "BEG",  # Eastern Europe
    }

    # Airline code to name mapping
    AIRLINE_MAPPING = {
        "W4": "Wizz Air",
        "W6": "Wizz Air",
        "LY": "EL AL",
        "FR": "Ryanair",
        "LH": "Lufthansa",
        "A3": "Aegean",
        "BA": "British Airways",
        "AF": "Air France",
        "KL": "KLM",
        "UA": "United",
        "AA": "American Airlines",
        "DL": "Delta",
    }

    # Sender domain to airline mapping (for subdomain matching)
    SENDER_AIRLINE_MAPPING = {
        "wizzair.com": "Wizz Air",
        "elal.co.il": "EL AL",
        "ryanair.com": "Ryanair",
        "lufthansa.com": "Lufthansa",
        "aegean.com": "Aegean",
        "aerocrs.com": "Blue Bird Airways",  # Third-party ticketing platform
        "amsalem.com": "Travel Agent",  # Israeli travel agent
    }

    def extract_dates(self, text: str) -> list[date]:
        """Extract dates from text."""
        dates = []
        # Use dateutil parser for flexibility
        for pattern in self.DATE_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    date_str = match.group(0)
                    parsed = date_parser.parse(date_str, fuzzy=False, dayfirst=True)
                    dates.append(parsed.date())
                except (ValueError, TypeError):
                    continue
        return sorted(set(dates))

    def extract_booking_refs(self, text: str) -> list[str]:
        """Extract booking reference numbers from text.

        Handles both LTR and RTL patterns.
        """
        refs = []

        # Standard LTR patterns
        for pattern in self.BOOKING_REF_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                ref = match.group(1).strip().upper()
                if ref and len(ref) >= 5:
                    refs.append(ref)

        # RTL Hebrew patterns (booking number BEFORE label)
        for pattern in self.RTL_BOOKING_PATTERNS:
            for match in re.finditer(pattern, text):
                ref = match.group(1).strip().upper()
                if ref and len(ref) >= 5:
                    refs.append(ref)

        # Also look for standalone all-caps alphanumeric codes
        for match in re.finditer(r"\b([A-Z0-9]{6,8})\b", text):
            candidate = match.group(1)
            # Filter out common false positives
            if candidate not in {"BOOKING", "CONFIRM", "RESERVE", "RECEIPT", "AIRBNB", "HYATT"}:
                refs.append(candidate)

        return list(dict.fromkeys(refs))  # Dedupe while preserving order

    def extract_flight_numbers(self, text: str) -> list[str]:
        """Extract flight numbers from text."""
        flights = []
        for pattern in self.FLIGHT_PATTERNS:
            for match in re.finditer(pattern, text):
                airline = match.group(1)
                number = match.group(2)
                flight_num = f"{airline} {number}"
                # Validate: airline should be 2 chars (letter+letter/digit), number 1-4 digits
                if re.match(r"[A-Z][A-Z0-9]\s+\d{1,4}$", flight_num):
                    flights.append(flight_num)
        return list(dict.fromkeys(flights))

    def extract_airports(self, text: str) -> list[str]:
        """Extract airport codes from text."""
        found = []
        for match in re.finditer(self.AIRPORT_PATTERN, text):
            code = match.group(1)
            if code in self.KNOWN_AIRPORTS:
                found.append(code)
        return list(dict.fromkeys(found))

    def extract_times(self, text: str) -> list[str]:
        """Extract times in HH:MM format."""
        times = []
        for match in re.finditer(self.TIME_PATTERN, text):
            hour, minute = match.groups()
            times.append(f"{int(hour):02d}:{minute}")
        return times

    def extract_prices(self, text: str) -> list[str]:
        """Extract price amounts from text."""
        prices = []
        for pattern in self.PRICE_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                prices.append(match.group(0).strip())
        return prices

    def extract_passenger_names(self, text: str) -> list[str]:
        """Extract passenger names from text."""
        names = []
        # Pattern for names in booking confirmations
        patterns = [
            r"(?:Passenger|Guest|Name|Mr|Mrs|Ms|Miss)\s*[:\s]+([A-Z][a-z]+\s+[A-Z][a-z]+)",
            r"Dear\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
            r"(?:for|to)\s+([A-Z][A-Z]+\s+[A-Z]+)",  # ALL CAPS names
        ]
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                name = match.group(1).strip()
                if name and len(name) > 3:
                    names.append(name.title())
        return list(dict.fromkeys(names))

    def get_airline_from_sender(self, sender: str) -> str | None:
        """Get airline name from sender domain (with subdomain matching)."""
        # Extract domain from sender
        email_match = re.search(r"<([^>]+)>", sender)
        if email_match:
            email = email_match.group(1)
        else:
            email = sender

        domain_match = re.search(r"@([^\s>]+)", email)
        if not domain_match:
            return None

        sender_domain = domain_match.group(1).lower()

        # Check with subdomain matching
        for known_domain, airline in self.SENDER_AIRLINE_MAPPING.items():
            if sender_domain == known_domain or sender_domain.endswith("." + known_domain):
                return airline

        return None

    def parse_flight_from_email(
        self, subject: str, body: str, sender: str
    ) -> Flight | None:
        """Parse flight information from email."""
        text = f"{subject}\n{body}"

        flight_nums = self.extract_flight_numbers(text)
        if not flight_nums:
            return None

        airports = self.extract_airports(text)
        dates = self.extract_dates(text)
        times = self.extract_times(text)
        booking_refs = self.extract_booking_refs(text)
        passengers = self.extract_passenger_names(text)

        # Determine airline from sender (with subdomain matching)
        airline = self.get_airline_from_sender(sender)

        # Fallback: determine from flight number
        if not airline and flight_nums:
            first_flight = flight_nums[0]
            if " " in first_flight:
                airline_code = first_flight.split()[0]
            else:
                airline_code = first_flight[:2]
            airline = self.AIRLINE_MAPPING.get(airline_code)

        return Flight(
            flight_number=flight_nums[0] if flight_nums else "",
            departure_airport=airports[0] if len(airports) >= 1 else "",
            arrival_airport=airports[1] if len(airports) >= 2 else "",
            departure_date=dates[0] if dates else date.today(),
            departure_time=times[0] if len(times) >= 1 else None,
            arrival_time=times[1] if len(times) >= 2 else None,
            passengers=passengers,
            booking_ref=booking_refs[0] if booking_refs else None,
            airline=airline,
        )

    def parse_flight_from_forwarded(
        self, forwarded: ForwardedEmail
    ) -> Flight | None:
        """Parse flight from a forwarded email chain."""
        return self.parse_flight_from_email(
            forwarded.original_subject,
            forwarded.body,
            forwarded.original_sender,
        )

    def parse_hotel_from_email(
        self, subject: str, body: str, sender: str
    ) -> Hotel | None:
        """Parse hotel information from email."""
        text = f"{subject}\n{body}"

        dates = self.extract_dates(text)
        booking_refs = self.extract_booking_refs(text)

        # Extract hotel name from subject or sender
        name = None

        # Check sender-based patterns first (more reliable)
        if "@reserve-online.net" in sender:
            # Format: "Hotel Name <booking+ID@reserve-online.net>"
            name_match = re.match(r"([^<]+)", sender)
            if name_match:
                name = name_match.group(1).strip()
        elif "booking.com" in sender.lower():
            name_match = re.search(r"at\s+([A-Za-z0-9\s]+)", subject)
            if name_match:
                name = name_match.group(1).strip()

        # Fallback: extract from subject line (less reliable)
        if not name:
            # Pattern: "✅ Hotel Name Booking confirmation 12345"
            hotel_pattern = r"[✅☑️]?\s*(.+?)\s+Booking\s+(?:confirmation|confirmed)"
            name_match = re.match(hotel_pattern, subject, re.IGNORECASE)
            if name_match:
                name = name_match.group(1).strip()
            elif "confirmed" in subject.lower() or "confirmation" in subject.lower():
                # Pattern: "booking confirmed at Hotel Name"
                name_match = re.search(r"at\s+([^-]+)", subject, re.IGNORECASE)
                if name_match:
                    name = name_match.group(1).strip()

        if not name:
            return None

        # Extract guest count
        guests = 2
        guests_match = re.search(r"(\d+)\s*(?:Guests?|people|persons?)", text, re.IGNORECASE)
        if guests_match:
            guests = int(guests_match.group(1))

        # Check if cancelled
        cancelled = "cancelled" in subject.lower() or "canceled" in subject.lower()

        return Hotel(
            name=name,
            check_in=dates[0] if len(dates) >= 1 else date.today(),
            check_out=dates[1] if len(dates) >= 2 else date.today(),
            booking_ref=booking_refs[0] if booking_refs else None,
            guests=guests,
            cancelled=cancelled,
        )

    def parse_restaurant_from_email(
        self, subject: str, body: str, sender: str
    ) -> Restaurant | None:
        """Parse restaurant reservation from email."""
        text = f"{subject}\n{body}"

        dates = self.extract_dates(text)
        times = self.extract_times(text)
        booking_refs = self.extract_booking_refs(text)

        # Extract restaurant name from subject/sender
        name = None
        # Pattern: "Restaurant: Reservation Confirmation"
        name_match = re.match(r"([^:]+):\s*Reservation", subject)
        if name_match:
            name = name_match.group(1).strip()
        elif "Accepted:" in subject:
            # Calendar format: "Accepted: Restaurant Reservation @ ..."
            name_match = re.search(r"Accepted:\s*([^@]+)", subject)
            if name_match:
                name = name_match.group(1).replace("Reservation", "").strip()

        if not name:
            return None

        # Extract party size
        party_size = 2
        party_match = re.search(r"(\d+)\s*(?:people|persons?|guests?)", text, re.IGNORECASE)
        if party_match:
            party_size = int(party_match.group(1))

        # Extract special occasion
        special_occasion = None
        occasion_match = re.search(
            r"Special\s+Occasion:\s*([^\n]+)", text, re.IGNORECASE
        )
        if occasion_match:
            special_occasion = occasion_match.group(1).strip()

        return Restaurant(
            name=name,
            date=dates[0] if dates else date.today(),
            time=times[0] if times else "19:00",
            party_size=party_size,
            booking_ref=booking_refs[0] if booking_refs else None,
            special_occasion=special_occasion,
        )

    def parse_cruise_from_email(
        self, subject: str, body: str, sender: str
    ) -> CruiseBooking | None:
        """Parse cruise booking from email."""
        text = f"{subject}\n{body}"

        dates = self.extract_dates(text)
        booking_refs = self.extract_booking_refs(text)
        passengers = self.extract_passenger_names(text)

        # Check for MSC cruise
        if "msc" not in sender.lower() and "msc" not in text.lower():
            return None

        # Extract ship name
        ship_name = None
        ship_match = re.search(r"MSC\s+([A-Za-z]+(?:\s+[A-Za-z]+)?)", text)
        if ship_match:
            ship_name = f"MSC {ship_match.group(1)}"

        # Extract nights
        nights = 7
        nights_match = re.search(r"(\d+)\s*(?:nights?|לילות)", text, re.IGNORECASE)
        if nights_match:
            nights = int(nights_match.group(1))

        if not ship_name or len(dates) < 1:
            return None

        # Calculate end date from nights if only one date provided
        from datetime import timedelta
        start = dates[0]
        end = dates[-1] if len(dates) > 1 else start + timedelta(days=nights)

        return CruiseBooking(
            ship_name=ship_name or "MSC Cruise",
            cruise_line="MSC Cruises",
            start_date=start,
            end_date=end,
            nights=nights,
            booking_refs=booking_refs,
            passengers=passengers,
        )

    def parse_from_pdf_text(
        self, pdf_text: str, filename: str
    ) -> dict[str, list[str] | list[date] | Flight | None]:
        """Parse travel data from PDF extracted text.

        Returns dict with keys: flights, hotels, booking_refs, dates, etc.
        """
        booking_refs = self.extract_booking_refs(pdf_text)
        dates = self.extract_dates(pdf_text)
        flight_numbers = self.extract_flight_numbers(pdf_text)
        airports = self.extract_airports(pdf_text)
        times = self.extract_times(pdf_text)
        passengers = self.extract_passenger_names(pdf_text)

        result: dict[str, list[str] | list[date] | Flight | None] = {
            "booking_refs": booking_refs,
            "dates": dates,
            "flight_numbers": flight_numbers,
            "airports": airports,
            "times": times,
            "passengers": passengers,
            "parsed_flight": None,
        }

        # Try to parse a flight if we have enough data
        if flight_numbers:
            flight = Flight(
                flight_number=flight_numbers[0],
                departure_airport=airports[0] if len(airports) >= 1 else "",
                arrival_airport=airports[1] if len(airports) >= 2 else "",
                departure_date=dates[0] if dates else date.today(),
                departure_time=times[0] if times else None,
                arrival_time=times[1] if len(times) >= 2 else None,
                passengers=passengers,
                booking_ref=booking_refs[0] if booking_refs else None,
            )
            result["parsed_flight"] = flight

        return result
