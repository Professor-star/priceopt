import { useState, useCallback, useEffect } from "react";
import SearchBar from "./components/SearchBar";
import FilterBar from "./components/FilterBar";
import ClusterCard from "./components/ClusterCard";
import EmptyState from "./components/EmptyState";
import Loader from "./components/Loader";
import "./styles/global.css";

// ── Point to deployed Render backend ──────────────────────────────────────
const API_BASE = "https://priceopt-backend.onrender.com";

export default function App() {
  const [query, setQuery]       = useState("");
  const [clusters, setClusters] = useState([]);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState(null);
  const [meta, setMeta]         = useState(null);
  const [sort, setSort]         = useState("price_asc");
  const [brand, setBrand]       = useState("");
  const [brands, setBrands]     = useState([]);
  const [searched, setSearched] = useState(false);

  // Fetch brand list on mount
  useEffect(() => {
    fetch(`${API_BASE}/brands`)
      .then((r) => r.json())
      .then(setBrands)
      .catch(() => {});
  }, []);

  const doSearch = useCallback(
    async (q = query, s = sort, b = brand) => {
      if (!q.trim()) return;
      setLoading(true);
      setError(null);
      setSearched(true);

      try {
        const params = new URLSearchParams({ q: q.trim(), sort: s });
        if (b) params.set("brand", b);

        const res = await fetch(`${API_BASE}/search?${params}`);

        if (!res.ok) {
          const errorData = await res.json().catch(() => ({}));
          throw new Error(errorData.error || "Server error");
        }

        const data = await res.json();
        setClusters(data.clusters || []);
        setMeta({ query: data.query, total: data.total_clusters });
      } catch (err) {
        setError(err.message);
        setClusters([]);
      } finally {
        setLoading(false);
      }
    },
    [query, sort, brand]
  );

  const handleSortChange = (newSort) => {
    setSort(newSort);
    if (searched) doSearch(query, newSort, brand);
  };

  const handleBrandChange = (newBrand) => {
    setBrand(newBrand);
    if (searched) doSearch(query, sort, newBrand);
  };

  return (
    <div className="app">
      {/* ── Hero / Header ── */}
      <header className="hero">
        <div className="hero-glow" />
        <div className="hero-inner">
          <div className="logo-lockup">
            <span className="logo-icon">⚡</span>
            <span className="logo-text">PriceOpt</span>
          </div>
          <p className="hero-sub">
            Intelligent cross-platform price comparison
          </p>
          <SearchBar
            value={query}
            onChange={setQuery}
            onSearch={() => doSearch()}
            loading={loading}
          />
          <div className="chip-row">
            {["shoes", "iphone 14", "headphones", "samsung"].map((s) => (
              <button
                key={s}
                className="chip"
                onClick={() => {
                  setQuery(s);
                  doSearch(s, sort, brand);
                }}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
      </header>

      {/* ── Main content ── */}
      <main className="main">
        {searched && !loading && clusters.length > 0 && (
          <FilterBar
            sort={sort}
            onSortChange={handleSortChange}
            brand={brand}
            brands={brands}
            onBrandChange={handleBrandChange}
            meta={meta}
          />
        )}

        {loading && <Loader />}

        {!loading && error && (
          <div className="error-banner">⚠️ {error}</div>
        )}

        {!loading && searched && !error && clusters.length === 0 && (
          <EmptyState query={query} />
        )}

        {!loading && clusters.length > 0 && (
          <div className="results-grid">
            {clusters.map((cluster, i) => (
              <ClusterCard key={i} cluster={cluster} rank={i} />
            ))}
          </div>
        )}
      </main>

      <footer className="footer">
        <span>PriceOpt — Avengers Team • Intelligent Price Comparison</span>
      </footer>
    </div>
  );
}
