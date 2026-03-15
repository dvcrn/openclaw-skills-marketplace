"""TripRenderer — renders Trip objects to markdown files."""

from datetime import date

from clawtourism.models import GapSeverity, Trip


class TripRenderer:
    """Renders Trip objects to markdown format."""

    def render(self, trip: Trip) -> str:
        """Render a trip to markdown."""
        lines: list[str] = []

        # Header
        month_year = trip.start_date.strftime("%B %Y")
        lines.append(f"# {trip.destination} — {month_year}")
        lines.append("")

        # Status and key info
        lines.append(f"**Status:** {trip.status.value} {trip.status_emoji}")
        lines.append(
            f"**Dates:** {trip.start_date.strftime('%d %b %Y')} → "
            f"{trip.end_date.strftime('%d %b %Y')} ({trip.nights} nights)"
        )

        if trip.travellers:
            lines.append(f"**Travellers:** {', '.join(trip.travellers)}")

        if trip.booking_refs:
            lines.append(f"**Booking refs:** {', '.join(trip.booking_refs)}")

        lines.append("")

        # Flights
        if trip.flights:
            lines.append("## ✈️ Flights")
            lines.append("")
            lines.append("| Leg | Flight | Date | Departs | Arrives | Passengers |")
            lines.append("|-----|--------|------|---------|---------|------------|")
            for flight in trip.flights:
                leg = "Return" if flight.is_return else "Outbound"
                dep_time = flight.departure_time or "—"
                arr_time = flight.arrival_time or "—"
                passengers = ", ".join(flight.passengers) if flight.passengers else "—"
                route = f"{flight.departure_airport} → {flight.arrival_airport}"
                lines.append(
                    f"| {leg} | {flight.flight_number} | "
                    f"{flight.departure_date.strftime('%d %b')} | "
                    f"{route} {dep_time} | {arr_time} | {passengers} |"
                )
            lines.append("")

        # Accommodation
        active_hotels = [h for h in trip.hotels if not h.cancelled]
        if active_hotels:
            lines.append("## 🏨 Accommodation")
            lines.append("")
            for hotel in active_hotels:
                lines.append(f"### {hotel.name}")
                lines.append(
                    f"- **Dates:** {hotel.check_in.strftime('%d %b')} → "
                    f"{hotel.check_out.strftime('%d %b')}"
                )
                if hotel.booking_ref:
                    lines.append(f"- **Booking ref:** {hotel.booking_ref}")
                if hotel.guests:
                    lines.append(f"- **Guests:** {hotel.guests}")
                if hotel.room_type:
                    lines.append(f"- **Room:** {hotel.room_type}")
                if hotel.price:
                    lines.append(f"- **Price:** {hotel.price}")
                lines.append("")

        # Cruise
        if trip.cruise:
            cruise = trip.cruise
            lines.append("## 🚢 Cruise")
            lines.append("")
            lines.append(f"### {cruise.ship_name}")
            lines.append(f"- **Line:** {cruise.cruise_line}")
            lines.append(
                f"- **Dates:** {cruise.start_date.strftime('%d %b')} → "
                f"{cruise.end_date.strftime('%d %b')} ({cruise.nights} nights)"
            )
            if cruise.booking_refs:
                lines.append(f"- **Booking refs:** {', '.join(cruise.booking_refs)}")
            if cruise.cabin_type:
                lines.append(f"- **Cabin:** {cruise.cabin_type}")
            if cruise.package:
                lines.append(f"- **Package:** {cruise.package}")
            if cruise.passengers:
                lines.append(f"- **Passengers:** {', '.join(cruise.passengers)}")
            if cruise.embark_port:
                lines.append(f"- **Embark:** {cruise.embark_port}")
            if cruise.disembark_port:
                lines.append(f"- **Disembark:** {cruise.disembark_port}")
            if cruise.agent_name:
                agent_info = cruise.agent_name
                if cruise.agent_email:
                    agent_info += f" ({cruise.agent_email})"
                lines.append(f"- **Agent:** {agent_info}")
            lines.append("")

        # Restaurants
        if trip.restaurants:
            lines.append("## 🍽️ Restaurants & Reservations")
            lines.append("")
            for restaurant in trip.restaurants:
                lines.append(f"### {restaurant.name}")
                lines.append(
                    f"- **Date:** {restaurant.date.strftime('%a %d %b')} at {restaurant.time}"
                )
                lines.append(f"- **Party size:** {restaurant.party_size}")
                if restaurant.booking_ref:
                    lines.append(f"- **Booking ref:** {restaurant.booking_ref}")
                if restaurant.special_occasion:
                    lines.append(f"- **Occasion:** {restaurant.special_occasion}")
                if restaurant.phone:
                    lines.append(f"- **Phone:** {restaurant.phone}")
                lines.append("")

        # Gaps / Missing Items
        if trip.gaps:
            lines.append("## ⚠️ Missing / Open Items")
            lines.append("")
            for gap in trip.gaps:
                severity_icon = {
                    GapSeverity.INFO: "ℹ️",
                    GapSeverity.WARNING: "⚠️",
                    GapSeverity.URGENT: "🚨",
                }[gap.severity]
                lines.append(f"- [ ] {severity_icon} {gap.description}")
            lines.append("")

        # Notes
        if trip.notes:
            lines.append("## 📝 Notes")
            lines.append("")
            for note in trip.notes:
                lines.append(f"- {note}")
            lines.append("")

        # Source emails
        if trip.source_emails:
            lines.append("## 📧 Source Emails")
            lines.append("")
            for email in trip.source_emails:
                date_str = email.date.strftime("%d %b %Y")
                lines.append(f"- {email.subject} from {email.sender} on {date_str}")
            lines.append("")

        # Footer
        lines.append("---")
        lines.append(f"*Generated by Kai Travel Bot on {date.today().strftime('%Y-%m-%d')}*")

        return "\n".join(lines)

    def get_filename(self, trip: Trip) -> str:
        """Generate filename for trip markdown."""
        return f"{trip.trip_id}.md"
