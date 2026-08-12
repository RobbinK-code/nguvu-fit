"""Transactional email via Resend's HTTP API (https://resend.com).

Deliberately NOT using SMTP: Render's free/starter tier blocks outbound
SMTP ports (25/465/587) as an anti-spam measure, so smtplib connections
fail with "Network is unreachable" no matter how correct the credentials
are. An HTTP API call over port 443 isn't affected by that block.

Required environment variables:
    RESEND_API_KEY       from https://resend.com/api-keys
    RESEND_FROM_EMAIL     the address recipients see as the sender - can be
                           "onboarding@resend.dev" for testing without
                           verifying your own domain first

Nothing here works until those are set - calls raise EmailConfigError
until then, exactly like mpesa.py does for missing Daraja credentials.
"""
import os

import requests

RESEND_API_URL = "https://api.resend.com/emails"


class EmailConfigError(Exception):
    pass


class EmailAPIError(Exception):
    """Raised when Resend's API itself rejects the request - carries
    their actual error body instead of a generic HTTP status message."""


def _require_env(*names):
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        raise EmailConfigError(
            f"Missing email environment variables: {', '.join(missing)}. "
            "Set RESEND_API_KEY and RESEND_FROM_EMAIL before sending emails."
        )


def send_email(to, subject, body_text):
    _require_env("RESEND_API_KEY", "RESEND_FROM_EMAIL")

    payload = {
        "from": os.environ["RESEND_FROM_EMAIL"],
        "to": [to],
        "subject": subject,
        "text": body_text,
    }

    resp = requests.post(
        RESEND_API_URL,
        json=payload,
        headers={"Authorization": f"Bearer {os.environ['RESEND_API_KEY']}"},
        timeout=15,
    )

    if not resp.ok:
        try:
            body = resp.json()
        except ValueError:
            body = resp.text
        raise EmailAPIError(f"Resend returned {resp.status_code}: {body}")


def send_password_reset_email(to, reset_url):
    body = (
        "You (or someone using your email) requested a password reset for Nguvu Fit.\n\n"
        f"Reset your password here: {reset_url}\n\n"
        "This link expires in 1 hour. If you didn't request this, you can safely ignore "
        "this email - your password won't change."
    )
    send_email(to, "Reset your Nguvu Fit password", body)