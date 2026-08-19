import { useCallback, useEffect, useState } from "react";
import * as api from "../services/api.js";
import { useToast } from "../context/ToastContext.jsx";
import UploadBox from "../components/UploadBox.jsx";
import DocumentCard from "../components/DocumentCard.jsx";
import CollectionCard from "../components/CollectionCard.jsx";
import Modal from "../components/Modal.jsx";
import ConfirmDialog from "../components/ConfirmDialog.jsx";
import Skeleton from "../components/Skeleton.jsx";
import ErrorMessage from "../components/ErrorMessage.jsx";

/**
 * Documents ("My Data")
 *
 * The Phase 3 core screen (spec section 16), now with the interaction
 * polish from the UI pass: toasts confirm what just happened (upload
 * succeeded/failed, document/collection deleted) instead of the user
 * having to infer it from the list changing; deletes go through a
 * confirm dialog rather than firing instantly; per-file upload progress
 * is visible instead of one blanket spinner; and the list animates in
 * rather than popping into place.
 *
 * Ask Questions / Summarize / Compare document actions are still not
 * wired up — those need Phases 4/5/9's retrieval and QA pipeline first.
 */
export default function Documents() {
  const toast = useToast();

  const [collections, setCollections] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [allDocumentsCount, setAllDocumentsCount] = useState(0);
  const [activeCollectionId, setActiveCollectionId] = useState(null); // null = "All Documents"
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Per-file upload progress: { fileName: "uploading" | "done" | "error" }
  const [uploadProgress, setUploadProgress] = useState({});
  const isUploading = Object.values(uploadProgress).some((s) => s === "uploading");

  const [showNewCollection, setShowNewCollection] = useState(false);
  const [newCollectionName, setNewCollectionName] = useState("");
  const [confirmTarget, setConfirmTarget] = useState(null); // { type: "document"|"collection", id, label }

  const loadCollections = useCallback(async () => {
    const data = await api.listCollections();
    setCollections(data);
  }, []);

  const loadDocuments = useCallback(async (collectionId) => {
    const data = await api.listDocuments(collectionId ?? undefined);
    setDocuments(data);
  }, []);

  const loadAllDocumentsCount = useCallback(async () => {
    // Deliberately a separate, always-unfiltered call: summing each
    // collection's document_count would miss documents that aren't
    // assigned to any collection, undercounting "All Documents".
    const all = await api.listDocuments();
    setAllDocumentsCount(all.length);
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([loadCollections(), loadDocuments(activeCollectionId), loadAllDocumentsCount()])
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeCollectionId]);

  async function handleFilesSelected(files) {
    const initialProgress = {};
    files.forEach((f) => (initialProgress[f.name] = "uploading"));
    setUploadProgress(initialProgress);

    let succeeded = 0;
    let failed = 0;

    for (const file of files) {
      try {
        await api.uploadDocument(file, activeCollectionId ?? undefined);
        setUploadProgress((prev) => ({ ...prev, [file.name]: "done" }));
        succeeded += 1;
      } catch (err) {
        setUploadProgress((prev) => ({ ...prev, [file.name]: "error" }));
        toast.error(`${file.name}: ${err.message}`);
        failed += 1;
      }
    }

    if (succeeded > 0) {
      toast.success(succeeded === 1 ? "Document uploaded" : `${succeeded} documents uploaded`);
    }

    await Promise.all([loadDocuments(activeCollectionId), loadCollections(), loadAllDocumentsCount()]);

    // Clear the progress list a moment after everything settles, so the
    // "done" checkmarks are visible briefly rather than disappearing
    // the instant the upload finishes.
    setTimeout(() => setUploadProgress({}), failed > 0 ? 4000 : 1200);
  }

  function requestDeleteDocument(doc) {
    setConfirmTarget({ type: "document", id: doc.id, label: doc.filename });
  }

  function requestDeleteCollection(collection) {
    setConfirmTarget({ type: "collection", id: collection.id, label: collection.name });
  }

  async function handleConfirmedDelete() {
    if (!confirmTarget) return;
    const { type, id, label } = confirmTarget;
    setConfirmTarget(null);

    try {
      if (type === "document") {
        await api.deleteDocument(id);
        setDocuments((prev) => prev.filter((d) => d.id !== id));
        loadCollections();
        loadAllDocumentsCount();
        toast.success(`Deleted "${label}"`);
      } else {
        await api.deleteCollection(id);
        if (activeCollectionId === id) setActiveCollectionId(null);
        loadCollections();
        loadDocuments(activeCollectionId === id ? null : activeCollectionId);
        loadAllDocumentsCount();
        toast.success(`Deleted collection "${label}"`);
      }
    } catch (err) {
      toast.error(err.message);
    }
  }

  async function handleCreateCollection(e) {
    e.preventDefault();
    if (!newCollectionName.trim()) return;
    try {
      await api.createCollection({ name: newCollectionName.trim() });
      toast.success(`Created "${newCollectionName.trim()}"`);
      setNewCollectionName("");
      setShowNewCollection(false);
      loadCollections();
    } catch (err) {
      toast.error(err.message);
    }
  }

  const progressEntries = Object.entries(uploadProgress);

  return (
    <main>
      <div className="container documents-page">
        <div className="documents-header">
          <h1>My Data</h1>
          <p className="hero-sub">
            Upload documents, organize them into collections, and manage what DataBound AI can answer from.
          </p>
        </div>

        <div className="documents-layout">
          <aside className="collections-sidebar">
            <div className="collections-sidebar-header">
              <h3>Collections</h3>
              <button className="btn-text" onClick={() => setShowNewCollection(true)}>
                + New
              </button>
            </div>

            <CollectionCard
              name="All Documents"
              documentCount={allDocumentsCount}
              isActive={activeCollectionId === null}
              onClick={() => setActiveCollectionId(null)}
            />
            {collections.map((c) => (
              <CollectionCard
                key={c.id}
                name={c.name}
                documentCount={c.document_count}
                isActive={activeCollectionId === c.id}
                onClick={() => setActiveCollectionId(c.id)}
                onDelete={() => requestDeleteCollection(c)}
              />
            ))}
          </aside>

          <div className="documents-main">
            <UploadBox onFilesSelected={handleFilesSelected} disabled={isUploading} />

            {progressEntries.length > 0 && (
              <div className="upload-progress-list">
                {progressEntries.map(([name, status]) => (
                  <div key={name} className="upload-progress-row">
                    {status === "uploading" && <span className="mini-spinner" />}
                    {status === "done" && <span className="upload-status-icon ok">✓</span>}
                    {status === "error" && <span className="upload-status-icon error">!</span>}
                    <span className="upload-progress-name">{name}</span>
                  </div>
                ))}
              </div>
            )}

            <ErrorMessage message={error} />

            {loading ? (
              <div className="document-list">
                <Skeleton variant="card" count={3} />
              </div>
            ) : documents.length === 0 ? (
              <p className="empty-state">No documents yet. Upload a .txt, .pdf, or .csv file above to get started.</p>
            ) : (
              <div className="document-list">
                {documents.map((doc, i) => (
                  <div key={doc.id} className="animate-fade-in-up" style={{ animationDelay: `${Math.min(i, 8) * 35}ms` }}>
                    <DocumentCard document={doc} onDelete={() => requestDeleteDocument(doc)} />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {showNewCollection && (
        <Modal title="New collection" onClose={() => setShowNewCollection(false)}>
          <form onSubmit={handleCreateCollection} className="auth-form">
            <label className="field-label" htmlFor="collection-name">
              Name
            </label>
            <input
              id="collection-name"
              type="text"
              autoFocus
              value={newCollectionName}
              onChange={(e) => setNewCollectionName(e.target.value)}
              placeholder="e.g. College, Project, Personal"
            />
            <button type="submit" className="btn-primary">
              Create
            </button>
          </form>
        </Modal>
      )}

      {confirmTarget && (
        <ConfirmDialog
          title={confirmTarget.type === "document" ? "Delete document?" : "Delete collection?"}
          message={
            confirmTarget.type === "document"
              ? `"${confirmTarget.label}" will be permanently deleted.`
              : `"${confirmTarget.label}" will be deleted. Documents inside it won't be deleted — they'll move to All Documents.`
          }
          onConfirm={handleConfirmedDelete}
          onCancel={() => setConfirmTarget(null)}
        />
      )}
    </main>
  );
}
