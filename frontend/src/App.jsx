import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import ProtectedRoute from "./components/ProtectedRoute.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Documents from "./pages/Documents.jsx";
import Login from "./pages/Login.jsx";
import Register from "./pages/Register.jsx";

/**
 * App
 *
 * The routing shell. Dashboard and Documents both require login (wrapped
 * in ProtectedRoute); /login and /register are public. Later phases add
 * /chat, /notes, /bookmarks, /study, /flashcards, /knowledge-gaps,
 * /settings — each as its own <Route> pointing at a page component under
 * src/pages/.
 */
export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route
          path="/documents"
          element={
            <ProtectedRoute>
              <Documents />
            </ProtectedRoute>
          }
        />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
      </Routes>
      <footer>DataBound AI — Phase 3: Document Management</footer>
    </>
  );
}
