import Modal from "./Modal.jsx";

/**
 * ConfirmDialog
 *
 * A focused confirm/cancel prompt built on top of Modal, for destructive
 * actions (deleting a document or collection). Replacing an instant
 * delete with a deliberate confirm step is both better UX (harder to lose
 * data by accident) and makes the app feel more considered/dynamic rather
 * than abrupt.
 */
export default function ConfirmDialog({ title, message, confirmLabel = "Delete", onConfirm, onCancel }) {
  return (
    <Modal title={title} onClose={onCancel}>
      <p style={{ color: "var(--color-ink-muted)", marginBottom: 20 }}>{message}</p>
      <div style={{ display: "flex", gap: 10, justifyContent: "flex-end" }}>
        <button className="btn-text" onClick={onCancel}>
          Cancel
        </button>
        <button className="btn-danger" onClick={onConfirm}>
          {confirmLabel}
        </button>
      </div>
    </Modal>
  );
}
