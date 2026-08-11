import { useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import { api } from "../lib/api";
import PasswordField from "../components/PasswordField";
import "./Auth.css";

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";
  const navigate = useNavigate();

  const [form, setForm] = useState({ password: "", confirmPassword: "" });
  const [status, setStatus] = useState("idle"); // idle | saving | done | error
  const [error, setError] = useState(null);

  const showMismatch = form.confirmPassword.length > 0 && form.password !== form.confirmPassword;
  const showMatch = form.confirmPassword.length > 0 && form.password === form.confirmPassword;

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    if (!token) {
      setError("This reset link is missing its token - please use the link from your email.");
      return;
    }
    if (form.password !== form.confirmPassword) {
      setError("Passwords don't match.");
      return;
    }

    setStatus("saving");
    try {
      await api.resetPassword(token, form.password);
      setStatus("done");
      setTimeout(() => navigate("/login"), 2000);
    } catch (err) {
      setStatus("error");
      setError(err.message);
    }
  }

  if (!token) {
    return (
      <div className="auth-page container">
        <div className="auth-card card">
          <h2 className="auth-title">Invalid reset link</h2>
          <p className="error-text">
            This link is missing its reset token. Request a new one below.
          </p>
          <p className="auth-switch">
            <Link to="/forgot-password">Request a new reset link</Link>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-page container">
      <div className="auth-card card">
        <h2 className="auth-title">Set a new password</h2>

        {status === "done" ? (
          <p className="saved-text">Password updated. Redirecting you to log in…</p>
        ) : (
          <form onSubmit={handleSubmit}>
            <PasswordField
              id="password"
              label="New password (min 8 characters)"
              minLength={8}
              autoComplete="new-password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
            <PasswordField
              id="confirmPassword"
              label="Confirm new password"
              minLength={8}
              autoComplete="new-password"
              value={form.confirmPassword}
              onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
            />
            {(showMismatch || showMatch) && (
              <p className={`password-match-hint ${showMismatch ? "mismatch" : "match"}`}>
                {showMismatch ? "Passwords don't match yet." : "Passwords match."}
              </p>
            )}
            {error && <p className="error-text">{error}</p>}
            <button className="btn btn-primary btn-block" disabled={status === "saving" || showMismatch}>
              {status === "saving" ? "Saving…" : "Set new password"}
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