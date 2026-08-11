import { useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import "./Auth.css";

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState("idle"); // idle | sending | sent | error
  const [error, setError] = useState(null);

  async function handleSubmit(e) {
    e.preventDefault();
    setStatus("sending");
    setError(null);
    try {
      await api.forgotPassword(email);
      setStatus("sent");
    } catch (err) {
      setStatus("error");
      setError(err.message);
    }
  }

  return (
    <div className="auth-page container">
      <div className="auth-card card">
        <h2 className="auth-title">Reset your password</h2>

        {status === "sent" ? (
          <p className="saved-text">
            If an account exists for that email, we've sent a link to reset your password. It
            expires in 1 hour.
          </p>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="field">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            {error && <p className="error-text">{error}</p>}
            <button className="btn btn-primary btn-block" disabled={status === "sending"}>
              {status === "sending" ? "Sending…" : "Send reset link"}
            </button>
          </form>
        )}

        <p className="auth-switch">
          <Link to="/login">Back to log in</Link>
        </p>
      </div>
    </div>
  );
}