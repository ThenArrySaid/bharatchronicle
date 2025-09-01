document.addEventListener('DOMContentLoaded', () => {
  const streamEl = document.getElementById('news-stream'); // homepage
  const feedEl   = document.getElementById('news-feed');   // news.html

  if (!streamEl && !feedEl) return;

  fetch(`data/news.json?cb=${Date.now()}`)
    .then(r => r.ok ? r.json() : Promise.reject(r.status))
    .then(items => {
      if (streamEl) renderTop(items);   // 8 on homepage
      if (feedEl)  renderAll(items);    // infinite on news.html
    })
    .catch(console.error);

  function renderTop(items) {
    const top = items.slice(0, 8); // exactly 8
    streamEl.innerHTML = top.map(cardHTML).join('');
  }

  function renderAll(items) {
    const chunk = 12;
    let index = 0;
    const loading = document.getElementById('loading');

    function append() {
      const next = items.slice(index, index + chunk);
      feedEl.insertAdjacentHTML('beforeend', next.map(cardHTML).join(''));
      index += chunk;
      if (index >= items.length && loading) loading.remove();
    }

    append();
    const io = new IntersectionObserver(([e]) => {
      if (e.isIntersecting && index < items.length) append();
    });
    if (loading) io.observe(loading);
  }

  function cardHTML(item) {
    const img = item.image ? `<img src="${item.image}" alt="" loading="lazy">` : '';
    const desc = item.description ? item.description : '';
    return `
      <article class="post">
        <a class="card-link" href="${item.link}" target="_blank" rel="noopener">
          <div class="thumb">${img}</div>
          <h3>${item.title}</h3>
          <p>${desc}</p>
          <span class="read-src" style="margin:0 1rem;">Read full story ↗</span>
        </a>
      </article>
    `;
  }
});
