/**
 * api.js
 *
 * A single place that knows how to talk to the FastAPI backend.
 *
 * Why this file exists:
 * If every component called `fetch(...)` directly, the base URL, headers,
 * and error handling would be duplicated everywhere and painful to change.
 * Instead, components import small functions like `checkHealth()` or
 * `login()` from here. As more features arrive (documents, chat, notes),
 * this file is a natural place to split into api/auth.js, api/documents.js,
 * etc. — for now it's small enough to stay together.
 */

// In Docker Compose, the frontend container talks to the backend container
// using the service name "backend" (see docker-compose.yml). When running
// the frontend outside Docker against a local backend, VITE_API_BASE_URL
// can override this via a .env file in frontend/.
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

/**
 * Generic request helper. Throws on non-2xx responses so callers can use
 * try/catch instead of checking response.ok everywhere. FastAPI's error
 * responses look like {"detail": "some message"} (or a list of validation
 * errors for 422s) — this pulls out a readable message either way.
 */
async function request(path, options = {}) {
  const token = getToken();

  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...options,
  });

  if (!response.ok) {
    let message = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") {
        message = body.detail;
      } else if (Array.isArray(body.detail)) {
        // Pydantic validation errors: an array of {loc, msg, ...}
        message = body.detail.map((e) => e.msg).join("; ");
      }
    } catch {
      // Response wasn't JSON — fall back to the generic message above.
    }
    throw new Error(message);
  }

  if (response.status === 204) return null;
  return response.json();
}

/** Pings the backend health endpoint (also confirms DB connectivity). */
export function checkHealth() {
  return request("/api/health");
}

// --- Auth token storage ---
//
// The JWT is kept in localStorage so a page refresh doesn't log the user
// out. It's sent as a Bearer token on every request via the `request()`
// helper above, rather than attached to each call site individually.
const TOKEN_KEY = "databound_token";

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
}

// --- Auth endpoints ---

/** Registers a new account. Returns { access_token, token_type, user }. */
export function register({ name, email, password }) {
  return request("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ name, email, password }),
  });
}

/** Logs in an existing account. Returns { access_token, token_type, user }. */
export function login({ email, password }) {
  return request("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

/** Returns the currently logged-in user, based on the stored token. */
export function getMe() {
  return request("/api/auth/me");
}

// --- Collections ---

export function listCollections() {
  return request("/api/collections");
}

export function createCollection({ name, description }) {
  return request("/api/collections", {
    method: "POST",
    body: JSON.stringify({ name, description }),
  });
}

export function deleteCollection(collectionId) {
  return request(`/api/collections/${collectionId}`, { method: "DELETE" });
}

// --- Documents ---

export function listDocuments(collectionId) {
  const query = collectionId ? `?collection_id=${collectionId}` : "";
  return request(`/api/documents${query}`);
}

export function getDocument(documentId) {
  return request(`/api/documents/${documentId}`);
}

export function deleteDocument(documentId) {
  return request(`/api/documents/${documentId}`, { method: "DELETE" });
}

/**
 * Uploads a file. Doesn't use the generic request() helper because file
 * uploads need multipart/form-data (the browser sets the correct
 * boundary header automatically when given a FormData body — setting
 * Content-Type manually here would actually break it).
 */
export async function uploadDocument(file, collectionId) {
  const token = getToken();
  const formData = new FormData();
  formData.append("file", file);

  const query = collectionId ? `?collection_id=${collectionId}` : "";
  const response = await fetch(`${API_BASE_URL}/api/documents/upload${query}`, {
    method: "POST",
    headers: token ? { Authorization: `Bearer ${token}` } : {},
    body: formData,
  });

  if (!response.ok) {
    let message = `Upload failed (${response.status})`;
    try {
      const body = await response.json();
      if (typeof body.detail === "string") message = body.detail;
    } catch {
      // fall back to generic message
    }
    throw new Error(message);
  }

  return response.json();
}

export { API_BASE_URL };

