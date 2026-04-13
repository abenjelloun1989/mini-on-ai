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
  // Google Docs renders text in .kix-lineview elements
  const lines = document.querySelectorAll(".kix-lineview");
  if (lines.length > 0) {
    return Array.from(lines)
      .map((el) => el.textContent)
      .join("\n")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
  }

  // Fallback: try the canvas-based editor text
  const paragraphs = document.querySelectorAll(".kix-paragraphrenderer");
  if (paragraphs.length > 0) {
    return Array.from(paragraphs)
      .map((el) => el.textContent)
      .join("\n")
      .trim();
  }

  throw new Error("Could not find document text. Google Docs may have updated its layout.");
}
