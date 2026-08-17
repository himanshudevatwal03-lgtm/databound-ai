/**
 * Modal
 *
 * A minimal, reusable modal shell. Used first for "create collection" but
 * written generically so later phases (rename, confirm-delete, etc.)
 * reuse it instead of each rolling their own overlay/dialog markup.
 */
export default function Modal({ title, onClose, children }) {
  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-card" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>{title}</h3>
          <button className="modal-close" onClick={onClose} aria-label="Close">
            ×
          </button>
        </div>
        <div className="modal-body">{children}</div>
      </div>
    </div>
  );
}
