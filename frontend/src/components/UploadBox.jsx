import { useRef, useState } from "react";

/**
 * UploadBox
 *
 * A drag-and-drop (and click-to-browse) upload target. Deliberately
 * dumb: it just hands the chosen File objects up to onFilesSelected and
 * lets the parent page (Documents.jsx) own the actual upload/progress/
 * error state, since that's shared with the collection-selection UI
 * around it.
 */
export default function UploadBox({ onFilesSelected, disabled }) {
  const inputRef = useRef(null);
  const [isDragOver, setIsDragOver] = useState(false);

  function handleDrop(e) {
    e.preventDefault();
    setIsDragOver(false);
    if (disabled) return;
    const files = Array.from(e.dataTransfer.files || []);
    if (files.length) onFilesSelected(files);
  }

  function handleFileInputChange(e) {
    const files = Array.from(e.target.files || []);
    if (files.length) onFilesSelected(files);
    e.target.value = ""; // allow re-selecting the same file later
  }

  return (
    <div
      className={`upload-box${isDragOver ? " drag-over" : ""}${disabled ? " disabled" : ""}`}
      onClick={() => !disabled && inputRef.current?.click()}
      onDragOver={(e) => {
        e.preventDefault();
        if (!disabled) setIsDragOver(true);
      }}
      onDragLeave={() => setIsDragOver(false)}
      onDrop={handleDrop}
      role="button"
      tabIndex={0}
      aria-disabled={disabled}
    >
      <div className="upload-box-icon">+</div>
      <p className="upload-box-title">
        {disabled ? "Uploading..." : "Drop files here or click to upload"}
      </p>
      <p className="upload-box-hint">Supports .txt, .pdf, .csv</p>
      <input
        ref={inputRef}
        type="file"
        accept=".txt,.pdf,.csv"
        multiple
        onChange={handleFileInputChange}
        disabled={disabled}
        style={{ display: "none" }}
      />
    </div>
  );
}
