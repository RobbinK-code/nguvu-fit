"""M-Pesa Daraja API integration (STK Push).

This talks to Safaricom's Daraja API. It needs credentials from
https://developer.safaricom.co.ke - register an app there to get a
Consumer Key/Secret, and a Till/Paybill Shortcode + Passkey (Safaricom
provides a shared sandbox shortcode and passkey for testing).

Required environment variables:
    MPESA_ENV                 "sandbox" or "production"
    MPESA_CONSUMER_KEY
    MPESA_CONSUMER_SECRET
    MPESA_SHORTCODE           Paybill/Till number (sandbox default: 174379)
    MPESA_PASSKEY
    MPESA_CALLBACK_URL        Publicly reachable URL for /payments/callback

Nothing here will work until those are set - calls raise MpesaConfigError
until then.
"""
import base64
import os
from datetime import datetime

import requests

SANDBOX_BASE = "https://sandbox.safaricom.co.ke"
PRODUCTION_BASE = "https://api.safaricom.co.ke"

PLAN_PRICES_KES = {
    "monthly": 300,
    "annual": 3000,
}


class MpesaConfigError(Exception):
    pass


def _base_url():
    return PRODUCTION_BASE if os.environ.get("MPESA_ENV") == "production" else SANDBOX_BASE


def _require_env(*names):
    missing = [n for n in names if not os.environ.get(n)]
    if missing:
        raise MpesaConfigError(
            f"Missing M-Pesa environment variables: {', '.join(missing)}. "
            "Set these from your Safaricom Daraja app before accepting payments."
        )


def get_access_token():
    _require_env("MPESA_CONSUMER_KEY", "MPESA_CONSUMER_SECRET")
    key = os.environ["MPESA_CONSUMER_KEY"]
    secret = os.environ["MPESA_CONSUMER_SECRET"]

    resp = requests.get(
        f"{_base_url()}/oauth/v1/generate?grant_type=client_credentials",
        auth=(key, secret),
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def _password_and_timestamp():
    _require_env("MPESA_SHORTCODE", "MPESA_PASSKEY")
    shortcode = os.environ["MPESA_SHORTCODE"]
    passkey = os.environ["MPESA_PASSKEY"]
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    raw = f"{shortcode}{passkey}{timestamp}"
    password = base64.b64encode(raw.encode()).decode()
    return password, timestamp


def initiate_stk_push(phone_number, amount, account_reference, description):
    """Triggers an STK Push prompt on the user's phone. Returns Safaricom's
    response, which includes CheckoutRequestID / MerchantRequestID to
    reconcile against the callback later."""
    _require_env("MPESA_SHORTCODE", "MPESA_CALLBACK_URL")
    shortcode = os.environ["MPESA_SHORTCODE"]
    callback_url = os.environ["MPESA_CALLBACK_URL"]

    token = get_access_token()
    password, timestamp = _password_and_timestamp()

    payload = {
        "BusinessShortCode": shortcode,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": shortcode,
        "PhoneNumber": phone_number,
        "CallBackURL": callback_url,
        "AccountReference": account_reference,
        "TransactionDesc": description,
    }

    resp = requests.post(
        f"{_base_url()}/mpesa/stkpush/v1/processrequest",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=15,
    )
    resp.raise_for_status()
    return resp.json()


def parse_callback(body):
    """Extracts (checkout_request_id, success, receipt, amount) from a
    Daraja STK callback payload."""
    stk = body.get("Body", {}).get("stkCallback", {})
    checkout_id = stk.get("CheckoutRequestID")
    result_code = stk.get("ResultCode")
    success = result_code == 0

    receipt = None
    amount = None
    if success:
        for item in stk.get("CallbackMetadata", {}).get("Item", []):
            if item.get("Name") == "MpesaReceiptNumber":
                receipt = item.get("Value")
            if item.get("Name") == "Amount":
                amount = item.get("Value")

    return checkout_id, success, receipt, amount
