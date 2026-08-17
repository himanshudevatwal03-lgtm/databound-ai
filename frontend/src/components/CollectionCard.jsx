/**
 * CollectionCard
 *
 * Rendered as a filter pill in the sidebar/tab row: click to filter the
 * document list down to this collection. Kept as a single small component
 * (rather than folding into the Documents page) since it's reused for
 * both the "All Documents" pseudo-collection and real ones.
 */
export default function CollectionCard({ name, documentCount, isActive, onClick, onDelete }) {
  return (
    <div className={`collection-pill${isActive ? " active" : ""}`} onClick={onClick}>
      <span>{name}</span>
      <span className="collection-count">{documentCount}</span>
      {onDelete && (
        <button
          className="collection-delete"
          aria-label={`Delete ${name}`}
          onClick={(e) => {
            e.stopPropagation();
            onDelete();
          }}
        >
          ×
        </button>
      )}
    </div>
  );
}
