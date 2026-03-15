"""clawtourism: From confirmation email to curated itinerary — automatically."""

from clawtourism.assembler import TripAssembler
from clawtourism.extractor import TripExtractor
from clawtourism.gap_detector import GapDetector
from clawtourism.models import (
    CruiseBooking,
    Flight,
    GapItem,
    GapSeverity,
    Hotel,
    Restaurant,
    SourceEmail,
    Trip,
    TripStatus,
)
from clawtourism.pdf_extractor import PdfExtractor
from clawtourism.renderer import TripRenderer
from clawtourism.scanner import (
    TRAVEL_LABEL,
    EmailAttachment,
    EmailMessage,
    EmailScanner,
    ForwardedEmail,
    UnassignedEmail,
    UnassignedEmailStore,
)
from clawtourism.store import TripStore

__all__ = [
    "TripAssembler", "TripExtractor", "GapDetector", "PdfExtractor",
    "TripRenderer", "TripStore", "EmailScanner", "TripStore",
    "Trip", "Flight", "Hotel", "Restaurant", "CruiseBooking",
    "GapItem", "GapSeverity", "TripStatus", "SourceEmail",
    "TRAVEL_LABEL", "EmailAttachment", "EmailMessage",
    "ForwardedEmail", "UnassignedEmail", "UnassignedEmailStore",
]
