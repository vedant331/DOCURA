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
