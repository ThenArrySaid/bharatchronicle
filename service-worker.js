const CACHE_NAME = 'bharat-chronicle-v1';
const FILES_TO_CACHE = [
  '/',
  '/index.html',
  '/news.html',
  '/about.html',
  '/privacy.html',
  '/terms.html',
  '/opinions.html',
  '/style.css',
  '/script.js',
  '/data/news.json',
  '/images/hero.png',
  '/images/post1.png',
  '/images/post2.png',
  '/images/post3.png',
  '/images/post4.png',
  '/manifest.json'
];

self.addEventListener('install', (evt) => {
  evt.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(FILES_TO_CACHE);
    })
  );
  self.skipWaiting();
});

self.addEventListener('activate', (evt) => {
  evt.waitUntil(
    caches.keys().then((keyList) => {
      return Promise.all(
        keyList.map((key) => {
          if (key !== CACHE_NAME) {
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

self.addEventListener('fetch', (evt) => {
  evt.respondWith(
    caches.match(evt.request).then((response) => {
      return response || fetch(evt.request);
    })
  );
});