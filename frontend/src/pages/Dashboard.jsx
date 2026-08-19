import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import * as api from "../services/api.js";
import { useAuth } from "../context/AuthContext.jsx";
import AnimatedNumber from "../components/AnimatedNumber.jsx";
import Skeleton from "../components/Skeleton.jsx";
import ErrorMessage from "../components/ErrorMessage.jsx";

/**
 * Dashboard
 *
 * The real dashboard from spec section 15: live counts (documents,
 * collections, ready vs. failed), recent documents, and quick actions —
 * pulled from actual data instead of a static status page. The
 * API/database connectivity check from earlier phases is kept, but
 * demoted to a small footer indicator rather than the headline content,
 * since "is the backend up" matters far less to a returning user than
 * "what's in my workspace."
 */
export default function Dashboard() {
  const { user } = useAuth();

  const [documents, setDocuments] = useState(null);
  const [collections, setCollections] = useState(null);
  const [loadError, setLoadError] = useState(null);
  const [backendStatus, setBackendStatus] = useState("pending"); // "pending" | "ok" | "error"

  useEffect(() => {
    Promise.all([api.listDocuments(), api.listCollections()])
      .then(([docs, cols]) => {
        setDocuments(docs);
        setCollections(cols);
      })
      .catch((err) => setLoadError(err.message));

    api
      .checkHealth()
      .then(() => setBackendStatus("ok"))
      .catch(() => setBackendStatus("error"));
  }, []);

  const loading = documents === null || collections === null;
  const readyCount = documents?.filter((d) => d.status === "ready").length ?? 0;
  const failedCount = documents?.filter((d) => d.status === "failed").length ?? 0;
  const recentDocuments = documents?.slice(0, 5) ?? [];

  return (
    <main>
      <div className="container dashboard-page">
        <div className="dashboard-header">
          <div className="hero-eyebrow">Welcome back</div>
          <h1>{user ? `Hi, ${user.name.split(" ")[0]}.` : "Dashboard"}</h1>
          <p className="hero-sub">Here's what's in your workspace right now.</p>
        </div>

        <ErrorMessage message={loadError} />

        <div className="stats-grid">
          <StatCard label="Documents" value={documents?.length} loading={loading} />
          <StatCard label="Ready" value={readyCount} loading={loading} accent="verified" />
          <StatCard label="Failed" value={failedCount} loading={loading} accent={failedCount > 0 ? "danger" : undefined} />
          <StatCard label="Collections" value={collections?.length} loading={loading} />
        </div>

        <div className="dashboard-quick-actions">
          <Link to="/documents" className="btn-primary">
            + Upload a document
          </Link>
          <Link to="/documents" className="btn-text">
            View all documents →
          </Link>
        </div>

        <div className="card dashboard-recent">
          <h3>Recent documents</h3>
          {loading ? (
            <Skeleton variant="row" count={3} />
          ) : recentDocuments.length === 0 ? (
            <p className="empty-state" style={{ padding: "12px 0" }}>
              No documents yet. <Link to="/documents">Upload your first one →</Link>
            </p>
          ) : (
            <ul className="recent-doc-list">
              {recentDocuments.map((doc, i) => (
                <li key={doc.id} className="recent-doc-row animate-fade-in-up" style={{ animationDelay: `${i * 40}ms` }}>
                  <span className={`status-dot ${doc.status === "ready" ? "ok" : doc.status === "failed" ? "error" : "pending"}`} />
                  <span className="recent-doc-name">{doc.filename}</span>
                  <span className="recent-doc-type mono">{doc.file_type.toUpperCase()}</span>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="backend-status-strip">
          <span className={`status-dot-small ${backendStatus}`} />
          <span>
            {backendStatus === "ok" && "Connected to backend"}
            {backendStatus === "error" && "Backend unreachable — try refreshing in a moment"}
            {backendStatus === "pending" && "Checking connection..."}
          </span>
        </div>
      </div>
    </main>
  );
}

function StatCard({ label, value, loading, accent }) {
  return (
    <div className={`card stat-card${accent ? ` stat-card-${accent}` : ""}`}>
      <div className="stat-card-value">{loading ? <Skeleton variant="number" /> : <AnimatedNumber value={value ?? 0} />}</div>
      <div className="stat-card-label">{label}</div>
    </div>
  );
}
