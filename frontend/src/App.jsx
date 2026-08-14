import { Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar.jsx";
import Dashboard from "./pages/Dashboard.jsx";

/**
 * App
 *
 * The routing shell. Phase 1 only registers "/" (Dashboard). Later phases
 * add /login, /register, /documents, /collections, /chat, /notes,
 * /bookmarks, /study, /flashcards, /knowledge-gaps, /settings — each as
 * its own <Route> pointing at a page component under src/pages/.
 */
export default function App() {
  return (
    <>
      <Navbar />
      <Routes>
        <Route path="/" element={<Dashboard />} />
      </Routes>
      <footer>DataBound AI — Phase 1: Project Foundation</footer>
    </>
  );
}
