import { useCallback, useEffect, useState } from "react";
import * as api from "../services/api.js";
import UploadBox from "../components/UploadBox.jsx";
import DocumentCard from "../components/DocumentCard.jsx";
import CollectionCard from "../components/CollectionCard.jsx";
import Modal from "../components/Modal.jsx";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import ErrorMessage from "../components/ErrorMessage.jsx";

/**
 * Documents ("My Data")
 *
 * The Phase 3 core screen (spec section 16). Combines:
 *   - a collections sidebar (create/select/delete, spec section 17)
 *   - drag-and-drop upload (spec section 9/10)
 *   - a document list scoped to the selected collection (or all documents)
 *
 * Ask Questions / Summarize / Compare document actions are intentionally
 * not wired up yet — those need Phases 4/5/9's retrieval and QA pipeline
 * first. Delete is fully functional now.
 */
export default function Documents() {
  const [collections, setCollections] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [activeCollectionId, setActiveCollectionId] = useState(null); // null = "All Documents"
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadErrors, setUploadErrors] = useState([]);
  const [showNewCollection, setShowNewCollection] = useState(false);
  const [newCollectionName, setNewCollectionName] = useState("");

  const loadCollections = useCallback(async () => {
    const data = await api.listCollections();
    setCollections(data);
  }, []);

  const loadDocuments = useCallback(async (collectionId) => {
    const data = await api.listDocuments(collectionId ?? undefined);
    setDocuments(data);
  }, []);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([loadCollections(), loadDocuments(activeCollectionId)])
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeCollectionId]);

  async function handleFilesSelected(files) {
    setUploading(true);
    setUploadErrors([]);
    const failures = [];

    for (const file of files) {
      try {
        await api.uploadDocument(file, activeCollectionId ?? undefined);
      } catch (err) {
        failures.push(`${file.name}: ${err.message}`);
      }
    }

    setUploadErrors(failures);
    setUploading(false);
    await Promise.all([loadDocuments(activeCollectionId), loadCollections()]);
  }

  async function handleDeleteDocument(documentId) {
    await api.deleteDocument(documentId);
    setDocuments((prev) => prev.filter((d) => d.id !== documentId));
    loadCollections();
  }

  async function handleDeleteCollection(collectionId) {
    await api.deleteCollection(collectionId);
    if (activeCollectionId === collectionId) setActiveCollectionId(null);
    loadCollections();
    loadDocuments(activeCollectionId === collectionId ? null : activeCollectionId);
  }

  async function handleCreateCollection(e) {
    e.preventDefault();
    if (!newCollectionName.trim()) return;
    await api.createCollection({ name: newCollectionName.trim() });
    setNewCollectionName("");
    setShowNewCollection(false);
    loadCollections();
  }

  const totalDocumentCount = collections.reduce((sum, c) => sum + c.document_count, 0);

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
              documentCount={totalDocumentCount}
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
                onDelete={() => handleDeleteCollection(c.id)}
              />
            ))}
          </aside>

          <div className="documents-main">
            <UploadBox onFilesSelected={handleFilesSelected} disabled={uploading} />

            {uploading && <LoadingSpinner label="Uploading and processing..." />}
            {uploadErrors.map((msg, i) => (
              <ErrorMessage key={i} message={msg} />
            ))}

            {loading && <LoadingSpinner label="Loading documents..." />}
            <ErrorMessage message={error} />

            {!loading && !error && documents.length === 0 && (
              <p className="empty-state">
                No documents yet. Upload a .txt, .pdf, or .csv file above to get started.
              </p>
            )}

            <div className="document-list">
              {documents.map((doc) => (
                <DocumentCard key={doc.id} document={doc} onDelete={handleDeleteDocument} />
              ))}
            </div>
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
    </main>
  );
}
