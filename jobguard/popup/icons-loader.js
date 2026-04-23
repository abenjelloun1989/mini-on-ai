// Load the SVG icon sprite into the document body.
// Extracted from popup.html to comply with MV3 CSP (script-src 'self' blocks inline scripts).
fetch(chrome && chrome.runtime ? chrome.runtime.getURL('popup/icons.svg') : 'icons.svg')
  .then(r => r.text())
  .then(svg => { document.body.insertAdjacentHTML('afterbegin', svg); })
  .catch(() => {});
