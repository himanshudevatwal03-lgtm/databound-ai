const STATUS_LABEL = {
  ready: "Ready",
  processing: "Processing",
  failed: "Failed",
};

function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/**
 * DocumentCard
 *
 * One row in the document list: filename, type/size/status, a short
 * content preview (or the processing error, if extraction failed), and a
 * delete action. "Ask Questions", "Summarize", and "Compare" (spec
 * section 16) are visually staged here but wired up starting Phase 5+,
 * once there's a QA pipeline for them to call.
 */
export default function DocumentCard({ document, onDelete }) {
  return (
    <div className="card document-card card-interactive">
      <div className="document-card-main">
        <div className="document-card-header">
          <span className={`status-dot ${document.status === "ready" ? "ok" : document.status === "failed" ? "error" : "pending"}`} />
          <span className="document-filename">{document.filename}</span>
          <span className="document-meta mono">
            {document.file_type.toUpperCase()} · {formatFileSize(document.file_size)}
          </span>
        </div>

        {document.status === "failed" ? (
          <p className="document-error">{document.processing_error}</p>
        ) : (
          <p className="document-preview">{document.preview || "No preview available."}</p>
        )}
      </div>

      <div className="document-card-actions">
        <span className="document-status-label">{STATUS_LABEL[document.status] || document.status}</span>
        <button className="btn-text" onClick={() => onDelete(document.id)}>
          Delete
        </button>
      </div>
    </div>
  );
}
