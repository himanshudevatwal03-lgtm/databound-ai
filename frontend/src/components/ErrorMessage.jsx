/**
 * ErrorMessage
 *
 * A consistent way to show error states across the app (failed API calls,
 * validation errors, etc.), instead of every page rolling its own red text.
 */
export default function ErrorMessage({ message }) {
  if (!message) return null;
  return (
    <div className="error-message" role="alert">
      <strong>Something went wrong:</strong> {message}
    </div>
  );
}
