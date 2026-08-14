import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

/**
 * Navbar
 *
 * Top-level navigation. The center links are still placeholders — they'll
 * become real routes as Phase 3 onward adds /documents, /chat, /notes,
 * etc. The right side now reflects real auth state: a logged-in user
 * sees their name and a logout button; a logged-out visitor sees
 * Login/Register links.
 */
export default function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <header className="navbar">
      <div className="navbar-inner">
        <Link to="/" className="brand">
          <span className="brand-seal">✓</span>
          DataBound AI
        </Link>
        <nav className="nav-links">
          <span>Documents</span>
          <span>Chat</span>
          <span>Notes</span>
          <span>Study</span>
        </nav>
        <div className="nav-auth">
          {isAuthenticated ? (
            <>
              <span className="nav-username">{user.name}</span>
              <button className="btn-text" onClick={logout}>
                Log out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn-text">
                Log in
              </Link>
              <Link to="/register" className="btn-primary btn-small">
                Register
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

