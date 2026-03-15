"""ClawHub example — generate an OG image."""
from socialcard import SocialCard

SocialCard("og").title("Hello World").subtitle("My first social card").render("og.png")
