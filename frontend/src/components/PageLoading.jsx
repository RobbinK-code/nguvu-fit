export default function PageLoading({ message = "Loading…" }) {
  return (
    <div className="page-loading container">
      <div className="spinner" aria-hidden="true" />
      <p>{message}</p>
    </div>
  );
}
