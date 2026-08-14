/**
 * LoadingSpinner
 *
 * A small reusable spinner shown while data is being fetched. Every
 * feature added in later phases (document lists, chat responses, etc.)
 * will reuse this component instead of each writing its own.
 */
export default function LoadingSpinner({ label = "Loading..." }) {
  return (
    <div className="loading-spinner" role="status" aria-live="polite">
      <div className="spinner" />
      <span>{label}</span>
    </div>
  );
}
