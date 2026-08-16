import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";
import "./Onboarding.css";
import "./Profile.css";

const GOALS = [
  { value: "lose_fat", label: "Lose fat / general fitness" },
  { value: "build_muscle", label: "Build muscle / strength" },
  { value: "endurance", label: "Improve endurance" },
  { value: "mobility", label: "Mobility & general health" },
];

const EQUIPMENT = [
  { value: "none", label: "Bodyweight only" },
  { value: "dumbbells", label: "Dumbbells" },
  { value: "bands", label: "Resistance bands" },
  { value: "full_gym", label: "Full home gym" },
];

const FOCUS_AREAS = ["legs", "chest", "back", "shoulders", "arms", "core", "full_body"];

const TIERS = [
  { value: "beginner", label: "Beginner", blurb: "Building the habit" },
  { value: "intermediate", label: "Intermediate", blurb: "Comfortable with the basics" },
  { value: "advanced", label: "Advanced", blurb: "Ready for more volume" },
  { value: "legendary", label: "Legendary", blurb: "Push me to the limit" },
];

export default function Profile() {
  const { user, refreshUser, logout } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState(null);
  const [error, setError] = useState(null);
  const [saved, setSaved] = useState(false);
  const [busy, setBusy] = useState(false);

  const [exporting, setExporting] = useState(false);
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deletePassword, setDeletePassword] = useState("");
  const [deleteError, setDeleteError] = useState(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    if (user) {
      setForm({
        height_cm: user.height_cm ?? "",
        weight_kg: user.weight_kg ?? "",
        age: user.age ?? "",
        goal: user.goal ?? "lose_fat",
        equipment: user.equipment?.length ? user.equipment : ["none"],
        focus_areas: user.focus_areas ?? [],
        fitness_tier: user.fitness_tier ?? "beginner",
        target_weight_kg: user.target_weight_kg ?? "",
        target_date: user.target_date ?? "",
      });
    }
  }, [user]);

  if (!form) return null;

  function toggleEquipment(value) {
    setForm((f) => ({
      ...f,
      equipment: f.equipment.includes(value)
        ? f.equipment.filter((v) => v !== value)
        : [...f.equipment, value],
    }));
  }

  function toggleFocus(value) {
    setForm((f) => ({
      ...f,
      focus_areas: f.focus_areas.includes(value)
        ? f.focus_areas.filter((v) => v !== value)
        : [...f.focus_areas, value],
    }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setSaved(false);
    setBusy(true);
    try {
      const payload = {
        height_cm: Number(form.height_cm),
        weight_kg: Number(form.weight_kg),
        age: form.age ? Number(form.age) : undefined,
        goal: form.goal,
        equipment: form.equipment.length ? form.equipment : ["none"],
        focus_areas: form.focus_areas,
        fitness_tier: form.fitness_tier,
      };
      if (form.target_weight_kg) payload.target_weight_kg = Number(form.target_weight_kg);
      if (form.target_date) payload.target_date = form.target_date;

      await api.updateProfile(payload);
      await refreshUser();
      setSaved(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  async function handleExport() {
    setExporting(true);
    try {
      const data = await api.exportProfileData();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `nguvu-fit-data-${new Date().toISOString().slice(0, 10)}.json`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.message);
    } finally {
      setExporting(false);
    }
  }

  async function handleDeleteAccount(e) {
    e.preventDefault();
    setDeleteError(null);
    setDeleting(true);
    try {
      await api.deleteAccount(deletePassword);
      logout();
      navigate("/");
    } catch (err) {
      setDeleteError(err.message);
    } finally {
      setDeleting(false);
    }
  }

  return (
    <div className="onboarding container">
      <div className="profile-header">
        <div className="profile-avatar" aria-hidden="true">
          {user.name?.charAt(0)?.toUpperCase() || "?"}
        </div>
        <div>
          <div className="profile-header-top">
            <h2 className="onboarding-title">{user.name}</h2>
            <span className={`pill ${user.has_premium ? "pill-active" : "pill-free"}`}>
              {user.has_premium ? "Premium" : "Free plan"}
            </span>
          </div>
          <p className="onboarding-sub">{user.email}</p>
        </div>
      </div>

      {user.bmi && (
        <div className="profile-quick-stats">
          <div className="card profile-quick-stat">
            <span className="stat-label mono">BMI</span>
            <span className="stat-value stat-value-small">{user.bmi}</span>
          </div>
          <div className="card profile-quick-stat">
            <span className="stat-label mono">GOAL</span>
            <span className="stat-value stat-value-small">{user.goal?.replace("_", " ")}</span>
          </div>
          <div className="card profile-quick-stat">
            <span className="stat-label mono">TIER</span>
            <span className="stat-value stat-value-small">{user.fitness_tier ?? "beginner"}</span>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="card onboarding-card">
        <div className="grid-2">
          <div className="field">
            <label htmlFor="height">Height (cm)</label>
            <input
              id="height"
              type="number"
              required
              value={form.height_cm}
              onChange={(e) => setForm({ ...form, height_cm: e.target.value })}
            />
          </div>
          <div className="field">
            <label htmlFor="weight">Weight (kg)</label>
            <input
              id="weight"
              type="number"
              required
              value={form.weight_kg}
              onChange={(e) => setForm({ ...form, weight_kg: e.target.value })}
            />
          </div>
        </div>

        <div className="grid-2">
          <div className="field">
            <label htmlFor="age">Age</label>
            <input
              id="age"
              type="number"
              value={form.age}
              onChange={(e) => setForm({ ...form, age: e.target.value })}
            />
          </div>
          <div className="field">
            <label htmlFor="goal">Main goal</label>
            <select id="goal" value={form.goal} onChange={(e) => setForm({ ...form, goal: e.target.value })}>
              {GOALS.map((g) => (
                <option key={g.value} value={g.value}>
                  {g.label}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div className="field">
          <label>Equipment you have</label>
          <div className="chip-row">
            {EQUIPMENT.map((eq) => (
              <button
                type="button"
                key={eq.value}
                className={`chip ${form.equipment.includes(eq.value) ? "chip-on" : ""}`}
                onClick={() => toggleEquipment(eq.value)}
              >
                {eq.label}
              </button>
            ))}
          </div>
        </div>

        <div className="field">
          <label>Areas you want to hit harder</label>
          <div className="chip-row">
            {FOCUS_AREAS.map((area) => (
              <button
                type="button"
                key={area}
                className={`chip ${form.focus_areas.includes(area) ? "chip-on" : ""}`}
                onClick={() => toggleFocus(area)}
              >
                {area.replace("_", " ")}
              </button>
            ))}
          </div>
        </div>

        <div className="field">
          <label>Fitness tier</label>
          <div className="tier-grid">
            {TIERS.map((t) => (
              <button
                type="button"
                key={t.value}
                className={`tier-card ${form.fitness_tier === t.value ? "tier-card-selected" : ""}`}
                onClick={() => setForm({ ...form, fitness_tier: t.value })}
              >
                <span className="tier-label">{t.label}</span>
                <span className="tier-blurb">{t.blurb}</span>
              </button>
            ))}
          </div>
          <p className="field-hint">
            Workout feeling too easy? Level up here for more sets, reps, and hold time. For
            athletes under 16, exercise difficulty is automatically capped for safety regardless
            of tier.
          </p>
        </div>

        <div className="grid-2">
          <div className="field">
            <label htmlFor="target_weight">Target weight (kg)</label>
            <input
              id="target_weight"
              type="number"
              value={form.target_weight_kg}
              onChange={(e) => setForm({ ...form, target_weight_kg: e.target.value })}
            />
          </div>
          <div className="field">
            <label htmlFor="target_date">Target date</label>
            <input
              id="target_date"
              type="date"
              value={form.target_date}
              onChange={(e) => setForm({ ...form, target_date: e.target.value })}
            />
          </div>
        </div>

        {error && <p className="error-text">{error}</p>}
        {saved && <p className="saved-text">Saved.</p>}
        <button className="btn btn-primary btn-block" disabled={busy}>
          {busy ? "Saving…" : "Save changes"}
        </button>
      </form>

      <div className="card danger-zone">
        <h3 className="danger-zone-title">Account data</h3>

        <div className="danger-zone-row">
          <div>
            <p className="danger-zone-label">Export your data</p>
            <p className="danger-zone-copy">
              Download everything Nguvu Fit holds about you - profile, workout history,
              measurements, and payment records - as a JSON file.
            </p>
          </div>
          <button className="btn btn-secondary" onClick={handleExport} disabled={exporting}>
            {exporting ? "Preparing…" : "Export my data"}
          </button>
        </div>

        <div className="danger-zone-row danger-zone-row-delete">
          <div>
            <p className="danger-zone-label danger-zone-label-danger">Delete account</p>
            <p className="danger-zone-copy">
              Permanently deletes your account and all associated data. This can't be undone.
            </p>
          </div>
          {!deleteOpen ? (
            <button className="btn btn-secondary btn-danger" onClick={() => setDeleteOpen(true)}>
              Delete my account
            </button>
          ) : (
            <form className="danger-zone-confirm" onSubmit={handleDeleteAccount}>
              <input
                type="password"
                required
                placeholder="Confirm your password"
                value={deletePassword}
                onChange={(e) => setDeletePassword(e.target.value)}
              />
              <div className="danger-zone-confirm-actions">
                <button
                  type="button"
                  className="btn btn-secondary"
                  onClick={() => {
                    setDeleteOpen(false);
                    setDeletePassword("");
                    setDeleteError(null);
                  }}
                >
                  Cancel
                </button>
                <button type="submit" className="btn btn-danger" disabled={deleting}>
                  {deleting ? "Deleting…" : "Permanently delete"}
                </button>
              </div>
              {deleteError && <p className="error-text">{deleteError}</p>}
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
