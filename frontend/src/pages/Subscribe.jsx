import { useState } from "react";
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

export default function Subscribe() {
  const { user, refreshUser } = useAuth();
  const [plan, setPlan] = useState("monthly");
  const [phone, setPhone] = useState("2547");
  const [status, setStatus] = useState("idle"); // idle | sending | sent | error
  const [message, setMessage] = useState(null);

  const isSubscribed = user?.subscription_status === "active";

  async function handleSubscribe(e) {
    e.preventDefault();
    setStatus("sending");
    setMessage(null);
    try {
      const res = await api.subscribe({ phone_number: phone, plan });
      setStatus("sent");
      setMessage(res.message);
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

            <button className="btn btn-primary btn-block" disabled={status === "sending"}>
              {status === "sending" ? "Sending prompt…" : "Pay with M-Pesa"}
            </button>

            {message && (
              <p className={status === "error" ? "error-text" : "saved-text"}>{message}</p>
            )}
          </form>
        </div>
      )}
    </div>
  );
}
