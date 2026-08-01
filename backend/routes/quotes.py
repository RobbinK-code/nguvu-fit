import random
from datetime import date

from flask import Blueprint, jsonify

from models import Quote
from decorators import login_required

quotes_bp = Blueprint("quotes", __name__, url_prefix="/quotes")


@quotes_bp.get("/today")
@login_required
def quote_of_the_day(user):
    quotes = Quote.query.all()
    if not quotes:
        return jsonify({"text": "Show up. That's the whole first step.", "author": None}), 200

    # Deterministic per user per day, so it doesn't change on refresh but
    # still differs between users and rotates daily.
    rng = random.Random(f"{user.id}-{date.today().isoformat()}")
    quote = rng.choice(quotes)
    return jsonify({"id": quote.id, "text": quote.text, "author": quote.author}), 200
