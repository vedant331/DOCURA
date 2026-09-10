// The one place the backend location lives. It must also appear in
// manifest.json `host_permissions`, or the service worker's fetch is blocked.
// Change both together when pointing at a non-local deployment.
export const API_BASE = "http://127.0.0.1:8000";
