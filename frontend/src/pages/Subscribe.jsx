import { useState, useRef, useEffect } from "react";
import { useAuth } from "../lib/AuthContext";
import { api } from "../lib/api";
import "./Subscribe.css";

const PLANS = [
  { value: "monthly", label: "Monthly", price: "KES 300 / month" },
  { value: "annual", label: "Annual", price: "KES 3,000 / year" },
];

const PERKS = [
  "Refreshable weekly plans (skip a stale week any time)",
  "Full workout history & progress stats",
  "Priority additions to the exercise catalog",
];

const POLL_INTERVAL_MS = 3000;
const POLL_TIMEOUT_MS = 60000;

// idle | sending | waiting | success | failed | error
export default function Subscribe() {
  const { user, refreshUser } = useAuth();
  const [plan, setPlan] = useState("monthly");
  const [phone, setPhone] = useState("2547");
  const [status, setStatus] = useState("idle");
  const [message, setMessage] = useState(null);

  const pollTimer = useRef(null);
  const pollDeadline = useRef(null);

  const isSubscribed = user?.subscription_status === "active";

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
    stopPolling();
    setStatus("sending");
    setMessage(null);
    try {
      const res = await api.subscribe({ phone_number: phone, plan });
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
            We sent an M-Pesa prompt to <strong>{phone}</strong>. Enter your PIN to complete the
            payment - this screen will update automatically.
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
              <div className="chip-row">
                {PLANS.map((p) => (
                  <button
                    type="button"
                    key={p.value}
                    className={`chip ${plan === p.value ? "chip-on" : ""}`}
                    onClick={() => setPlan(p.value)}
                  >
                    {p.label}
                  </button>
                ))}
              </div>
              <p className="plan-price mono">{PLANS.find((p) => p.value === plan)?.price}</p>
            </div>

            <div className="field">
              <label htmlFor="phone">M-Pesa phone number</label>
              <input
                id="phone"
                required
                pattern="2547\d{8}"
                title="Format: 2547XXXXXXXX"
                placeholder="2547XXXXXXXX"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
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
