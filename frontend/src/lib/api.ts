// The frontend's whole conversation with the DOCURA backend auth API.
//
// It speaks the SAME contract the extension already uses (see extension/src/api.js):
// a bearer token from POST /auth/login, carried as `Authorization: Bearer <token>` on
// every authenticated call, and every non-2xx surfaced through the problem+json
// `detail` string. There is no second auth architecture — this is a browser client for
// the endpoints in backend/app/api/auth.py.

import { readToken } from "@/auth/session";

const BASE = (import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000").replace(/\/$/, "");

// ---- shared response shapes (backend/app/schemas/auth.py) -------------------

export interface UserResponse {
  id: string;
  email: string;
  is_active: boolean;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: "bearer";
  expires_at: string;
  user: UserResponse;
}

export interface PasswordResetRequestResponse {
  status: "accepted";
  detail: string;
}

export interface PasswordResetConfirmResponse {
  status: "reset";
  sessions_revoked: number;
}

// An error the UI can render inside the Mercury visual language: a human `detail`
// (from problem+json) plus the HTTP status, so callers can branch on 401 vs 5xx.
export class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

function authHeaders(token: string): Record<string, string> {
  return { Authorization: `Bearer ${token}` };
}

async function request<T>(path: string, init: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE}${path}`, init);
  } catch {
    // Transport failure (backend unreachable). Fail toward a clear, non-technical state.
    throw new ApiError("Cannot reach DOCURA. Check your connection and try again.", 0);
  }
  if (!response.ok) {
    let detail = `Request failed (${response.status}).`;
    try {
      const body = await response.json();
      if (body && typeof body.detail === "string") detail = body.detail;
    } catch {
      /* non-JSON error body; keep the generic message */
    }
    throw new ApiError(detail, response.status);
  }
  if (response.status === 204) return undefined as T;
  return (await response.json()) as T;
}

const jsonInit = (body: unknown): RequestInit => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

// ---- endpoints --------------------------------------------------------------

export function login(email: string, password: string) {
  return request<LoginResponse>("/auth/login", jsonInit({ email, password }));
}

// Registration does NOT open a session server-side (no token returned) — the account
// then signs in. Returns the created account.
export function register(email: string, password: string) {
  return request<UserResponse>("/auth/register", jsonInit({ email, password }));
}

export function requestPasswordReset(email: string) {
  return request<PasswordResetRequestResponse>(
    "/auth/password-reset/request",
    jsonInit({ email }),
  );
}

export function confirmPasswordReset(token: string, password: string) {
  return request<PasswordResetConfirmResponse>(
    "/auth/password-reset/confirm",
    jsonInit({ token, password }),
  );
}

export function me(token: string) {
  return request<UserResponse>("/users/me", { headers: authHeaders(token) });
}

export function logout(token: string) {
  return request<{ revoked: number }>("/auth/logout", {
    method: "POST",
    headers: authHeaders(token),
  });
}

// ============================================================================
// Authenticated resource APIs (documents, record, form sessions, sessions).
//
// These reuse the SAME bearer token as auth (readToken from @/auth/session) so
// there is one auth system, and the SAME problem+json error handling. Every path
// below maps to an endpoint that already exists in backend/app/api — no invented
// endpoints. Where a product capability has no backend yet (assistant, attribute
// correction, conflict resolution, extension-side readiness/matching/approval
// detail), there is deliberately NO function here: the UI renders an honest
// not-connected seam instead of calling a fake endpoint.
// ============================================================================

function authInit(init: RequestInit = {}): RequestInit {
  const token = readToken();
  if (!token) throw new ApiError("Your session has ended. Sign in again.", 401);
  return { ...init, headers: { ...(init.headers ?? {}), ...authHeaders(token) } };
}

function authRequest<T>(path: string, init: RequestInit = {}): Promise<T> {
  return request<T>(path, authInit(init));
}

// ---- documents (backend/app/api/documents.py) ------------------------------

export type DocumentType = "unclassified";
export type DocumentStatus = "queued" | "processing" | "ready" | "needs_review" | "failed";

export interface DocumentResponse {
  id: string;
  original_filename: string;
  content_type: string;
  byte_size: number;
  checksum_sha256: string;
  document_type: DocumentType;
  status: DocumentStatus;
  failure_reason: string | null;
  created_at: string;
  updated_at: string;
}

export interface DocumentListResponse {
  documents: DocumentResponse[];
  count: number;
}

export interface RejectedUpload {
  filename: string;
  reason: string;
  remediation: string;
}

export interface UploadResponse {
  accepted: DocumentResponse[];
  rejected: RejectedUpload[];
}

export interface UploadLimits {
  accepted_media_types: string[];
  accepted_extensions: string[];
  max_document_bytes: number;
  max_documents_per_upload: number;
}

export interface DocumentDeletionResponse {
  deleted: boolean;
  id: string;
  original_filename: string;
  content_type: string;
  byte_size: number;
  detail: string;
}

export function getUploadLimits() {
  return authRequest<UploadLimits>("/documents/limits");
}

export function listDocuments() {
  return authRequest<DocumentListResponse>("/documents");
}

export function getDocument(id: string) {
  return authRequest<DocumentResponse>(`/documents/${id}`);
}

export function uploadDocuments(files: File[]) {
  const form = new FormData();
  for (const f of files) form.append("files", f);
  // Note: no Content-Type header — the browser sets the multipart boundary.
  return authRequest<UploadResponse>("/documents", { method: "POST", body: form });
}

export function reprocessDocument(id: string) {
  return authRequest<DocumentResponse>(`/documents/${id}/reprocess`, { method: "POST" });
}

export function deleteDocument(id: string) {
  return authRequest<DocumentDeletionResponse>(`/documents/${id}`, { method: "DELETE" });
}

// The original bytes, exactly as uploaded (FR-DOC-004), for preview/download. Returns a
// Blob so the caller can make an object URL; the original is never modified.
export async function downloadDocument(id: string): Promise<Blob> {
  let response: Response;
  try {
    response = await fetch(`${BASE}/documents/${id}/content`, authInit());
  } catch {
    throw new ApiError("Cannot reach DOCURA. Check your connection and try again.", 0);
  }
  if (!response.ok) throw new ApiError(`Could not load the document (${response.status}).`, response.status);
  return response.blob();
}

// ---- record (backend/app/api/record.py) ------------------------------------

export interface SourceRegionResponse {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface SupportingObservationResponse {
  value: string;
  confidence: number | null;
  document_id: string;
  extraction_run_id: string;
  page_number: number;
  region: SourceRegionResponse | null;
}

export interface AttributeValueResponse {
  canonical_identifier: string;
  value: string | null;
  is_ambiguous: boolean;
  observations: SupportingObservationResponse[];
}

export interface AttributeRecordResponse {
  attributes: AttributeValueResponse[];
  count: number;
}

export function getRecord() {
  return authRequest<AttributeRecordResponse>("/record/attributes");
}

export function getAttribute(canonicalIdentifier: string) {
  return authRequest<AttributeValueResponse>(
    `/record/attributes/${encodeURIComponent(canonicalIdentifier)}`,
  );
}

// ---- form sessions (backend/app/api/form_sessions.py) ----------------------

export type FormSessionState = "active" | "handed_back" | "stopped" | "expired";

export type FormActionType =
  | "hand_back"
  | "stop"
  | "fill"
  | "select"
  | "attach"
  | "ask"
  | "answer"
  | "approval_request"
  | "approval_decision"
  | "override";

export type FormActionOutcome = "succeeded" | "failed" | "skipped";

export interface FormSessionResponse {
  id: string;
  state: FormSessionState;
  created_at: string;
  ended_at: string | null;
}

export interface FormSessionListResponse {
  sessions: FormSessionResponse[];
  count: number;
}

export interface FormActionResponse {
  id: string;
  action_type: FormActionType;
  outcome: FormActionOutcome;
  field_ref: string | null;
  document_id: string | null;
  observation_id: string | null;
  reverses_action_id: string | null;
  detail: string | null;
  created_at: string;
}

export interface FormActionListResponse {
  actions: FormActionResponse[];
  count: number;
}

export function listFormSessions() {
  return authRequest<FormSessionListResponse>("/form-sessions");
}

export function getFormSession(id: string) {
  return authRequest<FormSessionResponse>(`/form-sessions/${id}`);
}

export function activateFormSession() {
  return authRequest<FormSessionResponse>("/form-sessions", { method: "POST" });
}

export function handBackFormSession(id: string) {
  return authRequest<FormSessionResponse>(`/form-sessions/${id}/hand-back`, { method: "POST" });
}

export function stopFormSession(id: string) {
  return authRequest<FormSessionResponse>(`/form-sessions/${id}/stop`, { method: "POST" });
}

export function getFormSessionActions(id: string) {
  return authRequest<FormActionListResponse>(`/form-sessions/${id}/actions`);
}

// ---- auth sessions (backend/app/api/auth.py — for Settings > Security) ------

export interface AuthSessionResponse {
  id: string;
  created_at: string;
  last_used_at: string;
  expires_at: string;
  current: boolean;
}

export interface AuthSessionListResponse {
  sessions: AuthSessionResponse[];
}

export function listAuthSessions() {
  return authRequest<AuthSessionListResponse>("/auth/sessions");
}

export function revokeAllAuthSessions() {
  return authRequest<{ revoked: number }>("/auth/sessions/revoke-all", { method: "POST" });
}
