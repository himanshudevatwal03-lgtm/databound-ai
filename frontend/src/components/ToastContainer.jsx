import { useToast } from "../context/ToastContext.jsx";

const ICON = { success: "✓", error: "!", info: "i" };

/**
 * ToastContainer
 *
 * Rendered once, near the app root (see main.jsx). Purely presentational
 * — all state lives in ToastContext. Toasts stack bottom-right and
 * animate in/out via CSS (see .toast styles in index.css).
 */
export default function ToastContainer() {
  const { toasts, dismissToast } = useToast();

  if (toasts.length === 0) return null;

  return (
    <div className="toast-stack" role="status" aria-live="polite">
      {toasts.map((toast) => (
        <div key={toast.id} className={`toast toast-${toast.type}`} onClick={() => dismissToast(toast.id)}>
          <span className={`toast-icon toast-icon-${toast.type}`}>{ICON[toast.type] || "i"}</span>
          <span className="toast-message">{toast.message}</span>
        </div>
      ))}
    </div>
  );
}
