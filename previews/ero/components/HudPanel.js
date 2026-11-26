export default function HudPanel({ title, children, className = '', aside = null }) {
  return (
    <section className={`hud-panel ${className}`}>
      <header className="hud-title">
        <h2>{title}</h2>
        {aside}
      </header>
      <div className="hud-body">{children}</div>
    </section>
  );
}
