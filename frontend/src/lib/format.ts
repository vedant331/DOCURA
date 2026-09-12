// Small, dependency-free formatting helpers shared across the app.

export function formatBytes(bytes: number): string {
  if (!Number.isFinite(bytes) || bytes < 0) return "—";
  if (bytes < 1024) return `${bytes} B`;
  const units = ["KB", "MB", "GB"];
  let value = bytes / 1024;
  let i = 0;
  while (value >= 1024 && i < units.length - 1) {
    value /= 1024;
    i += 1;
  }
  return `${value.toFixed(value < 10 ? 1 : 0)} ${units[i]}`;
}

export function formatDate(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

export function formatDateTime(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "—";
  return d.toLocaleString(undefined, {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

// A short, human label for a canonical attribute id like "person.full_name".
export function attributeLabel(canonicalIdentifier: string): string {
  const leaf = canonicalIdentifier.split(".").pop() ?? canonicalIdentifier;
  return leaf
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(" ");
}

// The scope group ("person", "qualification", …) for grouping the record view.
export function attributeGroup(canonicalIdentifier: string): string {
  const head = canonicalIdentifier.split(".")[0] ?? "other";
  return head.charAt(0).toUpperCase() + head.slice(1);
}
