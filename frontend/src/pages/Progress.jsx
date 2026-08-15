import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ReferenceLine } from "recharts";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";
import { useChartColors } from "../lib/chartColors";
import "./Progress.css";

const METRIC_FIELDS = [
  { key: "weight_kg", label: "Weight", unit: "kg" },
  { key: "waist_cm", label: "Waist", unit: "cm" },
  { key: "chest_cm", label: "Chest", unit: "cm" },
  { key: "hips_cm", label: "Hips", unit: "cm" },
  { key: "arm_cm", label: "Arm", unit: "cm" },
];

function ChartTooltip({ active, payload, label, unit }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <p className="chart-tooltip-label mono">{label}</p>
      <p className="chart-tooltip-value">
        {payload[0].value} {unit}
      </p>
    </div>
  );
}

function MetricChart({ title, unit, data, dataKey, targetValue, colors }) {
  const points = data.filter((d) => d[dataKey] != null);
  if (points.length === 0) return null;

  return (
    <div className="card metric-chart-card">
      <span className="stat-label mono">{title.toUpperCase()}</span>
      <div className="chart-wrap">
        <ResponsiveContainer width="100%" height={180}>
          <LineChart data={points} margin={{ top: 16, right: 16, left: -20, bottom: 0 }}>
            <CartesianGrid vertical={false} stroke={colors.grid} />
            <XAxis dataKey="label" tick={{ fontSize: 11, fill: colors.axisText }} axisLine={{ stroke: colors.grid }} tickLine={false} />
            <YAxis tick={{ fontSize: 11, fill: colors.axisText }} axisLine={false} tickLine={false} width={32} domain={["auto", "auto"]} />
            <Tooltip content={<ChartTooltip unit={unit} />} />
            {targetValue && (
              <ReferenceLine y={targetValue} stroke={colors.success} strokeDasharray="4 4" label={{ value: "target", fontSize: 10, fill: colors.success }} />
            )}
            <Line type="monotone" dataKey={dataKey} stroke={colors.accent} strokeWidth={2.5} dot={{ r: 3, fill: colors.accent }} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default function Progress() {
  const { user } = useAuth();
  const [metrics, setMetrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ weight_kg: "", waist_cm: "", chest_cm: "", hips_cm: "", arm_cm: "", notes: "" });

  const isPremium = Boolean(user?.has_premium);
  const chartColors = useChartColors();

  useEffect(() => {
    if (!isPremium) {
      setLoading(false);
      return;
    }
    async function load() {
      try {
        const data = await api.getMetrics();
        setMetrics(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, [isPremium]);

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);

    const payload = {};
    for (const f of METRIC_FIELDS) {
      if (form[f.key] !== "") payload[f.key] = Number(form[f.key]);
    }
    if (form.notes) payload.notes = form.notes;

    if (Object.keys(payload).filter((k) => k !== "notes").length === 0) {
      setError("Enter at least one measurement.");
      return;
    }

    setSaving(true);
    try {
      const entry = await api.logMetric(payload);
      setMetrics((prev) => [...prev, entry]);
      setForm({ weight_kg: "", waist_cm: "", chest_cm: "", hips_cm: "", arm_cm: "", notes: "" });
    } catch (err) {
      setError(err.message);
    } finally {
      setSaving(false);
    }
  }

  if (!isPremium) {
    return (
      <div className="container progress-page">
        <h2 className="section-title">Progress tracking</h2>
        <div className="card progress-locked">
          <span className="pill pill-free">Premium</span>
          <h3>See your trends, not just today's number.</h3>
          <p>
            Log weight and body measurements over time and watch real charts build - with a
            target line pulled straight from your goal.
          </p>
          <Link to="/subscribe" className="btn btn-primary">
            Unlock progress tracking
          </Link>
        </div>
      </div>
    );
  }

  if (loading) return <div className="page-loading container">Loading your progress…</div>;

  const chartData = metrics.map((m) => ({
    label: new Date(m.recorded_at).toLocaleDateString(undefined, { month: "short", day: "numeric" }),
    weight_kg: m.weight_kg,
    waist_cm: m.waist_cm,
    chest_cm: m.chest_cm,
    hips_cm: m.hips_cm,
    arm_cm: m.arm_cm,
  }));

  return (
    <div className="container progress-page">
      <h2 className="section-title">Progress tracking</h2>

      <form className="card progress-form" onSubmit={handleSubmit}>
        <span className="stat-label mono">LOG TODAY'S NUMBERS</span>
        <div className="progress-form-grid">
          {METRIC_FIELDS.map((f) => (
            <div className="field" key={f.key}>
              <label htmlFor={f.key}>
                {f.label} ({f.unit})
              </label>
              <input
                id={f.key}
                type="number"
                step="0.1"
                value={form[f.key]}
                onChange={(e) => setForm({ ...form, [f.key]: e.target.value })}
              />
            </div>
          ))}
        </div>
        <div className="field">
          <label htmlFor="notes">Notes (optional)</label>
          <input id="notes" value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
        </div>
        {error && <p className="error-text">{error}</p>}
        <button className="btn btn-primary" disabled={saving}>
          {saving ? "Saving…" : "Save entry"}
        </button>
      </form>

      {metrics.length === 0 ? (
        <p className="empty-state">No entries yet - log your first measurement above to start your chart.</p>
      ) : (
        <div className="metric-chart-grid">
          <MetricChart title="Weight" unit="kg" data={chartData} dataKey="weight_kg" targetValue={user.target_weight_kg} colors={chartColors} />
          <MetricChart title="Waist" unit="cm" data={chartData} dataKey="waist_cm" colors={chartColors} />
          <MetricChart title="Chest" unit="cm" data={chartData} dataKey="chest_cm" colors={chartColors} />
          <MetricChart title="Hips" unit="cm" data={chartData} dataKey="hips_cm" colors={chartColors} />
          <MetricChart title="Arm" unit="cm" data={chartData} dataKey="arm_cm" colors={chartColors} />
        </div>
      )}
    </div>
  );
}
