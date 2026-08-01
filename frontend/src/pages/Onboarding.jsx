import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";
import "./Onboarding.css";

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

export default function Onboarding() {
  const navigate = useNavigate();
  const { refreshUser } = useAuth();

  const [form, setForm] = useState({
    height_cm: "",
    weight_kg: "",
    age: "",
    goal: "lose_fat",
    equipment: ["none"],
    focus_areas: [],
    target_weight_kg: "",
    target_date: "",
  });
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

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
    setBusy(true);
    try {
      const payload = {
        height_cm: Number(form.height_cm),
        weight_kg: Number(form.weight_kg),
        age: form.age ? Number(form.age) : undefined,
        goal: form.goal,
        equipment: form.equipment.length ? form.equipment : ["none"],
        focus_areas: form.focus_areas,
      };
      if (form.target_weight_kg) payload.target_weight_kg = Number(form.target_weight_kg);
      if (form.target_date) payload.target_date = form.target_date;

      await api.updateProfile(payload);
      await refreshUser();
      navigate("/dashboard");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="onboarding container">
      <h2 className="onboarding-title">Set up your training profile</h2>
      <p className="onboarding-sub">This tunes your plan and pace. You can change it anytime.</p>

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
            <select
              id="goal"
              value={form.goal}
              onChange={(e) => setForm({ ...form, goal: e.target.value })}
            >
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
          <label>Areas you want to hit harder (optional)</label>
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

        <div className="grid-2">
          <div className="field">
            <label htmlFor="target_weight">Target weight (kg) - optional</label>
            <input
              id="target_weight"
              type="number"
              value={form.target_weight_kg}
              onChange={(e) => setForm({ ...form, target_weight_kg: e.target.value })}
            />
          </div>
          <div className="field">
            <label htmlFor="target_date">Target date - optional</label>
            <input
              id="target_date"
              type="date"
              value={form.target_date}
              onChange={(e) => setForm({ ...form, target_date: e.target.value })}
            />
          </div>
        </div>

        {error && <p className="error-text">{error}</p>}
        <button className="btn btn-primary btn-block" disabled={busy}>
          {busy ? "Saving…" : "Build my plan"}
        </button>
      </form>
    </div>
  );
}
