// Content script for Google Docs text extraction
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === "extractText") {
    try {
      const text = extractGoogleDocText();
      sendResponse({ text, wordCount: text.split(/\s+/).filter(Boolean).length });
    } catch (e) {
      sendResponse({ error: "Extraction failed: " + e.message });
    }
    return true;
  }
});

function extractGoogleDocText() {
  let text = "";

  // Strategy 1: .kix-lineview (classic renderer)
  const lines = document.querySelectorAll(".kix-lineview");
  if (lines.length > 0) {
    text = Array.from(lines).map((el) => el.textContent).join("\n");
    if (text.trim().length > 50) return clean(text);
  }

  // Strategy 2: .kix-paragraphrenderer
  const paras = document.querySelectorAll(".kix-paragraphrenderer");
  if (paras.length > 0) {
    text = Array.from(paras).map((el) => el.textContent).join("\n");
    if (text.trim().length > 50) return clean(text);
  }

  // Strategy 3: role="textbox" (newer Google Docs accessibility tree)
  const textbox = document.querySelector('[role="textbox"]');
  if (textbox) {
    text = textbox.innerText || textbox.textContent || "";
    if (text.trim().length > 50) return clean(text);
  }

  // Strategy 4: .kix-page-content-wrapper
  const pages = document.querySelectorAll(".kix-page-content-wrapper");
  if (pages.length > 0) {
    text = Array.from(pages).map((el) => el.innerText || el.textContent).join("\n");
    if (text.trim().length > 50) return clean(text);
  }

  // Strategy 5: .docs-editor (outer editor container)
  const editor = document.querySelector(".docs-editor");
  if (editor) {
    text = editor.innerText || editor.textContent || "";
    if (text.trim().length > 50) return clean(text);
  }

  // Strategy 6: any element with class starting with "kix-" that has substantial text
  const kixEls = document.querySelectorAll('[class*="kix-page"]');
  if (kixEls.length > 0) {
    text = Array.from(kixEls).map((el) => el.innerText || el.textContent).join("\n");
    if (text.trim().length > 50) return clean(text);
  }

  // Strategy 7: last resort — grab the largest text block on the page
  const allDivs = Array.from(document.querySelectorAll("div"));
  const biggest = allDivs
    .map((el) => ({ el, len: (el.innerText || "").length }))
    .filter((x) => x.len > 200)
    .sort((a, b) => b.len - a.len)[0];
  if (biggest) {
    text = biggest.el.innerText || "";
    if (text.trim().length > 50) return clean(text);
  }

  throw new Error("Could not extract text from this Google Doc. Try pasting the text manually into the extension.");
}

function clean(text) {
  return text.replace(/\n{3,}/g, "\n\n").trim().slice(0, 15000);
}
