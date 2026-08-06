// Small original line-icon illustrations for equipment categories - kept
// abstract/geometric rather than photographic, both to avoid any
// copyright questions around real equipment photography and to match
// the app's flat visual language.

function IconBase({ children }) {
  return (
    <svg viewBox="0 0 64 64" width="40" height="40" fill="none" xmlns="http://www.w3.org/2000/svg">
      {children}
    </svg>
  );
}

export function PlateStackIcon() {
  return (
    <IconBase>
      <rect x="10" y="28" width="44" height="8" rx="2" fill="var(--sunrise)" />
      <rect x="16" y="18" width="32" height="8" rx="2" fill="var(--gold)" />
      <rect x="4" y="38" width="56" height="8" rx="2" fill="var(--sunrise)" />
      <rect x="28" y="10" width="8" height="44" rx="2" fill="#24211c" opacity="0.15" />
    </IconBase>
  );
}

export function CableIcon() {
  return (
    <IconBase>
      <rect x="8" y="6" width="10" height="52" rx="2" fill="#24211c" opacity="0.15" />
      <circle cx="13" cy="16" r="5" fill="var(--gold)" />
      <path d="M13 21 L44 44" stroke="var(--sunrise)" strokeWidth="3" strokeLinecap="round" />
      <rect x="40" y="42" width="16" height="8" rx="3" fill="var(--sunrise)" />
    </IconBase>
  );
}

export function BarbellIcon() {
  return (
    <IconBase>
      <rect x="6" y="28" width="52" height="6" rx="3" fill="#24211c" opacity="0.2" />
      <rect x="4" y="20" width="8" height="22" rx="2" fill="var(--sunrise)" />
      <rect x="14" y="24" width="6" height="14" rx="2" fill="var(--gold)" />
      <rect x="52" y="20" width="8" height="22" rx="2" fill="var(--sunrise)" />
      <rect x="44" y="24" width="6" height="14" rx="2" fill="var(--gold)" />
    </IconBase>
  );
}

export function CardioIcon() {
  return (
    <IconBase>
      <path
        d="M6 40 L20 40 L26 26 L34 48 L40 34 L46 40 L58 40"
        stroke="var(--sunrise)"
        strokeWidth="3.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />
      <circle cx="6" cy="40" r="3" fill="var(--gold)" />
      <circle cx="58" cy="40" r="3" fill="var(--gold)" />
    </IconBase>
  );
}

const ICONS = {
  "plate-stack": PlateStackIcon,
  cable: CableIcon,
  barbell: BarbellIcon,
  cardio: CardioIcon,
};

export default function EquipmentIcon({ icon }) {
  const Component = ICONS[icon] || PlateStackIcon;
  return <Component />;
}
