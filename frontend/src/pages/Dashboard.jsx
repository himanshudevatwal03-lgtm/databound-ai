import { useEffect, useState } from "react";
import { checkHealth } from "../services/api.js";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import ErrorMessage from "../components/ErrorMessage.jsx";

/**
 * Dashboard (Phase 1 version)
 *
 * In later phases this becomes the real dashboard (document counts,
 * recent questions, unanswered-question analytics — see spec section 15).
 * For Phase 1, its job is simpler and more important: prove the full
 * chain works end to end — React calls FastAPI, FastAPI queries
 * PostgreSQL, and the result renders in the browser. If this card shows
 * "connected", the foundation is solid and every later phase can build on
 * top of it.
 */
export default function Dashboard() {
  const [status, setStatus] = useState("pending"); // "pending" | "ok" | "error"
  const [detail, setDetail] = useState(null);
  const [errorMsg, setErrorMsg] = useState(null);

  useEffect(() => {
    checkHealth()
      .then((data) => {
        setDetail(data);
        setStatus("ok");
      })
      .catch((err) => {
        setErrorMsg(err.message);
        setStatus("error");
      });
  }, []);

  return (
    <main>
      <section className="hero">
        <div className="hero-eyebrow">Data-grounded Q&A</div>
        <h1>Answers backed only by your own documents.</h1>
        <p className="hero-sub">
          Upload files, ask questions, and get answers with citations back
          to your source material — or an honest "not enough information"
          when the answer isn't in your data.
        </p>

        <div className="card status-card">
          <h3>System status</h3>

          {status === "pending" && <LoadingSpinner label="Checking backend connection..." />}

          {status === "ok" && (
            <>
              <div className="status-row">
                <span className="status-dot ok" />
                <span className="status-label">API</span>
                <span className="status-value">running</span>
              </div>
              <div className="status-row">
                <span className="status-dot ok" />
                <span className="status-label">Database</span>
                <span className="status-value">{detail.database}</span>
              </div>
              <p className="mono" style={{ fontSize: "0.8rem", color: "var(--color-ink-muted)", marginTop: 12, marginBottom: 0 }}>
                {detail.service}
              </p>
            </>
          )}

          {status === "error" && (
            <>
              <div className="status-row">
                <span className="status-dot error" />
                <span className="status-label">API</span>
                <span className="status-value">unreachable</span>
              </div>
              <ErrorMessage message={errorMsg} />
              <p style={{ fontSize: "0.85rem", color: "var(--color-ink-muted)", marginTop: 12, marginBottom: 0 }}>
                Make sure the backend is running (<code>docker compose up</code>) and reachable at the URL configured in <code>VITE_API_BASE_URL</code>.
              </p>
            </>
          )}
        </div>
      </section>
    </main>
  );
}
