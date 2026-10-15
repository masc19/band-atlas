"""band-atlas — a personalised scene atlas engine for developing artists.

Facts are researched once per lane / city / country and cached; judgments are
computed per artist profile. See README.md.
"""

__version__ = "0.1.0"

CATEGORIES = [
    "labels", "distributors", "collabs", "open_stages", "festivals",
    "showcases", "bookers", "promoters", "agents",
]
RESERVED = ["venues", "markets"]
