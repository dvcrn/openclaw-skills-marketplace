"""TripAssembler — merges multiple emails into Trip objects."""

from datetime import date, timedelta

from clawtourism.models import (
    CruiseBooking,
    Flight,
    Hotel,
    Restaurant,
    SourceEmail,
    Trip,
    TripStatus,
)


class TripAssembler:
    """Assembles extracted travel components into Trip objects."""

    def __init__(self) -> None:
        self.trips: list[Trip] = []

    def create_trip_id(self, destination: str, start_date: date) -> str:
        """Create a unique trip ID."""
        dest_slug = destination.lower().replace(" ", "-")
        date_str = start_date.strftime("%b-%Y").lower()
        return f"{dest_slug}-{date_str}"

    def calculate_status(
        self, start_date: date, end_date: date, today: date | None = None
    ) -> TripStatus:
        """Calculate trip status based on dates."""
        if today is None:
            today = date.today()

        if end_date < today:
            return TripStatus.PAST
        elif start_date <= today <= end_date:
            return TripStatus.IN_PROGRESS
        else:
            return TripStatus.UPCOMING

    def find_matching_trip(
        self,
        destination: str,
        event_date: date,
        tolerance_days: int = 7,
    ) -> Trip | None:
        """Find an existing trip that matches the destination and date range."""
        for trip in self.trips:
            # Check destination match (partial)
            if (
                destination.lower() in trip.destination.lower()
                or trip.destination.lower() in destination.lower()
            ):
                # Check date proximity
                if (
                    trip.start_date - timedelta(days=tolerance_days)
                    <= event_date
                    <= trip.end_date + timedelta(days=tolerance_days)
                ):
                    return trip
        return None

    def add_flight(
        self,
        flight: Flight,
        source_email: SourceEmail | None = None,
    ) -> Trip:
        """Add a flight to an existing or new trip."""
        # Infer destination from arrival airport
        destination = self._airport_to_city(flight.arrival_airport)

        trip = self.find_matching_trip(destination, flight.departure_date)
        if not trip:
            # Create new trip
            trip = Trip(
                trip_id=self.create_trip_id(destination, flight.departure_date),
                destination=destination,
                start_date=flight.departure_date,
                end_date=flight.departure_date,
                travellers=flight.passengers.copy(),
            )
            self.trips.append(trip)

        trip.flights.append(flight)
        if flight.booking_ref:
            trip.booking_refs.append(flight.booking_ref)
        if source_email:
            trip.source_emails.append(source_email)

        # Update travellers
        for passenger in flight.passengers:
            if passenger not in trip.travellers:
                trip.travellers.append(passenger)

        return trip

    def add_hotel(
        self,
        hotel: Hotel,
        source_email: SourceEmail | None = None,
    ) -> Trip:
        """Add a hotel to an existing or new trip."""
        # Try to match by city in hotel name
        destination = self._extract_city_from_hotel(hotel.name)

        trip = self.find_matching_trip(destination, hotel.check_in)
        if not trip:
            trip = Trip(
                trip_id=self.create_trip_id(destination, hotel.check_in),
                destination=destination,
                start_date=hotel.check_in,
                end_date=hotel.check_out,
            )
            self.trips.append(trip)

        trip.hotels.append(hotel)
        if hotel.booking_ref:
            trip.booking_refs.append(hotel.booking_ref)
        if source_email:
            trip.source_emails.append(source_email)

        # Expand trip dates if needed
        if hotel.check_in < trip.start_date:
            trip.start_date = hotel.check_in
        if hotel.check_out > trip.end_date:
            trip.end_date = hotel.check_out

        return trip

    def add_restaurant(
        self,
        restaurant: Restaurant,
        source_email: SourceEmail | None = None,
    ) -> Trip:
        """Add a restaurant to an existing trip (or create new)."""
        # Try to infer destination from restaurant name
        destination = self._extract_city_from_restaurant(restaurant.name)

        trip = self.find_matching_trip(destination, restaurant.date)
        if not trip:
            trip = Trip(
                trip_id=self.create_trip_id(destination, restaurant.date),
                destination=destination,
                start_date=restaurant.date,
                end_date=restaurant.date,
            )
            self.trips.append(trip)

        trip.restaurants.append(restaurant)
        if restaurant.booking_ref:
            trip.booking_refs.append(restaurant.booking_ref)
        if source_email:
            trip.source_emails.append(source_email)

        return trip

    def add_cruise(
        self,
        cruise: CruiseBooking,
        source_email: SourceEmail | None = None,
    ) -> Trip:
        """Add a cruise to an existing or new trip."""
        destination = f"Mediterranean Cruise ({cruise.ship_name})"

        trip = self.find_matching_trip("Mediterranean", cruise.start_date)
        if not trip:
            trip = Trip(
                trip_id=self.create_trip_id("cruise", cruise.start_date),
                destination=destination,
                start_date=cruise.start_date,
                end_date=cruise.end_date,
                travellers=cruise.passengers.copy(),
            )
            self.trips.append(trip)

        trip.cruise = cruise
        trip.booking_refs.extend(cruise.booking_refs)
        if source_email:
            trip.source_emails.append(source_email)

        return trip

    def _airport_to_city(self, airport_code: str) -> str:
        """Convert airport code to city name."""
        mapping = {
            "TLV": "Tel Aviv",
            "ATH": "Athens",
            "BCN": "Barcelona",
            "FCO": "Rome",
            "CDG": "Paris",
            "LHR": "London",
            "JFK": "New York",
            "EWR": "New York",
            "LAX": "Los Angeles",
            "MUC": "Munich",
            "FRA": "Frankfurt",
            "AMS": "Amsterdam",
            "VIE": "Vienna",
            "IST": "Istanbul",
            "DXB": "Dubai",
        }
        return mapping.get(airport_code, airport_code)

    def _extract_city_from_hotel(self, hotel_name: str) -> str:
        """Extract city from hotel name."""
        # Common city names in hotel names
        cities = [
            "Athens", "Barcelona", "Rome", "Paris", "London", "New York",
            "Munich", "Amsterdam", "Vienna", "Istanbul", "Dubai", "Milos",
        ]
        for city in cities:
            if city.lower() in hotel_name.lower():
                return city
        # Fallback: use hotel name
        return hotel_name.split()[0] if hotel_name else "Unknown"

    def _extract_city_from_restaurant(self, restaurant_name: str) -> str:
        """Extract city from restaurant name or context."""
        cities = [
            "Athens", "Barcelona", "Rome", "Paris", "London", "New York",
        ]
        for city in cities:
            if city.lower() in restaurant_name.lower():
                return city
        return "Unknown"

    def finalize_trips(self) -> list[Trip]:
        """Finalize all trips: update statuses, dedupe refs."""
        for trip in self.trips:
            # Update status
            trip.status = self.calculate_status(trip.start_date, trip.end_date)

            # Deduplicate booking refs
            trip.booking_refs = list(dict.fromkeys(trip.booking_refs))

            # Deduplicate travellers
            trip.travellers = list(dict.fromkeys(trip.travellers))

            # Filter out cancelled hotels
            trip.hotels = [h for h in trip.hotels if not h.cancelled]

            # Sort flights by date
            trip.flights.sort(key=lambda f: f.departure_date)

            # Sort restaurants by date and time
            trip.restaurants.sort(key=lambda r: (r.date, r.time))

        return self.trips
