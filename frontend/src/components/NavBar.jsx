import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/AuthContext";
import ThemeToggle from "./ThemeToggle";
import ConfirmDialog from "./ConfirmDialog";
import "./NavBar.css";

export default function NavBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [confirmLogoutOpen, setConfirmLogoutOpen] = useState(false);

  function handleLogout() {
    logout();
    navigate("/");
    setConfirmLogoutOpen(false);
  }

  return (
    <header className="navbar">
      <div className="container navbar-inner">
        <Link to="/" className="brand">
          NGUVU<span>FIT</span>
        </Link>

        {user ? (
          <nav className="nav-links">
            <Link to="/dashboard">Dashboard</Link>
            <Link to="/gym-guide">Gym Guide</Link>
            <Link to="/progress">Progress</Link>
            <Link to="/challenges">Challenges</Link>
            <Link to="/history">History</Link>
            <Link to="/subscribe">Subscribe</Link>
            <Link to="/profile">Profile</Link>
            {user.is_admin && <Link to="/admin">Admin</Link>}
            <ThemeToggle />
            <button
              className="btn btn-secondary nav-logout"
              onClick={() => setConfirmLogoutOpen(true)}
            >
              Log out
            </button>
          </nav>
        ) : (
          <nav className="nav-links">
            <Link to="/login">Log in</Link>
            <ThemeToggle />
            <Link to="/register" className="btn btn-primary nav-cta">
              Get started
            </Link>
          </nav>
        )}
      </div>

      <ConfirmDialog
        open={confirmLogoutOpen}
        title="Log out?"
        message="You'll need to log back in to see your dashboard, plan, and progress."
        confirmLabel="Log out"
        onConfirm={handleLogout}
        onCancel={() => setConfirmLogoutOpen(false)}
      />
    </header>
  );
}
