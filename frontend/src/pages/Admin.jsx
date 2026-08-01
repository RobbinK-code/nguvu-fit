import { useEffect, useState } from "react";
import { api } from "../lib/api";
import { useAuth } from "../lib/AuthContext";
import "./Admin.css";

export default function Admin() {
  const { user: currentUser } = useAuth();
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    try {
      const [s, u] = await Promise.all([api.adminStats(), api.adminListUsers()]);
      setStats(s);
      setUsers(u);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  async function handleToggleAdmin(id) {
    try {
      await api.adminToggleAdmin(id);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDelete(id) {
    if (!confirm("Delete this account? This can't be undone.")) return;
    try {
      await api.adminDeleteUser(id);
      load();
    } catch (err) {
      setError(err.message);
    }
  }

  if (loading) return <div className="page-loading container">Loading admin panel…</div>;

  return (
    <div className="container admin">
      <h2 className="section-title">Admin</h2>

      {error && <p className="error-text">{error}</p>}

      <div className="stat-row admin-stats">
        <div className="card stat-card">
          <span className="stat-label mono">TOTAL USERS</span>
          <span className="stat-value">{stats?.total_users}</span>
        </div>
        <div className="card stat-card">
          <span className="stat-label mono">ACTIVE SUBS</span>
          <span className="stat-value">{stats?.active_subscriptions}</span>
        </div>
        <div className="card stat-card">
          <span className="stat-label mono">WORKOUTS LOGGED</span>
          <span className="stat-value">{stats?.total_workouts_logged}</span>
        </div>
        <div className="card stat-card">
          <span className="stat-label mono">REVENUE</span>
          <span className="stat-value stat-value-small">KES {stats?.revenue_kes ?? 0}</span>
        </div>
      </div>

      <h3 className="section-title">Users</h3>
      <div className="card admin-table-card">
        <table className="admin-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Subscription</th>
              <th>Admin</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.name}</td>
                <td>{u.email}</td>
                <td>
                  <span className={`pill ${u.subscription_status === "active" ? "pill-active" : "pill-free"}`}>
                    {u.subscription_status}
                  </span>
                </td>
                <td>{u.is_admin ? "Yes" : "No"}</td>
                <td className="admin-actions">
                  <button
                    className="btn btn-secondary btn-small"
                    onClick={() => handleToggleAdmin(u.id)}
                  >
                    {u.is_admin ? "Revoke admin" : "Make admin"}
                  </button>
                  <button
                    className="btn btn-secondary btn-small btn-danger"
                    disabled={u.id === currentUser.id}
                    onClick={() => handleDelete(u.id)}
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
