import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import LoadingSpinner from "./LoadingSpinner.jsx";

/**
 * ProtectedRoute
 *
 * Wraps a page that requires a logged-in user. While we're still
 * checking for an existing session (loading), it shows a spinner rather
 * than flashing the login page and immediately redirecting away from it —
 * that flash is a common and avoidable rough edge in auth flows.
 */
export default function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <main>
        <div className="container" style={{ paddingTop: 48 }}>
          <LoadingSpinner label="Checking your session..." />
        </div>
      </main>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
