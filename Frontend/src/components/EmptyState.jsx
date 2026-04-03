// EmptyState.jsx
export function EmptyState({ query }) {
  return (
    <div className="empty-state">
      <div className="empty-icon">🔎</div>
      <h3>No results for "{query}"</h3>
      <p>Try a broader term like "shoes", "headphones", or a brand name.</p>
    </div>
  );
}

export default EmptyState;
