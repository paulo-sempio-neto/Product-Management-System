type LogoProps = { tone?: "ink" | "light"; showName?: boolean };

/** Gôndola mark: three products resting on a shelf. */
export default function Logo({ tone = "ink", showName = true }: LogoProps) {
  const ink = tone === "light" ? "#ffffff" : "#0e1530";
  return (
    <span className={`logo logo--${tone}`}>
      <svg width="30" height="30" viewBox="0 0 32 32" aria-hidden="true">
        <rect x="3" y="9" width="8" height="15" rx="2" fill="#ffd23f" />
        <rect x="13" y="13" width="7" height="11" rx="3.5" fill="#ff5a5f" />
        <rect x="22" y="6" width="7" height="18" rx="2" fill={ink} />
        <rect x="1" y="25" width="30" height="4" rx="1.5" fill={ink} />
      </svg>
      {showName && <span className="logo__name">Gôndola</span>}
    </span>
  );
}
