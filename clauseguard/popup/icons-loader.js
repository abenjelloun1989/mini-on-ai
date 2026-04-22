fetch(chrome && chrome.runtime ? chrome.runtime.getURL('popup/icons.svg') : 'icons.svg')
  .then(r => r.text())
  .then(svg => { document.body.insertAdjacentHTML('afterbegin', svg); })
  .catch(() => {});
