"""Data models for travel bookings."""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum


class TripStatus(Enum):
    """Status of a trip."""

    UPCOMING = "UPCOMING"
    IN_PROGRESS = "IN_PROGRESS"
    PAST = "PAST"
    CANCELLED = "CANCELLED"


class GapSeverity(Enum):
    """Severity level for gaps/missing items."""

    INFO = "INFO"
    WARNING = "WARNING"
    URGENT = "URGENT"


@dataclass
class SourceEmail:
    """Reference to a source email."""

    message_id: str
    thread_id: str
    subject: str
    sender: str
    date: datetime
    snippet: str = ""


@dataclass
class Flight:
    """A flight leg."""

    flight_number: str
    departure_airport: str
    arrival_airport: str
    departure_date: date
    departure_time: str | None = None  # HH:MM
    arrival_time: str | None = None  # HH:MM
    passengers: list[str] = field(default_factory=list)
    booking_ref: str | None = None
    airline: str | None = None
    seat: str | None = None
    is_return: bool = False


@dataclass
class Hotel:
    """A hotel booking."""

    name: str
    check_in: date
    check_out: date
    booking_ref: str | None = None
    address: str | None = None
    guests: int = 2
    room_type: str | None = None
    price: str | None = None
    cancelled: bool = False


@dataclass
class Restaurant:
    """A restaurant reservation."""

    name: str
    date: date
    time: str  # HH:MM
    party_size: int = 2
    booking_ref: str | None = None
    phone: str | None = None
    address: str | None = None
    special_occasion: str | None = None


@dataclass
class CruiseBooking:
    """A cruise booking."""

    ship_name: str
    cruise_line: str
    start_date: date
    end_date: date
    nights: int
    booking_refs: list[str] = field(default_factory=list)
    cabin_type: str | None = None
    passengers: list[str] = field(default_factory=list)
    itinerary: list[str] = field(default_factory=list)  # List of ports
    embark_port: str | None = None
    disembark_port: str | None = None
    package: str | None = None  # e.g., "drinks package"
    agent_name: str | None = None
    agent_email: str | None = None


@dataclass
class GapItem:
    """A missing item or concern for a trip."""

    description: str
    severity: GapSeverity = GapSeverity.WARNING
    category: str = "general"  # flights, accommodation, documents, kids, etc.


@dataclass
class Trip:
    """A complete trip with all components."""

    trip_id: str  # Unique identifier (e.g., "athens-feb-2026")
    destination: str
    start_date: date
    end_date: date
    status: TripStatus = TripStatus.UPCOMING
    travellers: list[str] = field(default_factory=list)
    flights: list[Flight] = field(default_factory=list)
    hotels: list[Hotel] = field(default_factory=list)
    restaurants: list[Restaurant] = field(default_factory=list)
    cruise: CruiseBooking | None = None
    gaps: list[GapItem] = field(default_factory=list)
    source_emails: list[SourceEmail] = field(default_factory=list)
    booking_refs: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)

    @property
    def nights(self) -> int:
        """Calculate the number of nights."""
        return (self.end_date - self.start_date).days

    @property
    def status_emoji(self) -> str:
        """Get emoji for status."""
        return {
            TripStatus.UPCOMING: "⚠️",
            TripStatus.IN_PROGRESS: "🟡",
            TripStatus.PAST: "✅",
            TripStatus.CANCELLED: "❌",
        }[self.status]

    @property
    def has_urgent_gaps(self) -> bool:
        """Check if there are any urgent gaps."""
        return any(g.severity == GapSeverity.URGENT for g in self.gaps)
