import { ChatWorkspace } from "@/components/command/ChatWorkspace";

// /app — the DOCURA AI chat workspace: the primary post-login surface (§5/§35). The chat is
// driven entirely by the backend conversation/orchestrator API (see ChatWorkspace).
export default function CommandCenterPage() {
  return <ChatWorkspace />;
}
