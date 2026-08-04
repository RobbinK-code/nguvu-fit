import "./PhoneInput.css";

// Only Kenya is wired to a working payment rail (Safaricom Daraja STK Push
// doesn't route to other countries/carriers). The rest are listed so the
// control is ready to extend later without being misleading about what
// works today.
export const COUNTRIES = [
  { code: "KE", dial: "254", flag: "🇰🇪", label: "Kenya", enabled: true },
  { code: "UG", dial: "256", flag: "🇺🇬", label: "Uganda", enabled: false },
  { code: "TZ", dial: "255", flag: "🇹🇿", label: "Tanzania", enabled: false },
  { code: "RW", dial: "250", flag: "🇷🇼", label: "Rwanda", enabled: false },
];

// Accepts the way people actually type Kenyan numbers - 07XXXXXXXX,
// 01XXXXXXXX, with or without a leading 0, with or without spaces -
// and normalizes to the 2547XXXXXXXX / 2541XXXXXXXX format Daraja expects.
export function normalizeLocalNumber(dialCode, rawLocal) {
  const digits = rawLocal.replace(/\D/g, "");
  const trimmed = digits.startsWith("0") ? digits.slice(1) : digits;
  return `${dialCode}${trimmed}`;
}

export function isValidKenyanLocalNumber(rawLocal) {
  const digits = rawLocal.replace(/\D/g, "");
  const trimmed = digits.startsWith("0") ? digits.slice(1) : digits;
  return /^[71]\d{8}$/.test(trimmed);
}

export default function PhoneInput({ country, onCountryChange, localNumber, onLocalNumberChange }) {
  const selected = COUNTRIES.find((c) => c.code === country) || COUNTRIES[0];

  return (
    <div className="phone-input">
      <div className="phone-input-country">
        <select
          value={country}
          onChange={(e) => onCountryChange(e.target.value)}
          aria-label="Country"
        >
          {COUNTRIES.map((c) => (
            <option key={c.code} value={c.code} disabled={!c.enabled}>
              {c.flag} +{c.dial} {!c.enabled ? "(coming soon)" : ""}
            </option>
          ))}
        </select>
      </div>
      <input
        className="phone-input-local"
        type="tel"
        inputMode="numeric"
        required
        placeholder="07XX XXX XXX"
        value={localNumber}
        onChange={(e) => onLocalNumberChange(e.target.value)}
        disabled={!selected.enabled}
      />
    </div>
  );
}
