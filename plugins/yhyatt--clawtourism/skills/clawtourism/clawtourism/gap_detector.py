"""GapDetector — finds missing information and generates questions for trips."""

from datetime import date

from clawtourism.models import GapItem, GapSeverity, Trip, TripStatus


class GapDetector:
    """Detects missing information and potential issues in trips."""

    def __init__(self, today: date | None = None) -> None:
        self.today = today or date.today()

    def analyze_trip(self, trip: Trip) -> list[GapItem]:
        """Analyze a trip and return all detected gaps."""
        gaps: list[GapItem] = []

        if trip.status == TripStatus.PAST or trip.status == TripStatus.CANCELLED:
            return gaps  # Don't flag gaps for past/cancelled trips

        # Calculate urgency based on departure date
        days_until = (trip.start_date - self.today).days
        is_urgent = days_until <= 14

        # Check for missing return flight
        gaps.extend(self._check_return_flight(trip, is_urgent))

        # Check for missing accommodation
        gaps.extend(self._check_accommodation(trip, is_urgent))

        # Check for flights without matching hotels
        gaps.extend(self._check_flight_hotel_mismatch(trip))

        # Check document reminders for upcoming trips
        if days_until <= 30:
            gaps.extend(self._check_documents(trip, days_until))

        # Check family/kids considerations
        gaps.extend(self._check_kids_considerations(trip))

        return gaps

    def _check_return_flight(self, trip: Trip, is_urgent: bool) -> list[GapItem]:
        """Check if return flight is missing."""
        gaps: list[GapItem] = []

        outbound_flights = [f for f in trip.flights if not f.is_return]
        return_flights = [f for f in trip.flights if f.is_return]

        if outbound_flights and not return_flights:
            # Check if it's a cruise (return might be included)
            if trip.cruise:
                return gaps

            severity = GapSeverity.URGENT if is_urgent else GapSeverity.WARNING
            gaps.append(
                GapItem(
                    description="Missing return flight",
                    severity=severity,
                    category="flights",
                )
            )

        return gaps

    def _check_accommodation(self, trip: Trip, is_urgent: bool) -> list[GapItem]:
        """Check if accommodation is missing."""
        gaps = []

        has_flights = len(trip.flights) > 0
        has_hotels = len([h for h in trip.hotels if not h.cancelled]) > 0
        has_cruise = trip.cruise is not None

        if has_flights and not has_hotels and not has_cruise:
            severity = GapSeverity.URGENT if is_urgent else GapSeverity.WARNING
            gaps.append(
                GapItem(
                    description="Missing accommodation (have flights but no hotel/cruise)",
                    severity=severity,
                    category="accommodation",
                )
            )

        return gaps

    def _check_flight_hotel_mismatch(self, trip: Trip) -> list[GapItem]:
        """Check if flight and hotel dates match."""
        gaps = []

        for hotel in trip.hotels:
            if hotel.cancelled:
                continue

            # Check if there's a flight arriving before check-in
            arrival_flights = [
                f for f in trip.flights
                if not f.is_return and f.departure_date <= hotel.check_in
            ]
            if not arrival_flights and trip.flights:
                gaps.append(
                    GapItem(
                        description=f"Hotel {hotel.name} check-in on {hotel.check_in} "
                        f"but no matching arrival flight found",
                        severity=GapSeverity.INFO,
                        category="logistics",
                    )
                )

        return gaps

    def _check_documents(self, trip: Trip, days_until: int) -> list[GapItem]:
        """Add document reminders for upcoming trips."""
        gaps = []

        if days_until <= 14:
            gaps.append(
                GapItem(
                    description="Reminder: Check passport validity (>6 months from travel)",
                    severity=GapSeverity.INFO,
                    category="documents",
                )
            )

        # For cruises, add check-in reminder
        if trip.cruise and days_until <= 30:
            gaps.append(
                GapItem(
                    description="Reminder: Complete cruise online check-in",
                    severity=GapSeverity.WARNING,
                    category="documents",
                )
            )

        return gaps

    def _check_kids_considerations(self, trip: Trip) -> list[GapItem]:
        """Check for family/kids related considerations."""
        gaps = []

        # Look for kids in traveller names (heuristic)
        kids_keywords = ["zoe", "lenny"]
        has_kids = any(
            any(kw in t.lower() for kw in kids_keywords)
            for t in trip.travellers
        )

        if has_kids or trip.cruise:  # Cruise emails mentioned kids
            if trip.cruise:
                gaps.append(
                    GapItem(
                        description="Family travel: Confirm kids club booking if needed",
                        severity=GapSeverity.INFO,
                        category="kids",
                    )
                )
                gaps.append(
                    GapItem(
                        description="Family travel: Check stroller policy for cruise",
                        severity=GapSeverity.INFO,
                        category="kids",
                    )
                )

        return gaps

    def detect_all_gaps(self, trips: list[Trip]) -> dict[str, list[GapItem]]:
        """Analyze all trips and return gaps organized by trip_id."""
        result = {}
        for trip in trips:
            gaps = self.analyze_trip(trip)
            trip.gaps = gaps  # Also update the trip object
            result[trip.trip_id] = gaps
        return result
