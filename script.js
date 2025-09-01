/*
 * Bharat Chronicle custom JavaScript
 *
 * Adds small enhancements like updating the current year and
 * gracefully handling the newsletter form submission.
 */

// Set current year in footer
document.addEventListener('DOMContentLoaded', () => {
  // Update the footer year dynamically
  const yearEl = document.getElementById('year');
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

  // Newsletter form handler
  const form = document.getElementById('newsletter-form');
  if (form) {
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      const emailInput = form.querySelector('input[type="email"]');
      // In a production site you would send the email to your mailing list service here.
      // For this prototype we simply thank the subscriber.
      alert(`Thank you for subscribing, ${emailInput.value}!`);
      emailInput.value = '';
    });
  }

  // Dynamic news feed loader
  const streamEl = document.getElementById('news-stream');
  if (!streamEl) return;
  let allNews = [];
  let newsIndex = 0;
  const batchSize = 4;

  // Show/hide loading indicator helper
  const loadingIndicator = document.getElementById('loading-indicator');
  const showLoading = () => { if (loadingIndicator) loadingIndicator.hidden = false; };
  const hideLoading = () => { if (loadingIndicator) loadingIndicator.hidden = true; };

  // Fetch news from the local JSON file.  If this fails (for example when
  // browsing the site via the file:// protocol, which blocks fetch for local
  // files), fall back to the inline JSON stored in the #news-data script tag.
  fetch('data/news.json')
    .then(resp => {
      if (!resp.ok) throw new Error('HTTP error');
      return resp.json();
    })
    .then(data => {
      allNews = Array.isArray(data) ? data : [];
      if (allNews.length === 0) {
        throw new Error('No news items found');
      }
      loadMoreNews();
    })
    .catch(err => {
      console.warn('Unable to fetch data/news.json; falling back to inline news.', err);
      try {
        const inlineEl = document.getElementById('news-data');
        if (inlineEl) {
          const inlineJson = inlineEl.textContent.trim();
          allNews = JSON.parse(inlineJson);
          loadMoreNews();
        }
      } catch (e) {
        console.error('Failed to parse inline news data:', e);
      }
    });

  function createNewsCard(item, index) {
    const article = document.createElement('article');
    article.classList.add('post');
    const imgDiv = document.createElement('div');
    imgDiv.classList.add('post-img');
    // Determine the image URL. Prefer the item image; otherwise cycle through local assets.
    let imgUrl = item.image;
    if (!imgUrl) {
      const fallback = (index % 4) + 1;
      imgUrl = `images/post${fallback}.png`;
    }
    imgDiv.style.backgroundImage = `url('${imgUrl}')`;
    // Title and link
    const h3 = document.createElement('h3');
    const link = document.createElement('a');
    link.href = item.link || '#';
    link.target = '_blank';
    link.rel = 'noopener';
    link.textContent = item.title || 'Untitled';
    h3.appendChild(link);
    // Description
    const p = document.createElement('p');
    p.textContent = item.description || '';
    article.appendChild(imgDiv);
    article.appendChild(h3);
    article.appendChild(p);
    return article;
  }

  function loadMoreNews() {
    if (newsIndex >= allNews.length) return;
    showLoading();
    const end = Math.min(newsIndex + batchSize, allNews.length);
    for (let i = newsIndex; i < end; i++) {
      const newsItem = allNews[i];
      const card = createNewsCard(newsItem, i);
      streamEl.appendChild(card);
      // Insert a placeholder for advertisements after every batch, except at the end
      if ((i + 1) % batchSize === 0 && i + 1 < allNews.length) {
        const adDiv = document.createElement('div');
        adDiv.classList.add('ad-placeholder');
        adDiv.innerHTML = '<p>Advertisement</p>';
        streamEl.appendChild(adDiv);
      }
    }
    newsIndex = end;
    hideLoading();
  }

  // Infinite scroll: load more news when near the bottom
  window.addEventListener('scroll', () => {
    if (window.innerHeight + window.pageYOffset >= document.body.offsetHeight - 200) {
      if (newsIndex < allNews.length) {
        loadMoreNews();
      }
    }
  });
});