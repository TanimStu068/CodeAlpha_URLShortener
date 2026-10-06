const form = document.getElementById("form");
const input = document.getElementById("url");
const errorEl = document.getElementById("error");
const result = document.getElementById("result");
const shortEl = document.getElementById("short");
const copyBtn = document.getElementById("copy");
const recent = document.getElementById("recent");

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errorEl.hidden = true;
  try {
    const res = await fetch("/api/shorten", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: input.value }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Something went wrong.");
    shortEl.textContent = data.short_url;
    shortEl.href = data.short_url;
    result.hidden = false;
    copyBtn.textContent = "Copy link";
    loadRecent();
  } catch (err) {
    result.hidden = true;
    errorEl.textContent = err.message;
    errorEl.hidden = false;
  }
});

copyBtn.addEventListener("click", async () => {
  try {
    await navigator.clipboard.writeText(shortEl.textContent);
    copyBtn.textContent = "Copied";
  } catch {
    copyBtn.textContent = "Press Ctrl+C to copy";
  }
});

async function loadRecent() {
  const res = await fetch("/api/urls");
  const items = await res.json();
  if (!items.length) return;
  recent.innerHTML = "";
  for (const it of items) {
    const li = document.createElement("li");
    const a = document.createElement("a");
    a.href = it.short_url; a.textContent = it.short_url; a.target = "_blank"; a.rel = "noopener";
    const orig = document.createElement("span");
    orig.className = "orig"; orig.textContent = it.original_url; orig.title = it.original_url;
    const clicks = document.createElement("span");
    clicks.className = "muted"; clicks.textContent = it.clicks + (it.clicks === 1 ? " click" : " clicks");
    li.append(a, orig, clicks);
    recent.append(li);
  }
}
loadRecent();
