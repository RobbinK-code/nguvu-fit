import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/AuthContext";
import "./NavBar.css";

export default function NavBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/");
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
            <Link to="/history">History</Link>
            <Link to="/subscribe">Subscribe</Link>
            <Link to="/profile">Profile</Link>
            {user.is_admin && <Link to="/admin">Admin</Link>}
            <button className="btn btn-secondary nav-logout" onClick={handleLogout}>
              Log out
            </button>
          </nav>
        ) : (
          <nav className="nav-links">
            <Link to="/login">Log in</Link>
            <Link to="/register" className="btn btn-primary nav-cta">
              Get started
            </Link>
          </nav>
        )}
      </div>
    </header>
  );
}
