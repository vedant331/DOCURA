import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { Search as SearchIcon, UploadCloud } from "lucide-react";

import * as api from "@/lib/api";
import { ApiError, type DocumentResponse, type SearchResponse } from "@/lib/api";
import { useAsync } from "@/hooks/useAsync";
import { PageHeader } from "@/components/app/PageHeader";
import { Button } from "@/components/ui/button";
import { DocumentTable } from "@/components/documents/DocumentTable";
import { UploadDialog } from "@/components/documents/UploadDialog";
import { ConfirmationDialog } from "@/components/system/ConfirmationDialog";
import { EmptyState, ErrorState, LoadingState } from "@/components/system/states";

type Sort = "recent" | "name" | "status";

// /app/documents — the vault (§7). List, upload, sort, reprocess, delete (with confirm).
export default function DocumentsPage() {
  const docs = useAsync(() => api.listDocuments());
  const limits = useAsync(() => api.getUploadLimits());
  const [uploadOpen, setUploadOpen] = useState(false);
  const [sort, setSort] = useState<Sort>("recent");
  const [toDelete, setToDelete] = useState<DocumentResponse | null>(null);

  // Search (FR-SRCH) — owner-scoped, server-side. When results !== null the results view
  // replaces the vault list; clearing returns to the full vault.
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResponse | null>(null);
  const [searchStatus, setSearchStatus] = useState<"idle" | "loading" | "error">("idle");
  const [searchError, setSearchError] = useState<string | null>(null);

  const doSearch = async (raw: string) => {
    const q = raw.trim();
    if (!q) {
      setResults(null);
      setSearchStatus("idle");
      return;
    }
    setSearchStatus("loading");
    setSearchError(null);
    try {
      setResults(await api.search(q));
      setSearchStatus("idle");
    } catch (err) {
      setSearchError(err instanceof ApiError ? err.message : "Search failed. Try again.");
      setSearchStatus("error");
    }
  };
  const clearSearch = () => {
    setQuery("");
    setResults(null);
    setSearchStatus("idle");
    setSearchError(null);
  };

  const documents = docs.data?.documents ?? [];
  const sorted = useMemo(() => {
    const copy = [...documents];
    if (sort === "name") copy.sort((a, b) => a.original_filename.localeCompare(b.original_filename));
    else if (sort === "status") copy.sort((a, b) => a.status.localeCompare(b.status));
    else copy.sort((a, b) => b.created_at.localeCompare(a.created_at));
    return copy;
  }, [documents, sort]);

  const reprocess = async (d: DocumentResponse) => {
    await api.reprocessDocument(d.id);
    docs.reload();
  };

  return (
    <>
      <PageHeader
        eyebrow="Vault"
        title="Documents"
        description="Every document you have stored, with its type, status, and original."
        actions={
          <Button variant="primary" onClick={() => setUploadOpen(true)}>
            <UploadCloud className="size-4" aria-hidden /> Upload
          </Button>
        }
      />

      <form
        onSubmit={(e) => {
          e.preventDefault();
          void doSearch(query);
        }}
        className="mb-4 flex items-center gap-2"
        role="search"
      >
        <div className="relative flex-1">
          <SearchIcon
            className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground"
            aria-hidden
          />
          <input
            type="search"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search documents and your record"
            aria-label="Search documents and your record"
            className="w-full border border-border bg-surface px-3 py-2 pl-9 text-sm text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          />
        </div>
        <Button type="submit" variant="outline" loading={searchStatus === "loading"} loadingLabel="Searching">
          Search
        </Button>
        {results !== null || searchStatus === "error" ? (
          <Button type="button" variant="ghost" onClick={clearSearch}>
            Clear
          </Button>
        ) : null}
      </form>

      {results !== null || searchStatus === "error" ? (
        searchStatus === "error" ? (
          <ErrorState message={searchError ?? undefined} onRetry={() => void doSearch(query)} />
        ) : results && results.document_count === 0 && results.attribute_count === 0 ? (
          <EmptyState
            title={`No matches for “${results.query}”`}
            description="Try a different document name or a value from your record."
          />
        ) : results ? (
          <div className="space-y-6">
            <section className="space-y-2">
              <h2 className="font-mono text-[11px] uppercase tracking-[0.15em] text-muted-foreground">
                Documents ({results.document_count})
              </h2>
              {results.documents.length === 0 ? (
                <p className="text-sm text-muted-foreground">No matching documents.</p>
              ) : (
                <ul className="divide-y divide-border border border-border">
                  {results.documents.map((d) => (
                    <li key={d.id}>
                      <Link
                        to={`/app/documents/${d.id}`}
                        className="flex items-center justify-between gap-3 px-3 py-2 text-sm hover:bg-surface"
                      >
                        <span className="truncate text-foreground">{d.original_filename}</span>
                        <span className="font-mono text-[11px] uppercase text-muted-foreground">{d.status}</span>
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </section>
            <section className="space-y-2">
              <h2 className="font-mono text-[11px] uppercase tracking-[0.15em] text-muted-foreground">
                Record attributes ({results.attribute_count})
              </h2>
              {results.attributes.length === 0 ? (
                <p className="text-sm text-muted-foreground">No matching record attributes.</p>
              ) : (
                <ul className="divide-y divide-border border border-border">
                  {results.attributes.map((a) => (
                    <li key={a.canonical_identifier}>
                      <Link
                        to="/app/record"
                        className="flex items-center justify-between gap-3 px-3 py-2 text-sm hover:bg-surface"
                      >
                        <span className="truncate text-foreground">
                          {a.canonical_identifier}
                          {a.value ? `: ${a.value}` : ""}
                        </span>
                        <span className="font-mono text-[11px] uppercase text-muted-foreground">
                          {a.is_ambiguous
                            ? "needs review"
                            : a.page_number != null
                              ? `p.${a.page_number}`
                              : ""}
                        </span>
                      </Link>
                    </li>
                  ))}
                </ul>
              )}
            </section>
          </div>
        ) : null
      ) : docs.status === "loading" ? (
        <LoadingState label="Loading documents" />
      ) : docs.status === "error" ? (
        <ErrorState message={docs.error ?? undefined} onRetry={docs.reload} />
      ) : documents.length === 0 ? (
        <EmptyState
          title="No documents yet"
          description="Upload a PDF, JPG, or PNG to get started."
          action={
            <Button variant="primary" onClick={() => setUploadOpen(true)}>
              <UploadCloud className="size-4" aria-hidden /> Upload documents
            </Button>
          }
        />
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <p className="font-mono text-[11px] uppercase tracking-[0.15em] text-muted-foreground">
              {documents.length} document{documents.length === 1 ? "" : "s"}
            </p>
            <label className="flex items-center gap-2 font-mono text-[11px] uppercase tracking-[0.15em] text-muted-foreground">
              Sort
              <select
                value={sort}
                onChange={(e) => setSort(e.target.value as Sort)}
                className="border border-border bg-surface px-2 py-1 text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
              >
                <option value="recent">Most recent</option>
                <option value="name">Name</option>
                <option value="status">Status</option>
              </select>
            </label>
          </div>
          <DocumentTable documents={sorted} onReprocess={reprocess} onDelete={setToDelete} />
        </div>
      )}

      <UploadDialog open={uploadOpen} onOpenChange={setUploadOpen} limits={limits.data} onUploaded={docs.reload} />

      <ConfirmationDialog
        open={toDelete !== null}
        onOpenChange={(o) => (o ? null : setToDelete(null))}
        title="Delete this document?"
        description={
          toDelete
            ? `"${toDelete.original_filename}" and any information extracted from it will be removed. This cannot be undone here.`
            : ""
        }
        confirmLabel="Delete"
        destructive
        onConfirm={async () => {
          if (!toDelete) return;
          await api.deleteDocument(toDelete.id);
          setToDelete(null);
          docs.reload();
        }}
      />
    </>
  );
}
