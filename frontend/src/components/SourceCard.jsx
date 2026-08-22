import { useState } from "react";

/**
 * SourceCard
 *
 * One citation: filename plus page/row if applicable, expandable to show
 * the exact quoted text the answer was grounded in (spec section 35,
 * "View Source"). Collapsed by default so a multi-source answer doesn't
 * turn into a wall of quoted text.
 */
export default function SourceCard({ source }) {
  const [expanded, setExpanded] = useState(false);

  const location = source.page_number != null ? `Page ${source.page_number}` : source.row_number != null ? `Row ${source.row_number}` : null;

  return (
    <div className="source-card">
      <button className="source-card-header" onClick={() => setExpanded((v) => !v)} aria-expanded={expanded}>
        <span className="source-card-icon">{expanded ? "▾" : "▸"}</span>
        <span className="source-card-filename">{source.filename}</span>
        {location && <span className="source-card-location mono">{location}</span>}
      </button>
      {expanded && <p className="source-card-text">"{source.text}"</p>}
    </div>
  );
}
