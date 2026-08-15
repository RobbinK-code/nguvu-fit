import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";
import { api } from "../lib/api";
import { buildWeeklyVolume } from "../lib/progress";
import { useChartColors } from "../lib/chartColors";
import "./History.css";

function ChartTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="chart-tooltip">
      <p className="chart-tooltip-label mono">{label}</p>
      <p className="chart-tooltip-value">{payload[0].value} session{payload[0].value === 1 ? "" : "s"}</p>
    </div>
  );
}

export default function History() {
  const [logs, setLogs] = useState([]);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const chartColors = useChartColors();

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

  const weeklyVolume = buildWeeklyVolume(logs, 8);

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

      {logs.length > 0 && (
        <div className="card chart-card">
          <span className="stat-label mono">SESSIONS PER WEEK · LAST 8 WEEKS</span>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={200}>
              <BarChart data={weeklyVolume} margin={{ top: 16, right: 8, left: -20, bottom: 0 }}>
                <CartesianGrid vertical={false} stroke={chartColors.grid} />
                <XAxis
                  dataKey="label"
                  tick={{ fontSize: 11, fill: chartColors.axisText }}
                  axisLine={{ stroke: chartColors.grid }}
                  tickLine={false}
                />
                <YAxis
                  allowDecimals={false}
                  tick={{ fontSize: 11, fill: chartColors.axisText }}
                  axisLine={false}
                  tickLine={false}
                  width={24}
                />
                <Tooltip content={<ChartTooltip />} cursor={{ fill: "rgba(255, 90, 54, 0.06)" }} />
                <Bar dataKey="sessions" fill={chartColors.accent} radius={[4, 4, 0, 0]} maxBarSize={28} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

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
