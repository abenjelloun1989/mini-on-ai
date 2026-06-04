/**
 * chat.js — AI financial assistant UI (aggregates-only privacy).
 */
import { api } from "../api.js";
import { store } from "../store.js";
import { renderMarkdown, escHtml, toast } from "../ui.js";

const SUGGESTIONS = [
  "Puis-je me permettre cet achat ?",
  "Où ai-je le plus dérapé ce mois ?",
  "Comment évolue ma trésorerie ?",
  "Quel est mon budget restant ?",
];

let messages = [];
let loading = false;

export async function renderChat(view) {
  view.innerHTML = `
    <div class="chat-view">
      <div class="chat-head">
        <h2>Assistant financier <button class="link-btn" id="clearChat" style="float:right;font-size:13px">Effacer</button></h2>
        <div class="sub">Accède uniquement à vos totaux — pas vos transactions individuelles</div>
      </div>
      <div id="privacyBanner"></div>
      <div class="chat-msgs" id="msgs"></div>
      <div class="chips" id="chips"></div>
      <div class="chat-input-row">
        <textarea id="chatInput" rows="1" placeholder="Pose ta question…"></textarea>
        <button class="chat-send" id="chatSend" aria-label="Envoyer">↑</button>
      </div>
    </div>
  `;

  // Privacy notice (once)
  if (!store.isPrivacyDismissed()) {
    view.querySelector("#privacyBanner").innerHTML = `
      <div class="privacy-banner">
        <span>Cet assistant ne reçoit que vos totaux par catégorie, jamais vos transactions individuelles.</span>
        <button id="dismissPrivacy">OK</button>
      </div>`;
    view.querySelector("#dismissPrivacy").onclick = () => { store.dismissPrivacy(); view.querySelector("#privacyBanner").innerHTML = ""; };
  }

  const msgsEl = view.querySelector("#msgs");
  const input = view.querySelector("#chatInput");
  const sendBtn = view.querySelector("#chatSend");

  try { messages = await api.chat.history(); } catch { messages = []; }
  paint();

  function paint() {
    msgsEl.innerHTML = messages.map(bubble).join("") + (loading ? typingBubble() : "");
    msgsEl.scrollTop = msgsEl.scrollHeight;
    // suggestion chips only when empty
    const chips = view.querySelector("#chips");
    chips.innerHTML = (!messages.length && !loading)
      ? SUGGESTIONS.map((s) => `<button class="chip">${escHtml(s)}</button>`).join("")
      : "";
    chips.querySelectorAll(".chip").forEach((c) => c.onclick = () => { input.value = c.textContent; send(); });
  }

  function bubble(m) {
    const content = m.role === "assistant" ? renderMarkdown(m.content) : escHtml(m.content);
    return `<div class="bubble ${m.role === "user" ? "user" : "assistant"}">${content}</div>`;
  }
  function typingBubble() {
    return `<div class="bubble assistant"><span class="typing"><span></span><span></span><span></span></span></div>`;
  }

  async function send() {
    const text = input.value.trim();
    if (!text || loading) return;
    input.value = ""; autoGrow();
    messages.push({ role: "user", content: text });
    loading = true; sendBtn.disabled = true; paint();
    try {
      const { reply } = await api.chat.send(text);
      messages.push({ role: "assistant", content: reply });
    } catch (e) {
      loading = false; sendBtn.disabled = false;
      paint();
      showError(text, e.message);
      return;
    }
    loading = false; sendBtn.disabled = false; paint();
  }

  function showError(failedText, msg) {
    const err = document.createElement("div");
    err.className = "chat-error";
    err.innerHTML = `${escHtml(msg || "Erreur")} <button>Réessayer</button>`;
    err.querySelector("button").onclick = () => { err.remove(); input.value = failedText; send(); };
    msgsEl.appendChild(err);
    msgsEl.scrollTop = msgsEl.scrollHeight;
  }

  function autoGrow() {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 110) + "px";
  }
  input.addEventListener("input", autoGrow);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); }
  });
  sendBtn.onclick = send;

  view.querySelector("#clearChat").onclick = async () => {
    if (!confirm("Effacer toute la conversation ?")) return;
    try { await api.chat.clear(); messages = []; paint(); toast("Conversation effacée", { type: "ok" }); }
    catch { toast("Échec", { type: "err" }); }
  };
}
