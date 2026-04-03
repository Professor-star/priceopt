import "./SearchBar.css";

export default function SearchBar({ value, onChange, onSearch, loading }) {
  const handleKey = (e) => {
    if (e.key === "Enter") onSearch();
  };

  return (
    <div className="search-wrap">
      <div className="search-box">
        <span className="search-icon">🔍</span>
        <input
          className="search-input"
          type="text"
          placeholder='Try "shoes", "iphone 14", "headphones" …'
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKey}
          autoFocus
        />
        {value && (
          <button
            className="clear-btn"
            onClick={() => onChange("")}
            aria-label="Clear"
          >
            ✕
          </button>
        )}
      </div>
      <button
        className="search-btn"
        onClick={onSearch}
        disabled={loading || !value.trim()}
      >
        {loading ? <span className="btn-spinner" /> : "Search"}
      </button>
    </div>
  );
}
