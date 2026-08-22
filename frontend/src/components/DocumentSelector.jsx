/**
 * DocumentSelector
 *
 * Lets the user scope a question to everything, one collection, or one
 * specific document — spec section 17: "Users should be able to ask
 * questions against: one document, multiple documents, an entire
 * collection." "Multiple documents" (spec section 26) beyond a whole
 * collection isn't exposed here yet; this covers the two most common
 * cases plus "search everything."
 */
export default function DocumentSelector({ collections, documents, value, onChange }) {
  return (
    <select
      className="document-selector"
      value={value ? `${value.type}:${value.id}` : "all"}
      onChange={(e) => {
        const raw = e.target.value;
        if (raw === "all") {
          onChange(null);
          return;
        }
        const [type, id] = raw.split(":");
        onChange({ type, id });
      }}
    >
      <option value="all">All documents</option>
      {collections.length > 0 && (
        <optgroup label="Collections">
          {collections.map((c) => (
            <option key={c.id} value={`collection:${c.id}`}>
              {c.name}
            </option>
          ))}
        </optgroup>
      )}
      {documents.length > 0 && (
        <optgroup label="Documents">
          {documents.map((d) => (
            <option key={d.id} value={`document:${d.id}`}>
              {d.filename}
            </option>
          ))}
        </optgroup>
      )}
    </select>
  );
}
