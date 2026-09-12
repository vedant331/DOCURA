// Minimal client-side validation for the auth forms. This is UX only — the backend is
// the authority (it enforces the real email + password-complexity rules and its errors
// are surfaced verbatim). We just avoid obviously-pointless round-trips.

export function isEmail(value: string): boolean {
  // Deliberately permissive: reject only clearly-not-an-email input; let the backend's
  // EmailStr be the real judge.
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value.trim());
}

export function required(value: string): boolean {
  return value.trim().length > 0;
}
