/* MAE news boundary: validate untrusted JSON before it reaches the slide renderer. */
(function () {
  'use strict';
  const clone = value => JSON.parse(JSON.stringify(value));
  const empty = () => ({ schemaVersion: 1, contentUpdatedAt: null, items: [] });
  const qrCache = new Map();
  function qrImage(value) {
    try {
      const url = new URL(value);
      if (url.protocol !== 'https:' || url.username || url.password || url.port || value.length > 2048) return null;
      if (qrCache.has(value)) return qrCache.get(value);
      const qr = window.qrcodegen.QrCode.encodeText(value, window.qrcodegen.QrCode.Ecc.MEDIUM);
      const border = 4, size = qr.size + border * 2, path = [];
      for (let y = 0; y < qr.size; y++) for (let x = 0; x < qr.size; x++) {
        if (qr.getModule(x, y)) path.push(`M${x + border},${y + border}h1v1h-1z`);
      }
      // SVG contains only numeric module coordinates, never source-supplied markup.
      const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${size} ${size}" shape-rendering="crispEdges"><rect width="100%" height="100%" fill="white"/><path d="${path.join('')}" fill="black"/></svg>`;
      const result = 'data:image/svg+xml;base64,' + btoa(svg);
      if (qrCache.size >= 24) qrCache.clear();
      qrCache.set(value, result);
      return result;
    } catch (_) { return null; } // A QR asset failure must not stop the base presentation.
  }
  const dateString = value => typeof value === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(value) &&
    Number.isFinite(Date.parse(value + 'T12:00:00Z')) && new Date(value + 'T12:00:00Z').toISOString().slice(0, 10) === value;
  const utc = value => typeof value === 'string' && /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/.test(value) && Number.isFinite(Date.parse(value));
  function itemValid(item, now) {
    if (!item || typeof item !== 'object' || Array.isArray(item)) return false;
    const bounds = { id: 64, title: 180, url: 2048, publishedDate: 10, summary: 300, source: 80, expiresAt: 30 };
    const event = Object.hasOwn(item, 'eventStartsAt');
    if (event) bounds.eventStartsAt = 30;
    if (Object.keys(item).length !== Object.keys(bounds).length) return false;
    for (const [key, limit] of Object.entries(bounds)) {
      if (event && key === 'publishedDate' && item[key] === null) continue;
      if (typeof item[key] !== 'string' || !item[key].trim() || [...item[key]].length > limit || /[\x00-\x1f\x7f<>]/.test(item[key])) return false;
    }
    try {
      const url = new URL(item.url);
      if (url.protocol !== 'https:' || url.hostname !== 'wmich.edu' || url.username || url.password || url.port) return false;
    } catch (_) { return false; }
    const today = new Intl.DateTimeFormat('en-CA', { timeZone: 'America/New_York', year: 'numeric', month: '2-digit', day: '2-digit' }).format(now);
    const publication = Date.parse(item.publishedDate + 'T00:00:00Z');
    const expiry = Date.parse(item.expiresAt);
    return /^[a-f0-9]{24}$/.test(item.id) && utc(item.expiresAt) && expiry > now.getTime() && (event ?
      item.publishedDate === null && utc(item.eventStartsAt) && item.expiresAt === item.eventStartsAt && expiry <= now.getTime() + 60 * 86400000 :
      dateString(item.publishedDate) && item.publishedDate <= today && expiry > publication && expiry <= publication + 181 * 86400000);
  }
  function validate(feed, now = new Date()) {
    if (!feed || feed.schemaVersion !== 1 || !Array.isArray(feed.items) || feed.items.length > 8 ||
        (feed.contentUpdatedAt !== null && !utc(feed.contentUpdatedAt))) throw new Error('Invalid news schema');
    const seen = new Set();
    return { schemaVersion: 1, contentUpdatedAt: feed.contentUpdatedAt, items: feed.items.filter(item => {
      if (!itemValid(item, now) || seen.has(item.id)) return false;
      seen.add(item.id);
      return true;
    }).map(clone) };
  }
  function compose(base, feed, now = new Date()) {
    const data = clone(base);
    data.slides = (data.slides || []).filter(s => s.type !== 'mae-news');
    if (data.config && data.config.newsEnabled === false) return data;
    const news = validate(feed, now);
    // Keep the base presentation running on encoder failure, but never display
    // an inaccessible news row with a missing QR. Publication tests require all.
    const available = news.items.map(item => ({ ...item, qrDataUrl: qrImage(item.url) }))
      .filter(item => item.qrDataUrl);
    const pages = [];
    for (let i = 0; i < available.length; i += 3) {
      const items = available.slice(i, i + 3).map(item => ({ ...item,
        title: editorialText(item.title), summary: editorialText(item.summary), source: editorialText(item.source) }));
      pages.push({ id: 'mae-news-' + items.map(item => item.id).join('-'), type: 'mae-news',
        duration: 25000, newsItems: items, page: pages.length + 1, pages: Math.ceil(available.length / 3) });
    }
    const at = data.slides.findIndex(s => s.type === 'wayfinding');
    data.slides.splice(at < 0 ? data.slides.length : at, 0, ...pages);
    return data;
  }
  async function fetchJson(url, limit = 65536) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), 10000);
    try {
      const response = await fetch(url + '?t=' + Date.now(), { cache: 'no-store', signal: controller.signal });
      if (!response.ok) throw new Error('HTTP ' + response.status);
      const reader = response.body.getReader();
      const chunks = [];
      let length = 0;
      while (true) {
        const result = await reader.read();
        if (result.done) break;
        length += result.value.byteLength;
        if (length > limit) { controller.abort(); throw new Error('Response too large'); }
        chunks.push(result.value);
      }
      const bytes = new Uint8Array(length);
      let offset = 0;
      chunks.forEach(chunk => { bytes.set(chunk, offset); offset += chunk.byteLength; });
      return JSON.parse(new TextDecoder().decode(bytes));
    } finally { clearTimeout(timer); }
  }
  function formatDate(value) {
    return dateString(value) ? new Intl.DateTimeFormat('en-US', { timeZone: 'UTC', month: 'short', day: 'numeric', year: 'numeric' })
      .format(new Date(value + 'T12:00:00Z')) : '';
  }
  function editorialText(value) {
    // Presentation only: retain the source's original copy in the feed.
    return value.replace(/^KALAMAZOO,\s*Mich\.\s*[\u2014\u2013-]\s*/i, '')
      .replace(/(\d)\s*[\u2014\u2013]\s*(\d)/g, '$1 to $2')
      .replace(/([.!?])\s*[\u2014\u2013]\s*/g, '$1 ')
      .replace(/\s*[\u2014\u2013]\s*/g, ', ').replace(/,\s*,/g, ',').trim();
  }
  function itemDate(item) {
    if (!item.eventStartsAt) return formatDate(item.publishedDate);
    return new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York',
      month: 'short', day: 'numeric', year: 'numeric', hour: 'numeric', minute: '2-digit', timeZoneName: 'short' })
      .format(new Date(item.eventStartsAt));
  }
  window.MaeNews = { empty, validate, compose, fetchJson, formatDate, editorialText, itemDate, qrImage };
})();
