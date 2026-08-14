/**
 * Navbar
 *
 * Top-level navigation. Phase 1 only has one real page, so the links are
 * placeholders — they'll become real <Link> routes as Phase 3 onward adds
 * /documents, /chat, /notes, etc.
 */
export default function Navbar() {
  return (
    <header className="navbar">
      <div className="navbar-inner">
        <div className="brand">
          <span className="brand-seal">✓</span>
          DataBound AI
        </div>
        <nav className="nav-links">
          <span>Documents</span>
          <span>Chat</span>
          <span>Notes</span>
          <span>Study</span>
        </nav>
      </div>
    </header>
  );
}
