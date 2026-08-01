import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";
import "./Dashboard.css";

export default function Dashboard() {
  const { user } = useAuth();
  const [quote, setQuote] = useState(null);
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [logging, setLogging] = useState(null);
  const [logged, setLogged] = useState({});

  useEffect(() => {
    let mounted = true;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [q, p] = await Promise.all([
          api.getQuoteOfDay(),
          api.getPlan(3).catch((err) => {
            if (err.status === 400) return { needsProfile: true };
            throw err;
          }),
        ]);
        if (!mounted) return;
        setQuote(q);
        setPlan(p);
      } catch (err) {
        if (mounted) setError(err.message);
      } finally {
        if (mounted) setLoading(false);
      }
    }
    load();
    return () => {
      mounted = false;
    };
  }, []);

  async function handleLogDay(day) {
    setLogging(day.day_number);
    try {
      await api.logWorkout({
        workout_name: `Day ${day.day_number} - ${day.focus}`,
        duration_minutes: 30,
      });
      setLogged((l) => ({ ...l, [day.day_number]: true }));
    } catch (err) {
      setError(err.message);
    } finally {
      setLogging(null);
    }
  }

  if (loading) return <div className="page-loading container">Loading your plan…</div>;

  if (plan?.needsProfile) {
    return (
      <div className="container dashboard-empty">
        <h2>Almost there</h2>
        <p>Add your height and weight to unlock your personalized plan.</p>
        <Link to="/onboarding" className="btn btn-primary">
          Finish setup
        </Link>
      </div>
    );
  }

  return (
    <div className="container dashboard">
      {quote && (
        <div className="quote-strip">
          <p className="quote-text">"{quote.text}"</p>
          {quote.author && <p className="quote-author mono">— {quote.author}</p>}
        </div>
      )}

      <div className="stat-row">
        <div className="card stat-card">
          <span className="stat-label mono">BMI</span>
          <span className="stat-value">{plan?.bmi ?? "—"}</span>
          <span className="stat-sub">{plan?.bmi_category?.replace("_", " ") ?? "add your stats"}</span>
        </div>
        <div className="card stat-card">
          <span className="stat-label mono">GOAL</span>
          <span className="stat-value stat-value-small">
            {plan?.goal?.replace("_", " ") ?? "—"}
          </span>
        </div>
        {plan?.pace && !plan.pace.error && (
          <div className="card stat-card">
            <span className="stat-label mono">WEEKLY PACE</span>
            <span className="stat-value stat-value-small">
              {Math.abs(plan.pace.weekly_rate_kg)} kg/wk to {plan.pace.direction}
            </span>
            <span className={`pill ${plan.pace.is_safe_pace ? "pill-active" : "pill-free"}`}>
              {plan.pace.is_safe_pace ? "sustainable pace" : "aggressive pace"}
            </span>
          </div>
        )}
      </div>

      <h2 className="section-title">This week</h2>
      <div className="day-grid">
        {plan?.days?.map((day) => (
          <div className="card day-card" key={day.day_number}>
            <div className="day-card-header">
              <span className="day-index mono">DAY {String(day.day_number).padStart(2, "0")}</span>
              <span className="day-focus">{day.focus}</span>
            </div>
            <ul className="exercise-list">
              {day.exercises.map((ex, i) => (
                <li key={i}>
                  <span className="exercise-name">{ex.name}</span>
                  <span className="exercise-detail mono">
                    {ex.sets}× {ex.reps ? `${ex.reps} reps` : `${ex.duration_seconds}s`}
                  </span>
                </li>
              ))}
            </ul>
            <button
              className="btn btn-secondary btn-block"
              disabled={logging === day.day_number || logged[day.day_number]}
              onClick={() => handleLogDay(day)}
            >
              {logged[day.day_number]
                ? "Logged ✓"
                : logging === day.day_number
                ? "Logging…"
                : "Mark as done"}
            </button>
          </div>
        ))}
      </div>

      {plan?.guidance?.length > 0 && (
        <div className="card guidance-card">
          <span className="stat-label mono">A FEW NOTES</span>
          <ul>
            {plan.guidance.map((tip, i) => (
              <li key={i}>{tip}</li>
            ))}
          </ul>
        </div>
      )}

      {error && <p className="error-text">{error}</p>}
    </div>
  );
}
