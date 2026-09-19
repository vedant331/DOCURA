// The popup is a thin view over the service worker's controller. It holds no session
// state of its own: it asks the background for the current state, renders it, and
// sends commands. All logic (and the token) live in the worker.

const $ = (id) => document.getElementById(id);

function send(message) {
  return chrome.runtime.sendMessage(message);
}

function render(state) {
  const error = $("error");
  if (state?.error) {
    error.textContent = state.error;
    error.hidden = false;
  } else {
    error.hidden = true;
  }

  const status = state?.status ?? "signed_out";
  const pill = $("state-pill");
  pill.textContent = status === "active" ? "Active" : status === "inactive" ? "Inactive" : "Signed out";
  pill.className = "pill" + (status === "active" ? " active" : status === "inactive" ? " inactive" : "");

  $("signin").hidden = status !== "signed_out";
  $("inactive").hidden = status !== "inactive";
  $("active").hidden = status !== "active";

  if (status === "inactive") $("who-inactive").textContent = state.userEmail ?? "";
  if (status === "active") {
    $("who-active").textContent = state.userEmail ?? "";
    $("session-id").textContent = state.sessionId ?? "";
    renderApprovals(state.pending ?? []);
  }
}

// Sensitive fields awaiting approval (M10 §13). Each row approves exactly one disclosure;
// approval does not carry to any other field/form/session (BR-005/BR-007).
function renderApprovals(pending) {
  const wrap = $("approvals");
  const list = $("approvals-list");
  list.textContent = "";
  if (!pending.length) {
    wrap.hidden = true;
    return;
  }
  wrap.hidden = false;
  for (const item of pending) {
    const li = document.createElement("li");
    const label = document.createElement("span");
    label.textContent = `${item.canonicalIdentifier} → ${item.fieldId}`;
    const btn = document.createElement("button");
    btn.textContent = "Approve once";
    btn.className = "primary";
    btn.addEventListener("click", async () => {
      btn.disabled = true;
      render(await send({ type: "approve", fieldId: item.fieldId }));
    });
    li.append(label, btn);
    list.append(li);
  }
}

async function refresh() {
  render(await send({ type: "getState" }));
}

$("signin").addEventListener("submit", async (event) => {
  event.preventDefault();
  render(await send({ type: "signIn", email: $("email").value, password: $("password").value }));
});
$("activate").addEventListener("click", async () => render(await send({ type: "activate" })));
$("stop").addEventListener("click", async () => render(await send({ type: "stop" })));
$("signout-inactive").addEventListener("click", async () => render(await send({ type: "signOut" })));

refresh();
