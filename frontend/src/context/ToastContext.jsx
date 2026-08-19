import { createContext, useCallback, useContext, useState } from "react";

/**
 * ToastContext
 *
 * App-wide transient notifications ("Document uploaded", "Collection
 * deleted", etc.) — the kind of live feedback that makes an app feel
 * responsive rather than static. Any component calls useToast() to fire
 * one; ToastContainer (rendered once near the root) handles displaying
 * and auto-dismissing them.
 */
const ToastContext = createContext(null);

let nextId = 1;

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);

  const dismissToast = useCallback((id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  }, []);

  const showToast = useCallback(
    (message, type = "info", duration = 3500) => {
      const id = nextId++;
      setToasts((prev) => [...prev, { id, message, type }]);
      if (duration > 0) {
        setTimeout(() => dismissToast(id), duration);
      }
      return id;
    },
    [dismissToast]
  );

  const value = {
    toasts,
    showToast,
    dismissToast,
    success: (msg) => showToast(msg, "success"),
    error: (msg) => showToast(msg, "error", 5000),
    info: (msg) => showToast(msg, "info"),
  };

  return <ToastContext.Provider value={value}>{children}</ToastContext.Provider>;
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within a ToastProvider");
  }
  return context;
}
