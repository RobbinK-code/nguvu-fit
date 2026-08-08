import { useState, useRef, useEffect } from "react";
import { useAuth } from "../lib/AuthContext";
import { api } from "../lib/api";
import PhoneInput, { normalizeLocalNumber, isValidKenyanLocalNumber } from "../components/PhoneInput";
import "./Subscribe.css";

const PLANS = [
  { value: "monthly", label: "Monthly", price: 300, unit: "/ month" },
  { value: "annual", label: "Annual", price: 3000, unit: "/ year", badge: "Best value" },
];

const MONTHLY_PRICE = PLANS.find((p) => p.value === "monthly").price;
const ANNUAL_PRICE = PLANS.find((p) => p.value === "annual").price;
const ANNUAL_SAVINGS_PCT = Math.round((1 - ANNUAL_PRICE / (MONTHLY_PRICE * 12)) * 100);

const PERKS = [
  "Shuffle your weekly plan any time you want something fresh",
  "Train up to 6 days a week, not just 3",
  "Track weight & measurements with real progress charts",
  "Full gym equipment library - every machine for every muscle group",
  "Priority additions to the exercise catalog",
];

const POLL_INTERVAL_MS = 3000;
const POLL_TIMEOUT_MS = 60000;

// idle | sending | waiting | success | failed | error
export default function Subscribe() {
  const { user, refreshUser } = useAuth();
  const [plan, setPlan] = useState("monthly");
  const [country, setCountry] = useState("KE");
  const [localNumber, setLocalNumber] = useState("");
  const [status, setStatus] = useState("idle");
  const [message, setMessage] = useState(null);

  const pollTimer = useRef(null);
  const pollDeadline = useRef(null);

  const isSubscribed = Boolean(user?.has_premium);

  useEffect(() => {
    return () => clearInterval(pollTimer.current);
  }, []);

  function stopPolling() {
    clearInterval(pollTimer.current);
    pollTimer.current = null;
  }

  function pollForResult(checkoutId) {
    pollDeadline.current = Date.now() + POLL_TIMEOUT_MS;

    pollTimer.current = setInterval(async () => {
      if (Date.now() > pollDeadline.current) {
        stopPolling();
        setStatus("failed");
        setMessage(
          "We didn't get a confirmation in time. If you approved the prompt, your subscription " +
            "will activate shortly - otherwise, try again."
        );
        return;
      }

      try {
        const res = await api.paymentStatus(checkoutId);
        if (res.status === "success") {
          stopPolling();
          await refreshUser();
          setStatus("success");
          setMessage("Payment confirmed. You're subscribed.");
        } else if (res.status === "failed") {
          stopPolling();
          setStatus("failed");
          setMessage("Payment wasn't completed - it may have been cancelled or declined.");
        }
        // status === "pending" -> keep polling silently
      } catch {
        // transient network hiccup - keep polling until the deadline
      }
    }, POLL_INTERVAL_MS);
  }

  async function handleSubscribe(e) {
    e.preventDefault();

    if (!isValidKenyanLocalNumber(localNumber)) {
      setStatus("error");
      setMessage("Enter a valid Safaricom number, e.g. 07XX XXX XXX or 01XX XXX XXX.");
      return;
    }

    stopPolling();
    setStatus("sending");
    setMessage(null);
    const normalizedPhone = normalizeLocalNumber("254", localNumber);
    try {
      const res = await api.subscribe({ phone_number: normalizedPhone, plan });
      setStatus("waiting");
      setMessage(null);
      pollForResult(res.checkout_request_id);
    } catch (err) {
      setStatus("error");
      if (err.status === 501) {
        setMessage(
          "M-Pesa isn't configured on the server yet. The site owner needs to add Daraja API credentials."
        );
      } else {
        setMessage(err.message);
      }
    }
  }

  function reset() {
    stopPolling();
    setStatus("idle");
    setMessage(null);
  }

  const busy = status === "sending" || status === "waiting";

  return (
    <div className="container subscribe">
      <p className="mono hero-eyebrow">GO PREMIUM</p>
      <h2>Train without limits.</h2>

      {isSubscribed ? (
        <div className="card subscribe-active">
          <span className="pill pill-active">Active subscription</span>
          <p>
            You're all set until{" "}
            {user.subscription_expires_at
              ? new Date(user.subscription_expires_at).toLocaleDateString()
              : "further notice"}
            .
          </p>
        </div>
      ) : status === "waiting" ? (
        <div className="card subscribe-waiting">
          <div className="pulse-dot" aria-hidden="true" />
          <h3 className="waiting-title">Check your phone</h3>
          <p className="waiting-copy">
            We sent an M-Pesa prompt to{" "}
            <strong>+{normalizeLocalNumber("254", localNumber)}</strong>. Enter your PIN to
            complete the payment - this screen will update automatically.
          </p>
          <button className="btn btn-secondary" onClick={reset}>
            Cancel
          </button>
        </div>
      ) : status === "success" ? (
        <div className="card subscribe-active">
          <span className="pill pill-active">Payment confirmed</span>
          <p>{message}</p>
        </div>
      ) : (
        <div className="subscribe-grid">
          <div className="card">
            <h3 className="perks-title">What you get</h3>
            <ul className="perks-list">
              {PERKS.map((perk) => (
                <li key={perk}>{perk}</li>
              ))}
            </ul>
          </div>

          <form className="card" onSubmit={handleSubscribe}>
            <div className="field">
              <label>Plan</label>
              <div className="pricing-grid">
                {PLANS.map((p) => (
                  <button
                    type="button"
                    key={p.value}
                    className={`pricing-card ${plan === p.value ? "pricing-card-selected" : ""}`}
                    onClick={() => setPlan(p.value)}
                  >
                    {p.badge && <span className="pricing-badge">{p.badge}</span>}
                    <span className="pricing-label">{p.label}</span>
                    <span className="pricing-amount">
                      <span className="mono">KES {p.price.toLocaleString()}</span>
                      <span className="pricing-unit">{p.unit}</span>
                    </span>
                    {p.value === "annual" && (
                      <span className="pricing-savings">Save {ANNUAL_SAVINGS_PCT}% vs monthly</span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            <div className="field">
              <label htmlFor="phone">M-Pesa phone number</label>
              <PhoneInput
                country={country}
                onCountryChange={setCountry}
                localNumber={localNumber}
                onLocalNumberChange={setLocalNumber}
              />
              <p className="field-hint">M-Pesa currently only supports Safaricom Kenya numbers.</p>
            </div>

            <button className="btn btn-primary btn-block" disabled={busy}>
              {status === "sending" ? "Sending prompt…" : "Pay with M-Pesa"}
            </button>

            {message && (
              <p className={status === "error" || status === "failed" ? "error-text" : "saved-text"}>
                {message}
              </p>
            )}
          </form>
        </div>
      )}
    </div>
  );
}
