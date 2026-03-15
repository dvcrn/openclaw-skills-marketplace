"""PdfExtractor — extracts text from PDF attachments.

Many booking confirmations have ALL data in PDF attachments:
- El Al: 8FL7BG.pdf (booking confirmation)
- Club Med: CTR-Voucher_*.pdf (French + Hebrew voucher)
- Blue Bird: e-ticket PDF
"""

from __future__ import annotations

import base64
import io
import re
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from clawtourism.scanner import EmailAttachment


@dataclass
class PdfContent:
    """Extracted content from a PDF."""

    filename: str
    text: str
    pages: int
    is_travel_document: bool


class PdfExtractor:
    """Extracts text from PDF attachments for travel booking detection."""

    # Keywords indicating travel-related PDF
    TRAVEL_KEYWORDS = [
        # Booking/reservation
        "booking", "reservation", "confirmation", "itinerary",
        "e-ticket", "eticket", "ticket", "voucher",
        # Flight
        "flight", "departure", "arrival", "passenger", "pnr", "boarding",
        # Hotel
        "check-in", "check-out", "hotel", "accommodation", "guest",
        # Cruise
        "cruise", "cabin", "embark", "disembark", "port",
        # Hebrew
        "הזמנה", "טיסה", "נוסע", "מלון", "אישור",
        # French (for Club Med)
        "réservation", "vol", "passager", "hébergement",
    ]

    def extract_text_from_bytes(self, pdf_bytes: bytes, filename: str = "") -> PdfContent:
        """Extract text from PDF bytes.

        Tries pdfplumber first (better for structured docs), falls back to pypdf.
        """
        text = ""
        pages = 0

        # Try pdfplumber first
        try:
            import pdfplumber

            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                pages = len(pdf.pages)
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                text = "\n\n".join(text_parts)
        except Exception:
            pass

        # Fall back to pypdf if pdfplumber failed
        if not text:
            try:
                from pypdf import PdfReader

                reader = PdfReader(io.BytesIO(pdf_bytes))
                pages = len(reader.pages)
                text_parts = []
                for pypdf_page in reader.pages:
                    page_text = pypdf_page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                text = "\n\n".join(text_parts)
            except Exception:
                pass

        is_travel = self._is_travel_document(text, filename)

        return PdfContent(
            filename=filename,
            text=text,
            pages=pages,
            is_travel_document=is_travel,
        )

    def extract_text_from_base64(self, b64_data: str, filename: str = "") -> PdfContent:
        """Extract text from base64-encoded PDF data."""
        # Handle data: URL prefix
        if b64_data.startswith("data:"):
            # data:application/pdf;base64,XXXXXXX
            _, b64_data = b64_data.split(",", 1)

        pdf_bytes = base64.b64decode(b64_data)
        return self.extract_text_from_bytes(pdf_bytes, filename)

    def extract_from_attachment(self, attachment: EmailAttachment) -> PdfContent | None:
        """Extract text from an EmailAttachment if it's a PDF with data."""
        if not attachment.filename.lower().endswith(".pdf"):
            return None

        if not attachment.data:
            return None

        return self.extract_text_from_bytes(attachment.data, attachment.filename)

    def _is_travel_document(self, text: str, filename: str) -> bool:
        """Check if the PDF appears to be a travel document."""
        combined = (text + " " + filename).lower()

        # Count keyword matches
        matches = sum(1 for kw in self.TRAVEL_KEYWORDS if kw.lower() in combined)

        # Need at least 2 keyword matches to be considered travel
        return matches >= 2

    def extract_booking_ref_from_filename(self, filename: str) -> str | None:
        """Extract booking reference from PDF filename.

        Examples:
        - 8FL7BG.pdf → 8FL7BG
        - CTR-Voucher_MR HYATT YONATAN_20251027_074326.pdf → extract from content instead
        """
        # Pattern for alphanumeric booking codes
        match = re.match(r"^([A-Z0-9]{5,8})\.pdf$", filename, re.IGNORECASE)
        if match:
            return match.group(1).upper()

        return None
