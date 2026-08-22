import SourceCard from "./SourceCard.jsx";

/**
 * AnswerCard
 *
 * Renders one grounded answer: the text, a clear "Supported by provided
 * data" / "Not enough information" badge (spec section 18's chat example
 * shows this exact distinction), and expandable source citations. The
 * badge is the single most important visual element on this card — it's
 * the whole product's core promise made visible.
 */
export default function AnswerCard({ answer, supported, sources }) {
  return (
    <div className="card answer-card">
      <p className="answer-text">{answer}</p>

      <div className={`supported-badge ${supported ? "supported" : "unsupported"}`}>
        {supported ? (
          <>
            <span className="supported-badge-icon">✓</span> Supported by provided data
          </>
        ) : (
          <>
            <span className="supported-badge-icon">i</span> Not found in your documents
          </>
        )}
      </div>

      {supported && sources.length > 0 && (
        <div className="source-list">
          {sources.map((s, i) => (
            <SourceCard key={i} source={s} />
          ))}
        </div>
      )}
    </div>
  );
}
