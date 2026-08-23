from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify
from marshmallow import ValidationError

from config import db
from models import Payment, User
from schemas import stk_push_schema
from decorators import login_required
import mpesa

payments_bp = Blueprint("payments", __name__, url_prefix="/payments")

PLAN_DURATIONS = {
    "monthly": timedelta(days=30),
    "annual": timedelta(days=365),
}


@payments_bp.post("/subscribe")
@login_required
def subscribe(user):
    json_data = request.get_json(silent=True) or {}
    try:
        data = stk_push_schema.load(json_data)
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400

    plan = data["plan"]
    amount = mpesa.PLAN_PRICES_KES[plan]

    payment = Payment(user_id=user.id, amount=amount, phone_number=data["phone_number"], plan=plan)
    db.session.add(payment)
    db.session.commit()

    try:
        result = mpesa.initiate_stk_push(
            phone_number=data["phone_number"],
            amount=amount,
            account_reference=f"NguvuFit-{user.id}",
            description=f"Nguvu Fit {plan} subscription",
        )
    except mpesa.MpesaConfigError as err:
        return jsonify({"error": str(err)}), 501
    except mpesa.MpesaAPIError as err:
        payment.status = "failed"
        db.session.commit()
        return jsonify({"error": str(err)}), 502
    except Exception as err:
        payment.status = "failed"
        db.session.commit()
        return jsonify({"error": f"Could not reach M-Pesa: {err}"}), 502

    payment.checkout_request_id = result.get("CheckoutRequestID")
    payment.merchant_request_id = result.get("MerchantRequestID")
    db.session.commit()

    return jsonify(
        {
            "message": "STK Push sent. Approve the prompt on your phone to complete payment.",
            "checkout_request_id": payment.checkout_request_id,
        }
    ), 202


REFERRAL_REWARD_DAYS = 7


def _extend_premium(user, days):
    """Adds `days` of premium on top of whatever the user already has,
    rather than overwriting a longer existing subscription."""
    now = datetime.utcnow()
    base = user.subscription_expires_at if (user.subscription_expires_at and user.subscription_expires_at > now) else now
    user.subscription_status = "active"
    user.subscription_expires_at = base + timedelta(days=days)


@payments_bp.post("/callback")
def mpesa_callback():
    """Public webhook Safaricom calls once the STK push is approved/declined.
    Configure this URL as MPESA_CALLBACK_URL in your Daraja app settings."""
    body = request.get_json(silent=True) or {}
    checkout_id, success, receipt, amount = mpesa.parse_callback(body)

    payment = Payment.query.filter_by(checkout_request_id=checkout_id).first()
    if not payment:
        return jsonify({"error": "Unknown checkout_request_id."}), 404

    if success:
        is_first_successful_payment = (
            Payment.query.filter_by(user_id=payment.user_id, status="success").count() == 0
        )

        payment.status = "success"
        payment.mpesa_receipt = receipt
        payment.user.subscription_status = "active"
        payment.user.subscription_expires_at = datetime.utcnow() + PLAN_DURATIONS[payment.plan]

        if is_first_successful_payment and payment.user.referred_by_id and not payment.user.referral_reward_granted:
            referrer = db.session.get(User, payment.user.referred_by_id)
            if referrer:
                _extend_premium(referrer, REFERRAL_REWARD_DAYS)
                _extend_premium(payment.user, REFERRAL_REWARD_DAYS)
                payment.user.referral_reward_granted = True
    else:
        payment.status = "failed"

    db.session.commit()
    return jsonify({"ResultCode": 0, "ResultDesc": "Accepted"}), 200


@payments_bp.get("/status/<checkout_request_id>")
@login_required
def payment_status(user, checkout_request_id):
    payment = Payment.query.filter_by(
        checkout_request_id=checkout_request_id, user_id=user.id
    ).first()
    if not payment:
        return jsonify({"error": "Payment not found."}), 404
    return jsonify({"status": payment.status, "plan": payment.plan}), 200
