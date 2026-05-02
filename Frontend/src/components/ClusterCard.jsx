import "./ClusterCard.css";

// ── Platform color map ─────────────────────────────────────────────────────
const PLATFORM_COLOR = {
  Amazon:   { bg: "#ff9900", text: "#000" },
  Flipkart: { bg: "#2874f0", text: "#fff" },
  Meesho:   { bg: "#9b2cec", text: "#fff" },
  Snapdeal: { bg: "#e40000", text: "#fff" },
};

function PlatformBadge({ platform }) {
  const style = PLATFORM_COLOR[platform] || { bg: "#555", text: "#fff" };
  return (
    <span
      className="platform-badge"
      style={{ background: style.bg, color: style.text }}
    >
      {platform}
    </span>
  );
}

function StarRating({ rating }) {
  if (!rating || rating === 0) return <span className="stars no-rating">No rating</span>;
  const full  = Math.floor(rating);
  const half  = rating - full >= 0.5;
  const empty = 5 - full - (half ? 1 : 0);
  return (
    <span className="stars" title={`${rating}/5`}>
      {"★".repeat(full)}
      {half ? "½" : ""}
      {"☆".repeat(empty)}
      <span className="rating-num"> {rating}</span>
    </span>
  );
}

function PlatformRow({ item, isBest }) {
  if (!item) return null;
  return (
    <div className={`platform-row ${isBest ? "platform-row--best" : ""}`}>
      <div className="platform-row__left">
        <PlatformBadge platform={item.platform} />
        <div className="platform-row__details">
          <span className="platform-row__title">{item.title}</span>
          <StarRating rating={item.rating} />
        </div>
      </div>
      <div className="platform-row__right">
        <span className="platform-row__price">
          ₹{item.price.toLocaleString("en-IN")}
        </span>
        {isBest && <span className="best-tag">🏆 Best Deal</span>}
        <a
          className="view-link"
          href={item.link}
          target="_blank"
          rel="noopener noreferrer"
        >
          View on {item.platform} →
        </a>
      </div>
    </div>
  );
}

export default function ClusterCard({ cluster, rank }) {
  const amazon   = cluster.amazon_item;
  const snapdeal = cluster.snapdeal_item;
  const meesho   = cluster.items?.find(i => i.platform === "Meesho") || null;

  const savings        = cluster.savings || 0;
  const savingsPct     = cluster.savings_percent || 0;
  const bestPlatform   = cluster.best_platform;

  return (
    <div className={`cluster-card ${rank === 0 ? "rank-first" : ""}`}>

      {/* ── Header ── */}
      <div className="card-header">
        {cluster.brand && (
          <span className="brand-tag">{cluster.brand.toUpperCase()}</span>
        )}
        <h2 className="card-title">{cluster.cluster_name}</h2>
        <div className="card-meta-row">
          <span className="platform-pills">
            {cluster.platforms_available?.map((p) => (
              <PlatformBadge key={p} platform={p} />
            ))}
          </span>
          {savings > 0 && (
            <span className="savings-badge">
              Save ₹{savings.toLocaleString("en-IN")} ({savingsPct}% cheaper on {bestPlatform})
            </span>
          )}
        </div>
      </div>

      {/* ── Divider ── */}
      <div className="comparison-divider">
        <span>Price Comparison</span>
      </div>

      {/* ── Platform rows ── */}
      <div className="items-table">
        <PlatformRow item={amazon}   isBest={bestPlatform === "Amazon"}   />
        <PlatformRow item={snapdeal} isBest={bestPlatform === "Snapdeal"} />
        <PlatformRow item={meesho}   isBest={bestPlatform === "Meesho"}   />
      </div>

      {/* ── Footer ── */}
      <div className="card-footer">
        <span className="footer-label">Best price</span>
        <span className="footer-price">
          ₹{cluster.best_price.toLocaleString("en-IN")}
        </span>
        <span className="footer-on">on</span>
        <PlatformBadge platform={cluster.best_platform} />
      </div>

    </div>
  );
}
