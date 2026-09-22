import { ChatWorkspace } from "@/components/command/ChatWorkspace";

// /ask — the DOCURA AI chat workspace (the "Ask" destination). The chat is driven entirely by
// the backend conversation/orchestrator API (see ChatWorkspace). Post-login now lands on the
// Overview page; Ask is reached from the primary nav.
export default function CommandCenterPage() {
  return <ChatWorkspace />;
}
