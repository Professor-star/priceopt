import "./FilterBar.css";

export default function FilterBar({
  sort, onSortChange,
  brand, brands, onBrandChange,
  meta,
}) {
  return (
    <div className="filter-bar">
      <div className="filter-meta">
        <span className="meta-query">"{meta?.query}"</span>
        <span className="meta-count">{meta?.total} group{meta?.total !== 1 ? "s" : ""} found</span>
      </div>
      <div className="filter-controls">
        {/* Sort */}
        <div className="filter-group">
          <label>Sort</label>
          <select value={sort} onChange={(e) => onSortChange(e.target.value)}>
            <option value="price_asc">Price: Low → High</option>
            <option value="price_desc">Price: High → Low</option>
          </select>
        </div>
        {/* Brand filter */}
        <div className="filter-group">
          <label>Brand</label>
          <select value={brand} onChange={(e) => onBrandChange(e.target.value)}>
            <option value="">All brands</option>
            {brands.map((b) => (
              <option key={b} value={b.toLowerCase()}>{b}</option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}
