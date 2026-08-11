"""Transactional email via plain SMTP - works with Gmail (app password),
SendGrid, Mailgun, or any other provider's SMTP relay, so you're not
locked into one vendor.

Required environment variables:
    SMTP_HOST
    SMTP_PORT           (587 for TLS is standard)
    SMTP_USERNAME
    SMTP_PASSWORD
    SMTP_FROM_EMAIL      the address recipients see as the sender

Nothing here works until those are set - calls raise EmailConfigError
until then, exactly like mpesa.py does for missing Daraja credentials.
"""
import os
import smtplib
from email.message import EmailMessage


class EmailConfigError(Exception):
    pass


def _require_env(*names):
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        raise EmailConfigError(
            f"Missing email environment variables: {', '.join(missing)}. "
            "Set these to a real SMTP provider before sending emails."
        )


def send_email(to, subject, body_text):
    _require_env("SMTP_HOST", "SMTP_PORT", "SMTP_USERNAME", "SMTP_PASSWORD", "SMTP_FROM_EMAIL")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.environ["SMTP_FROM_EMAIL"]
    msg["To"] = to
    msg.set_content(body_text)

    host = os.environ["SMTP_HOST"]
    port = int(os.environ["SMTP_PORT"])

    with smtplib.SMTP(host, port, timeout=15) as server:
        server.starttls()
        server.login(os.environ["SMTP_USERNAME"], os.environ["SMTP_PASSWORD"])
        server.send_message(msg)


def send_password_reset_email(to, reset_url):
    body = (
        "You (or someone using your email) requested a password reset for Nguvu Fit.\n\n"
        f"Reset your password here: {reset_url}\n\n"
        "This link expires in 1 hour. If you didn't request this, you can safely ignore "
        "this email - your password won't change."
    )
    send_email(to, "Reset your Nguvu Fit password", body)