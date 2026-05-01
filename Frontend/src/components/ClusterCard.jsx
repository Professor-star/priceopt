import "./ClusterCard.css";

// ── Platform color map — add new platforms here ────────────────────────────
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
  const full  = Math.floor(rating);
  const half  = rating - full >= 0.5;
  const empty = 5 - full - (half ? 1 : 0);
  return (
    <span className="stars" title={`${rating}/5`}>
      {"★".repeat(full)}
      {half ? "½" : ""}
      {"☆".repeat(empty)}
      <span className="rating-num">{rating}</span>
    </span>
  );
}

export default function ClusterCard({ cluster, rank }) {
  const savings =
    cluster.items.length > 1
      ? Math.max(...cluster.items.map((i) => i.price)) - cluster.best_price
      : 0;

  return (
    <div className={`cluster-card ${rank === 0 ? "rank-first" : ""}`}>

      {/* ── Card header ── */}
      <div className="card-header">
        {cluster.brand && (
          <span className="brand-tag">{cluster.brand.toUpperCase()}</span>
        )}
        <h2 className="card-title">{cluster.cluster_name}</h2>
        <div className="card-meta-row">
          <span className="cluster-count">
            {cluster.items.length} listing{cluster.items.length !== 1 ? "s" : ""}
          </span>
          {/* Show which platforms have this product */}
          <span className="platform-pills">
            {cluster.platforms_available?.map((p) => (
              <PlatformBadge key={p} platform={p} />
            ))}
          </span>
          {savings > 0 && (
            <span className="savings-badge">
              Save up to ₹{savings.toLocaleString("en-IN")}
            </span>
          )}
        </div>
      </div>

      {/* ── Price comparison table ── */}
      <div className="items-table">
        {cluster.items.map((item, i) => (
          <div
            key={i}
            className={`item-row ${item.is_best_deal ? "best-deal" : ""}`}
          >
            <div className="item-left">
              <PlatformBadge platform={item.platform} />
              <span className="item-title">{item.title}</span>
            </div>
            <div className="item-right">
              <StarRating rating={item.rating} />
              <span className="item-price">
                ₹{item.price.toLocaleString("en-IN")}
              </span>
              {item.is_best_deal && (
                <span className="best-tag">🏆 Best Deal</span>
              )}
              <a
                className="view-link"
                href={item.link}
                target="_blank"
                rel="noopener noreferrer"
              >
                View →
              </a>
            </div>
          </div>
        ))}
      </div>

      {/* ── Footer summary ── */}
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
