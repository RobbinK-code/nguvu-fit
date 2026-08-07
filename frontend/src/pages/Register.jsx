import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/AuthContext";
import PasswordField from "../components/PasswordField";
import "./Auth.css";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", password: "", confirmPassword: "" });
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const showMismatch = form.confirmPassword.length > 0 && form.password !== form.confirmPassword;
  const showMatch = form.confirmPassword.length > 0 && form.password === form.confirmPassword;

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    if (form.password !== form.confirmPassword) {
      setError("Passwords don't match.");
      return;
    }

    setBusy(true);
    try {
      await register(form.email, form.password, form.name);
      navigate("/onboarding");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="auth-page container">
      <div className="auth-card card">
        <h2 className="auth-title">Create your account</h2>
        <form onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="name">Name</label>
            <input
              id="name"
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
            />
          </div>
          <div className="field">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              required
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
            />
          </div>

          <PasswordField
            id="password"
            label="Password (min 8 characters)"
            minLength={8}
            autoComplete="new-password"
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />

          <PasswordField
            id="confirmPassword"
            label="Confirm password"
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
          <button className="btn btn-primary btn-block" disabled={busy || showMismatch}>
            {busy ? "Creating account…" : "Create account"}
          </button>
        </form>
        <p className="auth-switch">
          Already training with us? <Link to="/login">Log in</Link>
        </p>
      </div>
    </div>
  );
}
