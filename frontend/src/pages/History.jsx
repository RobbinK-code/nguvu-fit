import { useEffect, useState } from "react";
import { api } from "../lib/api";
import "./History.css";

export default function History() {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const [l, s] = await Promise.all([api.getLogs(), api.getStats()]);
        setLogs(l);
        setStats(s);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <div className="page-loading container">Loading history…</div>;

  return (
    <div className="container history">
      <h2 className="section-title">Your history</h2>

      <div className="stat-row">
        <div className="card stat-card">
          <span className="stat-label mono">WORKOUTS LOGGED</span>
          <span className="stat-value">{stats?.total_workouts ?? 0}</span>
        </div>
        <div className="card stat-card">
          <span className="stat-label mono">TOTAL MINUTES</span>
          <span className="stat-value">{stats?.total_minutes ?? 0}</span>
        </div>
      </div>

      {error && <p className="error-text">{error}</p>}

      {logs.length === 0 ? (
        <p className="empty-state">
          Nothing logged yet - mark a workout as done on your dashboard to start your streak.
        </p>
      ) : (
        <ul className="log-list">
          {logs.map((log) => (
            <li key={log.id} className="card log-row">
              <div>
                <p className="log-name">{log.workout_name_snapshot}</p>
                <p className="log-date mono">
                  {new Date(log.completed_at).toLocaleDateString(undefined, {
                    weekday: "short",
                    month: "short",
                    day: "numeric",
                  })}
                </p>
              </div>
              {log.duration_minutes && <span className="log-duration mono">{log.duration_minutes} min</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
