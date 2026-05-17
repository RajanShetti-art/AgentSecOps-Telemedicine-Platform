export default function Toast({ type = "success", message, onClose }) {
  if (!message) {
    return null;
  }

  return (
    <div className={`toast ${type}`} role="status" aria-live="polite">
      <span>{message}</span>
      <button type="button" className="toast-close" onClick={onClose} aria-label="Dismiss notification">
        ×
      </button>
    </div>
  );
}