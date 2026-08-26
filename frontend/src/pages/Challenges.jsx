import { useEffect, useState } from "react";
import { api } from "../lib/api";
import PageLoading from "../components/PageLoading";
import ConfirmDialog from "../components/ConfirmDialog";
import "./Challenges.css";

export default function Challenges() {
  const [templates, setTemplates] = useState([]);
  const [active, setActive] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [busyId, setBusyId] = useState(null);
  const [leaveConfirmOpen, setLeaveConfirmOpen] = useState(false);

  async function load() {
    setLoading(true);
    try {
      const data = await api.getChallenges();
      setTemplates(data.templates);
      setActive(data.active);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleJoin(id) {
    setBusyId(id);
    setError(null);
    try {
      await api.joinChallenge(id);
      await load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyId(null);
    }
  }

  async function handleLeave() {
    setLeaveConfirmOpen(false);
    try {
      await api.leaveChallenge();
      await load();
    } catch (err) {
      setError(err.message);
    }
  }

  if (loading) return <PageLoading message="Loading challenges…" />;

  return (
    <div className="container challenges-page">
      <h2 className="section-title">Challenges</h2>

      {error && <p className="error-text">{error}</p>}

      {active ? (
        <div className="card active-challenge-card">
          <span className="pill pill-active">Active</span>
          <h3>{active.challenge.title}</h3>
          <p className="challenge-copy">{active.challenge.description}</p>

          <div className="challenge-progress-track">
            <div
              className="challenge-progress-fill"
              style={{ width: `${active.progress_pct}%` }}
            />
          </div>
          <div className="challenge-stats-row">
            <span>
              {active.workouts_logged} / {active.target_workouts} workouts
            </span>
            <span>{active.days_remaining} days left</span>
          </div>

          {active.is_complete ? (
            <p className="challenge-status challenge-status-good">
              Target hit! Nice work - stay on it or start a new challenge once this one ends.
            </p>
          ) : active.is_expired ? (
            <p className="challenge-status challenge-status-bad">
              This challenge window closed without hitting the target. No shame - start a fresh
              one whenever you're ready.
            </p>
          ) : active.on_track ? (
            <p className="challenge-status challenge-status-good">You're on pace. Keep going.</p>
          ) : (
            <p className="challenge-status challenge-status-bad">
              A little behind pace - a couple of extra sessions this week gets you back on track.
            </p>
          )}

          <button className="btn btn-secondary" onClick={() => setLeaveConfirmOpen(true)}>
            Leave this challenge
          </button>
        </div>
      ) : (
        <div className="challenge-grid">
          {templates.map((t) => (
            <div key={t.id} className="card challenge-card">
              <span className="pill pill-free challenge-level">{t.level}</span>
              <h3>{t.title}</h3>
              <p className="challenge-copy">{t.description}</p>
              <p className="challenge-meta mono">
                {t.target_workouts} workouts / {t.duration_days} days
              </p>
              <button
                className="btn btn-primary btn-block"
                onClick={() => handleJoin(t.id)}
                disabled={busyId === t.id}
              >
                {busyId === t.id ? "Joining…" : "Start challenge"}
              </button>
            </div>
          ))}
        </div>
      )}

      <ConfirmDialog
        open={leaveConfirmOpen}
        title="Leave this challenge?"
        message="Your progress on this challenge won't carry over if you start it again later."
        confirmLabel="Leave"
        danger
        onConfirm={handleLeave}
        onCancel={() => setLeaveConfirmOpen(false)}
      />
    </div>
  );
}
