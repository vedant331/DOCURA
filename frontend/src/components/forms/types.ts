// Presentational types for the form-session surfaces. They intentionally MIRROR the
// shapes the browser extension's pure modules already produce in its isolated world:
//   readiness  → extension/src/readiness.js  (computeReadiness)
//   retrieval  → extension/src/retrieval.js  (computeRetrieval)
//   matching   → extension/src/matching.js   (computeMatching)
//
// The backend does NOT expose these today (the form-session API stores only lifecycle +
// audit). So these types define the seam a future bridge (extension → web) would fill;
// until then the web pages render an honest "not available here" state and never invent
// field, candidate, confidence, or matching data.

export type FieldStatusKind =
  | "matched"
  | "available"
  | "unknown"
  | "ambiguous"
  | "conflict"
  | "requires_user"
  | "blocked"
  | "missing"
  | "declaration";

export interface Candidate {
  value: string;
  source?: string;
  confidence?: number | null;
}

export interface DetectedField {
  fieldId: string;
  type: string;
  required: boolean;
  status: FieldStatusKind;
  meaning?: string | null;
  proposedValue?: string | null;
  confidence?: number | null;
  source?: string | null;
  candidates?: Candidate[];
  reason?: string;
  isDeclaration?: boolean;
}

export interface ReadinessData {
  requiredFields: number;
  requiredDocuments: number;
  available: number;
  missing: number;
  requiresUser: number;
  fields: DetectedField[];
}

export type MatchStatusKind =
  | "matched"
  | "multiple"
  | "missing"
  | "preparing"
  | "ready"
  | "blocked"
  | "quality_loss"
  | "unresolved";

export interface UploadFieldMatch {
  fieldId: string;
  requiredType?: string | null;
  constraints?: { format?: string; maxSize?: string; dimensions?: string };
  status: MatchStatusKind;
  candidates?: { documentId: string; filename?: string; confidence?: number | null }[];
  reason?: string;
}
