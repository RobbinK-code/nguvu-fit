import PageLoading from "../components/PageLoading";
import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";
import { computeStreak, countThisWeek, MILESTONES } from "../lib/progress";
import { useCloseOnHide } from "../lib/useCloseOnHide";
import "./Dashboard.css";

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [quote, setQuote] = useState(null);
  const [plan, setPlan] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [shuffling, setShuffling] = useState(false);
  const [logging, setLogging] = useState(null);
  const [logged, setLogged] = useState({});
  const [logs, setLogs] = useState([]);
  const [openVideoKey, setOpenVideoKey] = useState(null);
  useCloseOnHide(() => setOpenVideoKey(null));

  async function loadPlan(refresh = false) {
    if (refresh) setShuffling(true);
    setError(null);
    try {
      const p = await api.getPlan(3, refresh).catch((err) => {
        if (err.status === 400) return { needsProfile: true };
        if (err.status === 402) throw err;
        throw err;
      });
      setPlan(p);
      if (refresh) setLogged({});
    } catch (err) {
      setError(err.message);
    } finally {
      setShuffling(false);
    }
  }

  useEffect(() => {
    let mounted = true;
    async function load() {
      setLoading(true);
      setError(null);
      try {
        const [q, p, l] = await Promise.all([
          api.getQuoteOfDay(),
          api.getPlan(3).catch((err) => {
            if (err.status === 400) return { needsProfile: true };
            throw err;
          }),
          api.getLogs().catch(() => []),
        ]);
        if (!mounted) return;
        setQuote(q);
        setPlan(p);
        setLogs(l);
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

  const streak = computeStreak(logs);
  const sessionsThisWeek = countThisWeek(logs);
  const weeklyTarget = plan?.days?.length || 3;
  const weekProgressPct = Math.min(100, Math.round((sessionsThisWeek / weeklyTarget) * 100));
  const milestoneStats = { total_workouts: logs.length, total_minutes: logs.reduce((sum, l) => sum + (l.duration_minutes || 0), 0), streak };
  const unlockedMilestones = MILESTONES.filter((m) => m.check(milestoneStats));

  async function handleLogDay(day) {
    setLogging(day.day_number);
    try {
      const newLog = await api.logWorkout({
        workout_name: `Day ${day.day_number} - ${day.focus}`,
        duration_minutes: 30,
      });
      setLogged((l) => ({ ...l, [day.day_number]: true }));
      setLogs((prev) => [newLog, ...prev]);
    } catch (err) {
      setError(err.message);
    } finally {
      setLogging(null);
    }
  }

  if (loading) return <PageLoading message="Loading your plan…" />;

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
        <div className="card stat-card stat-card-streak">
          <span className="stat-label mono">STREAK</span>
          <span className="stat-value">
            {streak}
            <span className="stat-value-unit">{streak === 1 ? " day" : " days"}</span>
          </span>
          <span className="stat-sub">{streak > 0 ? "keep it going" : "log a session to start"}</span>
        </div>
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

      <div className="card week-progress-card">
        <div className="week-progress-header">
          <span className="stat-label mono">WEEKLY PROGRESS</span>
          <span className="week-progress-count mono">
            {sessionsThisWeek} / {weeklyTarget} sessions
          </span>
        </div>
        <div className="week-progress-track">
          <div className="week-progress-fill" style={{ width: `${weekProgressPct}%` }} />
        </div>
      </div>

      {unlockedMilestones.length > 0 && (
        <div className="milestones-row">
          {unlockedMilestones.map((m) => (
            <span key={m.id} className="milestone-badge">
              {m.label}
            </span>
          ))}
        </div>
      )}

      <div className="section-header-row">
        <h2 className="section-title">This week</h2>
        {user?.has_premium ? (
          <button
            className="btn btn-secondary btn-small"
            onClick={() => loadPlan(true)}
            disabled={shuffling}
          >
            {shuffling ? "Shuffling…" : "Shuffle plan"}
          </button>
        ) : (
          <Link to="/subscribe" className="shuffle-upsell mono">
            Premium: shuffle your plan any time
          </Link>
        )}
      </div>
      <div className="day-grid">
        {plan?.days?.map((day) => (
          <div className="card day-card" key={day.day_number}>
            <div className="day-card-header">
              <span className="day-index mono">DAY {String(day.day_number).padStart(2, "0")}</span>
              <span className="day-focus">{day.focus}</span>
            </div>
            <ul className="exercise-list">
              {day.exercises.map((ex, i) => {
                const videoKey = `${day.day_number}-${i}`;
                return (
                  <li key={i}>
                    <div className="exercise-row">
                      <span className="exercise-name">{ex.name}</span>
                      <span className="exercise-detail mono">
                        {ex.sets}× {ex.reps ? `${ex.reps} reps` : `${ex.duration_seconds}s`}
                      </span>
                    </div>
                    <div className="exercise-links">
                      <button
                        type="button"
                        className="gym-alt-link"
                        onClick={() => navigate(`/gym-guide?group=${ex.muscle_group}`)}
                      >
                        At the gym instead →
                      </button>
                      {ex.video_id && (
                        <button
                          type="button"
                          className="gym-alt-link"
                          onClick={() => setOpenVideoKey(openVideoKey === videoKey ? null : videoKey)}
                        >
                          {openVideoKey === videoKey ? "Hide video" : "Watch video"}
                        </button>
                      )}
                    </div>
                    {openVideoKey === videoKey && ex.video_id && (
                      <div className="exercise-video-wrap">
                        <iframe
                          src={`https://www.youtube.com/embed/${ex.video_id}`}
                          title={`${ex.name} demonstration`}
                          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                          allowFullScreen
                          loading="lazy"
                        />
                      </div>
                    )}
                  </li>
                );
              })}
            </ul>
            <button
              className="btn btn-primary btn-block"
              disabled={logged[day.day_number]}
              onClick={() => navigate("/workout", { state: { day } })}
            >
              Start workout
            </button>
            <button
              className="btn btn-secondary btn-block"
              disabled={logging === day.day_number || logged[day.day_number]}
              onClick={() => handleLogDay(day)}
            >
              {logged[day.day_number]
                ? "Logged ✓"
                : logging === day.day_number
                ? "Logging…"
                : "Mark as done without guided mode"}
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
