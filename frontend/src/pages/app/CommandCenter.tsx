import * as api from "@/lib/api";
import { useAsync } from "@/hooks/useAsync";
import { ChatWorkspace } from "@/components/command/ChatWorkspace";

// /app — the DOCURA AI chat workspace: the primary post-login surface (§5/§35). The chat is
// driven entirely by the backend conversation/orchestrator API (see ChatWorkspace). This page
// only supplies real document state for the workspace's live status card (never fabricated).
export default function CommandCenterPage() {
  const docs = useAsync(() => api.listDocuments());
  const documents = docs.status === "success" ? (docs.data?.documents ?? []) : null;

  return <ChatWorkspace documents={documents} documentsLoading={docs.status !== "success"} />;
}
