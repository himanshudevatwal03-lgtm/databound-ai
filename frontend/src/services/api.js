/**
 * api.js
 *
 * A single place that knows how to talk to the FastAPI backend.
 *
 * Why this file exists:
 * If every component called `fetch(...)` directly, the base URL, headers,
 * and error handling would be duplicated everywhere and painful to change.
 * Instead, components import small functions like `checkHealth()` from
 * here. Later phases will add `login()`, `uploadDocument()`, `askQuestion()`
 * etc. to this same file (or split into api/auth.js, api/documents.js, etc.
 * as it grows).
 */

// In Docker Compose, the frontend container talks to the backend container
// using the service name "backend" (see docker-compose.yml). When running
// the frontend outside Docker against a local backend, VITE_API_BASE_URL
// can override this via a .env file in frontend/.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Generic request helper. Throws on non-2xx responses so callers can
 * use try/catch instead of checking response.ok everywhere.
 */
async function request(path, options = {}) {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`API error ${response.status}: ${errorBody}`);
  }

  return response.json();
}

/** Pings the backend health endpoint (also confirms DB connectivity). */
export function checkHealth() {
  return request("/api/health");
}

export { API_BASE_URL };
