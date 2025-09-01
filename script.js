document.addEventListener('DOMContentLoaded', () => {
  const streamEl = document.getElementById('news-stream'); // homepage
  const feedEl   = document.getElementById('news-feed');   // news.html
  if (!streamEl && !feedEl) return;

  const url = `data/news.json?cb=${Date.now()}`; // cache-bust
  fetch(url)
    .then(r => r.ok ? r.json() : Promise.reject(r.status))
    .then(items => {
      if (feedEl) renderAll(items);     // full inshorts-like feed
      if (streamEl) renderTop(items);   // small set on homepage
    })
    .catch(() => {
      // Fallback: do nothing or use your inline sample if you want
    });

  function renderTop(items) {
    const top = items.slice(0, 8);
    streamEl.innerHTML = top.map(cardHTML).join('');
  }

  function renderAll(items) {
    const container = feedEl;
    let index = 0, chunk = 12;
    function append() {
      const next = items.slice(index, index + chunk);
      container.insertAdjacentHTML('beforeend', next.map(cardHTML).join(''));
      index += chunk;
      if (index >= items.length) observer.disconnect();
    }
    const sentinel = document.getElementById('loading');
    const observer = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting) append();
    });
    observer.observe(sentinel);
    append();
  }

  function cardHTML(item) {
    const img = item.image ? `<img src="${item.image}" alt="" loading="lazy">` : '';
    const desc = item.description || '';
    return `
      <article class="post">
        <a class="card-link" href="${item.link}" target="_blank" rel="noopener">
          <div class="thumb">${img}</div>
          <h3>${item.title}</h3>
          <p>${desc}</p>
          <span class="read-src">Read full story ↗</span>
        </a>
      </article>`;
  }
});
