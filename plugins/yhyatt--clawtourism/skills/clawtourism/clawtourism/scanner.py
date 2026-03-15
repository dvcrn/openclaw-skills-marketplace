"""EmailScanner — scans Gmail for travel emails via gog CLI.

Design: Label-first scanning. Only reads from label:Trips.
No broad Gmail search needed — the user manually labels travel-related emails.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from clawtourism.models import SourceEmail


# The magic label — we ONLY scan this
TRAVEL_LABEL = "Trips"


@dataclass
class EmailAttachment:
    """A Gmail attachment."""

    filename: str
    mime_type: str
    size: int
    attachment_id: str
    data: bytes | None = None  # Populated when downloaded


@dataclass
class ForwardedEmail:
    """A nested forwarded email extracted from email body."""

    original_sender: str
    original_subject: str
    original_date: str
    body: str


@dataclass
class EmailMessage:
    """A Gmail message."""

    id: str
    thread_id: str
    date: datetime
    sender: str
    subject: str
    labels: list[str]
    body: str = ""
    attachments: list[EmailAttachment] = field(default_factory=list)
    forwarded_emails: list[ForwardedEmail] = field(default_factory=list)


@dataclass
class UnassignedEmail:
    """An email that couldn't be assigned to a trip."""

    message_id: str
    thread_id: str
    subject: str
    sender: str
    date: str  # ISO format
    snippet: str
    reason: str  # Why it couldn't be assigned


class EmailScanner:
    """Scans Gmail for travel-related emails using gog CLI.

    Design: Label-first scanning.
    - ONLY reads from label:Trips
    - No broad subject/sender searches
    - User manually labels all travel emails
    """

    # Known travel sender domain suffixes (use .endswith() for subdomain matching)
    TRAVEL_SENDER_DOMAINS = [
        # Airlines
        "wizzair.com",
        "notifications.wizzair.com",
        "elal.co.il",
        "ryanair.com",
        "lufthansa.com",
        "aegean.com",
        "aerocrs.com",  # Blue Bird Airways tickets
        # Hotels/Accommodation
        "booking.com",
        "airbnb.com",
        "reserve-online.net",
        "expedia.com",
        # Cruises
        "msc.com",
        "msccruises.com",
        # Restaurant reservations
        "i-host.gr",
        # Travel agents
        "amsalem.com",  # Israeli travel agent (El Al bookings via Moshe Timsit)
        # Club Med (multiple subdomains)
        "clubmed.com",
        "infos.clubmed.com",
        "contact.clubmed.com",
        "email.clubmed.com",
    ]

    # Forwarded email pattern
    FORWARDED_PATTERN = re.compile(
        r"-{5,}\s*Forwarded message\s*-{5,}\s*"
        r"(?:From:\s*(.+?)(?:\n|$))?"
        r"(?:Date:\s*(.+?)(?:\n|$))?"
        r"(?:Subject:\s*(.+?)(?:\n|$))?"
        r"(?:To:\s*(.+?)(?:\n|$))?"
        r"(.*)",
        re.IGNORECASE | re.DOTALL,
    )

    # Alternative forwarded pattern (Hebrew/other formats)
    ALT_FORWARDED_PATTERNS = [
        # "---------- Forwarded message ---------"
        re.compile(
            r"-+\s*Forwarded message\s*-+\s*\n"
            r"From:\s*(?P<from>.+?)\n"
            r"Date:\s*(?P<date>.+?)\n"
            r"Subject:\s*(?P<subject>.+?)\n"
            r"To:\s*(?P<to>.+?)\n\n"
            r"(?P<body>.*)",
            re.IGNORECASE | re.DOTALL,
        ),
        # Hebrew forwarded pattern
        re.compile(
            r"הודעה מועברת\s*\n"
            r"מאת:\s*(?P<from>.+?)\n"
            r"תאריך:\s*(?P<date>.+?)\n"
            r"נושא:\s*(?P<subject>.+?)\n",
            re.IGNORECASE,
        ),
        # Simple "Fwd:" detection for self-forwards
        re.compile(r"^Fwd:\s*(.+)", re.IGNORECASE),
    ]

    def __init__(
        self,
        account: str = "hyatt.yonatan@gmail.com",
        keyring_password: str | None = None,
    ) -> None:
        self.account = account
        self.keyring_password = keyring_password or os.environ.get(
            "GOG_KEYRING_PASSWORD", "kai-gog-keyring"
        )

    def _run_gog(self, args: list[str]) -> str:
        """Run gog CLI command and return output."""
        env = os.environ.copy()
        env["GOG_KEYRING_PASSWORD"] = self.keyring_password

        cmd = ["gog"] + args + ["--account", self.account]
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env,
        )
        if result.returncode != 0:
            raise RuntimeError(f"gog command failed: {result.stderr}")
        return result.stdout

    def _run_gog_json(self, args: list[str]) -> dict[str, Any]:
        """Run gog CLI command and parse JSON output."""
        output = self._run_gog(args + ["--json"])
        result: dict[str, Any] = json.loads(output)
        return result

    def search_trips_label(self, max_results: int = 100, days: int = 365) -> list[EmailMessage]:
        """Search for messages with the Trips label.

        This is the ONLY entry point for scanning. We never do broad searches.
        """
        query = f"label:{TRAVEL_LABEL} newer_than:{days}d"
        return self._search_messages(query, max_results)

    def _search_messages(self, query: str, max_results: int = 50) -> list[EmailMessage]:
        """Search for messages matching query."""
        output = self._run_gog([
            "gmail", "messages", "search",
            query,
            "--max", str(max_results),
            "--json",
        ])

        data = json.loads(output)
        messages = []
        for msg in data.get("messages", []):
            try:
                dt = datetime.strptime(msg["date"], "%Y-%m-%d %H:%M")
            except (ValueError, KeyError):
                dt = datetime.now()

            messages.append(EmailMessage(
                id=msg["id"],
                thread_id=msg["threadId"],
                date=dt,
                sender=msg.get("from", ""),
                subject=msg.get("subject", ""),
                labels=msg.get("labels", []),
            ))
        return messages

    def get_thread(self, thread_id: str) -> str:
        """Get full thread content as text."""
        return self._run_gog([
            "gmail", "thread", "show",
            thread_id,
        ])

    def get_thread_json(self, thread_id: str) -> dict[str, Any]:
        """Get full thread content as JSON (includes attachment metadata)."""
        return self._run_gog_json([
            "gmail", "thread", "show",
            thread_id,
        ])

    def is_known_travel_sender(self, sender: str) -> bool:
        """Check if sender is from a known travel domain.

        Uses suffix matching to handle subdomains:
        - infos.clubmed.com matches clubmed.com
        - noreply@notifications.wizzair.com matches wizzair.com
        """
        # Extract domain from sender email
        email_match = re.search(r"<([^>]+)>", sender)
        if email_match:
            email = email_match.group(1)
        else:
            email = sender

        domain_match = re.search(r"@([^\s>]+)", email)
        if not domain_match:
            return False

        sender_domain = domain_match.group(1).lower()

        # Suffix matching for subdomain support
        for known_domain in self.TRAVEL_SENDER_DOMAINS:
            if sender_domain == known_domain or sender_domain.endswith("." + known_domain):
                return True

        return False

    def extract_forwarded_emails(self, body: str) -> list[ForwardedEmail]:
        """Extract forwarded email chains from body.

        Many booking confirmations arrive as forwarded emails:
        - Zeev Hyatt forwards MSC bookings
        - Rotem Iram forwarded El Al booking
        - Yonatan self-forwards

        This extracts the nested From/Subject/Date/Body from forwarded chains.
        """
        forwarded = []

        # Try main forwarded pattern
        match = self.FORWARDED_PATTERN.search(body)
        if match:
            from_addr = match.group(1) or ""
            date_str = match.group(2) or ""
            subject = match.group(3) or ""
            nested_body = match.group(5) or ""

            if from_addr or subject:
                forwarded.append(ForwardedEmail(
                    original_sender=from_addr.strip(),
                    original_subject=subject.strip(),
                    original_date=date_str.strip(),
                    body=nested_body.strip(),
                ))

        # Try alternative patterns
        for pattern in self.ALT_FORWARDED_PATTERNS:
            for match in pattern.finditer(body):
                groups = match.groupdict() if hasattr(match, 'groupdict') else {}
                if groups:
                    forwarded.append(ForwardedEmail(
                        original_sender=groups.get("from", "").strip(),
                        original_subject=groups.get("subject", "").strip(),
                        original_date=groups.get("date", "").strip(),
                        body=groups.get("body", "").strip(),
                    ))

        return forwarded

    def fetch_thread_body(self, msg: EmailMessage) -> EmailMessage:
        """Fetch the full thread body for a message.

        Also extracts forwarded email chains.
        """
        try:
            body = self.get_thread(msg.thread_id)
            msg.body = body

            # Extract forwarded emails
            msg.forwarded_emails = self.extract_forwarded_emails(body)

            # Try to get JSON for attachment info
            try:
                thread_json = self.get_thread_json(msg.thread_id)
                msg.attachments = self._extract_attachments_from_json(thread_json)
            except Exception:
                pass

        except RuntimeError:
            msg.body = ""

        return msg

    def _extract_attachments_from_json(self, thread_json: dict[str, Any]) -> list[EmailAttachment]:
        """Extract attachment metadata from thread JSON."""
        attachments = []

        # Navigate through thread messages
        for message in thread_json.get("messages", []):
            payload = message.get("payload", {})
            parts = payload.get("parts", [])

            for part in parts:
                filename = part.get("filename", "")
                if filename and part.get("body", {}).get("attachmentId"):
                    attachments.append(EmailAttachment(
                        filename=filename,
                        mime_type=part.get("mimeType", ""),
                        size=part.get("body", {}).get("size", 0),
                        attachment_id=part["body"]["attachmentId"],
                    ))

        return attachments

    def scan_all_travel_emails(self) -> list[EmailMessage]:
        """Scan all emails with the Trips label.

        This is the main entry point. We ONLY read from label:Trips.
        """
        return self.search_trips_label(max_results=100, days=365)

    def to_source_email(self, msg: EmailMessage) -> SourceEmail:
        """Convert EmailMessage to SourceEmail model."""
        from clawtourism.models import SourceEmail  # noqa: F811

        return SourceEmail(
            message_id=msg.id,
            thread_id=msg.thread_id,
            subject=msg.subject,
            sender=msg.sender,
            date=msg.date,
            snippet=msg.body[:200] if msg.body else "",
        )


class UnassignedEmailStore:
    """Stores unassigned emails for later manual resolution."""

    def __init__(self, base_dir: str | Path) -> None:
        self.base_dir = Path(base_dir)
        self.inbox_dir = self.base_dir / "_inbox"
        self.inbox_dir.mkdir(parents=True, exist_ok=True)
        self.unassigned_file = self.inbox_dir / "unassigned.jsonl"

    def add_unassigned(self, email: UnassignedEmail) -> None:
        """Add an unassigned email to the store."""
        record = {
            "message_id": email.message_id,
            "thread_id": email.thread_id,
            "subject": email.subject,
            "sender": email.sender,
            "date": email.date,
            "snippet": email.snippet,
            "reason": email.reason,
            "added_at": datetime.now().isoformat(),
        }

        with open(self.unassigned_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def get_unassigned(self) -> list[UnassignedEmail]:
        """Get all unassigned emails."""
        if not self.unassigned_file.exists():
            return []

        emails = []
        with open(self.unassigned_file, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    emails.append(UnassignedEmail(
                        message_id=record["message_id"],
                        thread_id=record["thread_id"],
                        subject=record["subject"],
                        sender=record["sender"],
                        date=record["date"],
                        snippet=record.get("snippet", ""),
                        reason=record.get("reason", ""),
                    ))
        return emails

    def resolve(self, email_id: str, trip_id: str) -> bool:
        """Mark an email as resolved and assigned to a trip.

        Returns True if email was found and resolved.
        """
        if not self.unassigned_file.exists():
            return False

        # Read all, filter out the resolved one
        remaining = []
        resolved = False

        with open(self.unassigned_file, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    record = json.loads(line)
                    if record["message_id"] == email_id:
                        resolved = True
                        # Write to resolved log
                        self._log_resolution(record, trip_id)
                    else:
                        remaining.append(line)

        # Rewrite unassigned file without resolved email
        with open(self.unassigned_file, "w", encoding="utf-8") as f:
            f.writelines(remaining)

        return resolved

    def _log_resolution(self, record: dict[str, Any], trip_id: str) -> None:
        """Log a resolution for audit purposes."""
        resolved_file = self.inbox_dir / "resolved.jsonl"
        record["resolved_to"] = trip_id
        record["resolved_at"] = datetime.now().isoformat()

        with open(resolved_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
