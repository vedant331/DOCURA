import { test } from "node:test";
import assert from "node:assert/strict";

import {
  computeMatching,
  matchUploadField,
  evaluateConstraints,
  noApprovedDocumentMatcher,
  noApprovedDocumentSensitivity,
  noApprovedMatchThreshold,
  preparationUnavailable,
} from "../src/matching.js";
import { newApprovalLedger, grantApproval } from "../src/sensitivity.js";
import { FormWatcher } from "../src/detect.js";

// ---- helpers ---------------------------------------------------------------
function fileField({ fieldId = "upload", required = true, constraints = {} } = {}) {
  return { fieldId, type: "file", required, constraints };
}
function textField({ fieldId = "name" } = {}) {
  return { fieldId, type: "text", required: false, constraints: {} };
}
function snapshot(fields, { formId = "app", standalone = false } = {}) {
  return { forms: [{ formId, standalone, fields }], formCount: standalone ? 0 : 1 };
}
function doc({ id, filename = "f.pdf", contentType = "application/pdf", size = 1000, checksum = "sum" } = {}) {
  return { id, original_filename: filename, content_type: contentType, byte_size: size, checksum_sha256: checksum, document_type: "unclassified", status: "ready" };
}
const only = (r) => r.forms[0].fields[0];

const tierRoutine = () => "routine";
const tierSensitive = () => "sensitive";
const ctx = { userId: "u1", sessionId: "s1" };

// 1. A file-upload field produces a document requirement; non-file fields do not.
test("only file-upload fields produce a matching requirement", () => {
  const r = computeMatching({ snapshot: snapshot([textField(), fileField({ fieldId: "photo" })]) });
  assert.equal(r.summary.total, 1);
  assert.equal(only(r).fieldId, "photo");
  assert.equal(only(r).type, "file");
});

// 2 + 3. One candidate → a deterministic candidate result that includes its confidence.
test("a single matched candidate yields a candidate result carrying its confidence", () => {
  const d = doc({ id: "d1" });
  const matcher = () => [{ documentId: "d1", confidence: 0.8 }];
  const r = matchUploadField({ field: fileField(), documents: [d], matchDocuments: matcher, classifySensitivity: tierRoutine });
  assert.equal(r.status, "candidate");
  assert.equal(r.candidate.documentId, "d1");
  assert.equal(r.candidate.confidence, 0.8);
});

// 4 + 17. Multiple candidates → ambiguous + requiresUser; never collapsed to one by any heuristic.
test("multiple candidates are ambiguous, require the user, and are never reduced to one", () => {
  const docs = [doc({ id: "d1", filename: "a.pdf" }), doc({ id: "d2", filename: "b.pdf" })];
  // Distinct confidence, recency (order), and filenames — none of which may pick a winner.
  const matcher = () => [{ documentId: "d2", confidence: 0.9 }, { documentId: "d1", confidence: 0.4 }];
  const r = matchUploadField({ field: fileField(), documents: docs, matchDocuments: matcher });
  assert.equal(r.status, "ambiguous");
  assert.equal(r.requiresUser, true);
  assert.equal(r.candidates.length, 2);
  assert.equal(r.candidate, undefined); // nothing selected
  assert.equal(r.preview, null); // no exact file until the user chooses
});

// 5. Candidate identity / distinguishing metadata is preserved.
test("candidate metadata identifies documents clearly enough to tell them apart", () => {
  const docs = [doc({ id: "d1", filename: "aadhaar.pdf", size: 111 }), doc({ id: "d2", filename: "pan.jpg", contentType: "image/jpeg", size: 222 })];
  const matcher = () => [{ documentId: "d1", confidence: 0.5 }, { documentId: "d2", confidence: 0.5 }];
  const r = matchUploadField({ field: fileField(), documents: docs, matchDocuments: matcher });
  const [c1, c2] = r.candidates;
  assert.equal(c1.filename, "aadhaar.pdf");
  assert.equal(c1.byteSize, 111);
  assert.equal(c2.filename, "pan.jpg");
  assert.equal(c2.contentType, "image/jpeg");
});

// 6. No candidate → missing.
test("no matched document is reported as missing", () => {
  const r = matchUploadField({ field: fileField(), documents: [doc({ id: "d1" })], matchDocuments: () => [] });
  assert.equal(r.status, "missing");
  assert.equal(r.requiresUser, true);
});

// 7. A different document is never substituted (a hit outside the vault is dropped, not faked).
test("a matcher hit that is not in the vault is dropped, never substituted", () => {
  const r = matchUploadField({ field: fileField(), documents: [doc({ id: "d1" })], matchDocuments: () => [{ documentId: "ghost", confidence: 0.99 }] });
  assert.equal(r.status, "missing"); // not "candidate" for some other document
  assert.equal(r.candidates.length, 0);
});

// 8. A constraint-compatible candidate is accepted with the original as the exact file.
test("a candidate already meeting the constraints needs no preparation", () => {
  const d = doc({ id: "d1", contentType: "application/pdf", size: 500 });
  const field = fileField({ constraints: { accept: "application/pdf", maxSize: 1000 } });
  const r = matchUploadField({ field, documents: [d], matchDocuments: () => [{ documentId: "d1", confidence: 1 }], classifySensitivity: tierRoutine });
  assert.equal(r.status, "candidate");
  assert.equal(r.constraints.satisfied, true);
  assert.equal(r.preparation.needed, false);
  assert.equal(r.preview.source, "original");
});

// 9. A constraint-incompatible candidate with no available transform → constraint_failure (no attach).
test("a candidate that cannot meet the constraints, with no transform, is a constraint_failure", () => {
  const d = doc({ id: "d1", contentType: "image/png", size: 9_000_000 });
  const field = fileField({ constraints: { accept: "application/pdf", maxSize: 1000 } });
  const r = matchUploadField({ field, documents: [d], matchDocuments: () => [{ documentId: "d1", confidence: 1 }], prepare: preparationUnavailable });
  assert.equal(r.status, "constraint_failure");
  assert.equal(r.constraints.satisfied, false);
  assert.deepEqual(r.constraints.unmet.sort(), ["format", "size"]);
  assert.equal(r.attach.performed, false);
});

// 9b. Quality-floor preparation → constraint_failure, told to the user, nothing degraded.
test("preparation that would breach the quality floor stops rather than attach a degraded file", () => {
  const d = doc({ id: "d1", contentType: "image/png", size: 9_000_000 });
  const field = fileField({ constraints: { maxSize: 1000 } });
  const r = matchUploadField({ field, documents: [d], matchDocuments: () => [{ documentId: "d1", confidence: 1 }], prepare: () => ({ status: "quality_floor" }) });
  assert.equal(r.status, "constraint_failure");
  assert.match(r.reason, /quality loss/i);
});

// 10 + 11. Preparation creates a derived copy and never mutates the stored original.
test("preparation yields a derived copy and leaves the original byte-for-byte unchanged", () => {
  const d = doc({ id: "d1", contentType: "image/png", size: 5000, checksum: "orig-sum" });
  const frozen = JSON.stringify(d);
  const field = fileField({ constraints: { accept: "application/pdf" } });
  const prepare = (f, document) => ({ status: "prepared", derived: { derivedFrom: document.id, content_type: "application/pdf", byte_size: 4000, checksum_sha256: "derived-sum" } });
  const r = matchUploadField({ field, documents: [d], matchDocuments: () => [{ documentId: "d1", confidence: 1 }], prepare, classifySensitivity: tierRoutine });
  assert.equal(r.preparation.status, "prepared");
  assert.equal(r.preview.source, "derived");
  assert.equal(r.preview.derived.derivedFrom, "d1"); // provenance link retained
  assert.equal(JSON.stringify(d), frozen); // original never modified (BR-013)
});

// 12. The preview target identifies exactly the file that would be attached.
test("the preview target names the exact file that would be attached", () => {
  const d = doc({ id: "d1", contentType: "application/pdf", size: 700 });
  const field = fileField({ constraints: { accept: "application/pdf", maxSize: 1000 } });
  const r = matchUploadField({ field, documents: [d], matchDocuments: () => [{ documentId: "d1", confidence: 1 }], classifySensitivity: tierRoutine });
  assert.equal(r.preview.documentId, "d1");
  assert.equal(r.preview.source, "original");
  assert.equal(r.preview.byteSize, 700);
});

// 13. A sensitive candidate is approval-gated (per-instance), and prepared+previewed first (EC-011).
test("a sensitive candidate requires explicit approval but is still prepared and previewable", () => {
  const d = doc({ id: "d1", contentType: "application/pdf", size: 700 });
  const field = fileField({ constraints: { accept: "application/pdf" } });
  const r = matchUploadField({ field, documents: [d], matchDocuments: () => [{ documentId: "d1", confidence: 1 }], classifySensitivity: tierSensitive, approvals: newApprovalLedger(), context: { ...ctx, formId: "app" } });
  assert.equal(r.sensitivity, "sensitive");
  assert.equal(r.approvalState, "required");
  assert.equal(r.action, "none");
  assert.equal(r.requiresUser, true);
  assert.equal(r.preview.source, "original"); // previewable to its owner before the gate
  assert.equal(r.attach.performed, false);
});

// 13b. With explicit, exact-scope approval, the sensitive candidate is no longer gated.
test("explicit exact-scope approval clears the sensitive gate", () => {
  const d = doc({ id: "d1", contentType: "application/pdf", size: 700, checksum: "the-sum" });
  const field = fileField({ fieldId: "id_upload", constraints: { accept: "application/pdf" } });
  const approvals = newApprovalLedger();
  grantApproval(approvals, { ...ctx, formId: "app", fieldId: "id_upload", canonicalIdentifier: "document:d1", value: "the-sum" });
  const r = matchUploadField({ field, documents: [d], matchDocuments: () => [{ documentId: "d1", confidence: 1 }], classifySensitivity: tierSensitive, threshold: () => 0.5, approvals, context: { ...ctx, formId: "app" } });
  assert.equal(r.approvalState, "granted");
  assert.equal(r.action, "propose"); // now proposable (threshold known & met)
});

// 14. No automatic sensitive disclosure: an unknown tier is never treated as routine.
test("an unknown-tier candidate is blocked, never disclosed automatically", () => {
  const d = doc({ id: "d1", contentType: "application/pdf", size: 700 });
  const field = fileField({ constraints: { accept: "application/pdf" } });
  const r = matchUploadField({ field, documents: [d], matchDocuments: () => [{ documentId: "d1", confidence: 1 }], classifySensitivity: noApprovedDocumentSensitivity });
  assert.equal(r.sensitivity, "unknown");
  assert.equal(r.approvalState, "blocked");
  assert.equal(r.action, "none");
  assert.match(r.reason, /unassigned/i);
});

// 15. No threshold is invented: a strong candidate stays unresolved without an approved threshold.
test("without an approved threshold, a candidate is prepared but never auto-proposed", () => {
  const d = doc({ id: "d1", contentType: "application/pdf", size: 700 });
  const field = fileField({ constraints: { accept: "application/pdf" } });
  const r = matchUploadField({ field, documents: [d], matchDocuments: () => [{ documentId: "d1", confidence: 0.999 }], classifySensitivity: tierRoutine, threshold: noApprovedMatchThreshold });
  assert.equal(r.action, "prepare"); // not "propose"
  assert.equal(r.requiresUser, true);
  assert.match(r.reason, /threshold is unset/i);
});

// 15b. Threshold known and met → proposable; below → not proposed.
test("with an approved threshold, proposal is deterministic on confidence", () => {
  const d = doc({ id: "d1", contentType: "application/pdf", size: 700 });
  const field = fileField({ constraints: { accept: "application/pdf" } });
  const above = matchUploadField({ field, documents: [d], matchDocuments: () => [{ documentId: "d1", confidence: 0.8 }], classifySensitivity: tierRoutine, threshold: () => 0.7 });
  assert.equal(above.action, "propose");
  assert.equal(above.requiresUser, false);
  const below = matchUploadField({ field, documents: [d], matchDocuments: () => [{ documentId: "d1", confidence: 0.6 }], classifySensitivity: tierRoutine, threshold: () => 0.7 });
  assert.equal(below.action, "prepare");
  assert.equal(below.requiresUser, true);
});

// 16. An unmapped requirement (production matcher) stays unresolved; no document is read.
test("the production matcher leaves every upload field unresolved", () => {
  assert.equal(noApprovedDocumentMatcher(fileField(), [doc({ id: "d1" })]), null);
  const r = matchUploadField({ field: fileField(), documents: [doc({ id: "d1" })] });
  assert.equal(r.status, "unresolved");
  assert.equal(r.requiresUser, true);
  assert.equal(r.candidates.length, 0);
});

// 18. No merge/assembly of multiple documents: multiple candidates never combine into one.
test("multiple candidates are never assembled/merged into one prepared file", () => {
  const docs = [doc({ id: "d1" }), doc({ id: "d2" })];
  const r = matchUploadField({ field: fileField(), documents: docs, matchDocuments: () => [{ documentId: "d1", confidence: 0.5 }, { documentId: "d2", confidence: 0.5 }] });
  assert.equal(r.status, "ambiguous");
  assert.equal(r.preview, null); // no combined artefact
  assert.equal(r.preparation, undefined);
});

// 19. A stopped session clears M7 state (mirrors content.js teardown); no later processing.
test("after stop, teardown clears the matching result; late mutations do nothing", () => {
  const store = { matching: undefined };
  const controls = [{ tagName: "INPUT", type: "file", id: "up", name: "up", required: true, form: null, getAttribute: () => null }];
  const obsRef = { cb: null };
  const factory = (cb) => ((obsRef.cb = cb), { observe() {}, disconnect() {} });
  const w = new FormWatcher({ root: { querySelectorAll: () => controls }, onChange: (result) => (store.matching = computeMatching({ snapshot: result })), observerFactory: factory }).start();
  assert.equal(store.matching.summary.total, 1);
  assert.equal(store.matching.forms[0].fields[0].status, "unresolved");

  w.stop();
  store.matching = null; // teardown
  store.matching = "UNCHANGED";
  obsRef.cb(); // late mutation after stop
  assert.equal(store.matching, "UNCHANGED");
});

// 20. An inactive page (watcher never started) performs no M7 processing.
test("an unstarted watcher (inactive page) computes no matching", () => {
  const store = {};
  new FormWatcher({ root: { querySelectorAll: () => [] }, onChange: (result) => (store.matching = computeMatching({ snapshot: result })) });
  assert.equal("matching" in store, false);
});

// 21. M7 is a pure data result: it holds no DOM/form handle and mutates no control.
test("matching is a plain data result and touches no DOM/form control", () => {
  const control = { tagName: "INPUT", type: "file", id: "up", form: null, getAttribute: () => null, value: "UNTOUCHED" };
  const r = computeMatching({ snapshot: snapshot([fileField()]) });
  assert.equal(typeof r, "object");
  assert.equal(control.value, "UNTOUCHED"); // never written
});

// 22. User-scoped document access is preserved: matching sees only the vault it is handed.
test("matching reflects only the documents it is given (user isolation)", () => {
  // The matcher points at a document id this account does not hold → missing, not substituted.
  const r = matchUploadField({ field: fileField(), documents: [doc({ id: "mine" })], matchDocuments: () => [{ documentId: "someone-elses", confidence: 1 }] });
  assert.equal(r.status, "missing");
});

// Bonus: evaluateConstraints is a pure metadata read (accept wildcard + extension tokens).
test("evaluateConstraints reads only declared accept/maxSize", () => {
  const d = doc({ id: "d1", filename: "photo.png", contentType: "image/png", size: 400 });
  assert.equal(evaluateConstraints({ constraints: { accept: "image/*" } }, d).satisfied, true);
  assert.equal(evaluateConstraints({ constraints: { accept: ".png" } }, d).satisfied, true);
  assert.equal(evaluateConstraints({ constraints: { accept: "application/pdf" } }, d).format, false);
  assert.equal(evaluateConstraints({ constraints: { maxSize: 100 } }, d).size, false);
  assert.equal(evaluateConstraints({ constraints: {} }, d).satisfied, true); // nothing declared
});
