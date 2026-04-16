export default function Spinner() {
  return (
    <div className="spinner-wrap" role="status" aria-live="polite">
      <div className="spinner" />
      <span>Loading...</span>
    </div>
  );
}
