/**
 * Main Application Bootstrap & Kiosk Lifecycle
 */

(function () {
  'use strict';
  // Bounded counters for unattended observation. Never retain exception bodies.
  const diagnostics = window.MaeDiagnostics = { errors: 0, unhandledRejections: 0 };
  window.addEventListener('error', () => { diagnostics.errors = Math.min(1000000, diagnostics.errors + 1); });
  window.addEventListener('unhandledrejection', () => { diagnostics.unhandledRejections = Math.min(1000000, diagnostics.unhandledRejections + 1); });

  // Update Live Formatted Clock
  function initClock() {
    const timeEl = document.getElementById('clockTime');
    const dateEl = document.getElementById('clockDate');

    function update() {
      const now = new Date();
      
      const timeOpts = {
        hour: 'numeric',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
      };
      
      const dateOpts = {
        weekday: 'long',
        month: 'short',
        day: 'numeric',
        year: 'numeric'
      };

      if (timeEl) timeEl.textContent = now.toLocaleTimeString('en-US', timeOpts);
      if (dateEl) dateEl.textContent = now.toLocaleDateString('en-US', dateOpts);
    }

    update();
    setInterval(update, 1000);
  }

  let baseData = null;
  let newsData = window.MaeNews.empty();
  let loading = false;

  // Independent bounded requests; a news failure cannot replace the base deck.
  async function loadSlideData() {
    const results = await Promise.allSettled([
      window.MaeNews.fetchJson('data/slides.json', 512 * 1024),
      window.MaeNews.fetchJson('data/news.json')
    ]);
    if (results[0].status === 'fulfilled' && results[0].value && Array.isArray(results[0].value.slides) && results[0].value.slides.length) {
      baseData = results[0].value;
    }
    if (!baseData) baseData = JSON.parse(JSON.stringify(window.DEFAULT_SLIDES_DATA || { slides: [] }));
    if (results[1].status === 'fulfilled') {
      try { newsData = window.MaeNews.validate(results[1].value); }
      catch (_) { console.warn('News validation failed; retaining unexpired news.'); }
    }
    return window.MaeNews.compose(baseData, newsData);
  }

  // Background Watchdog for Auto-Updates
  function setupWatchdog(slideshow) {
    const pollInterval = (slideshow.config.contentPollIntervalMinutes || 10) * 60 * 1000;
    
    const refresh = async () => {
      if (loading) return;
      loading = true;
      try {
        const newData = await loadSlideData();
        if (JSON.stringify(newData.slides) !== JSON.stringify(slideshow.pendingData ? slideshow.pendingData.slides : slideshow.slides) ||
            JSON.stringify(newData.config) !== JSON.stringify(slideshow.config)) {
          slideshow.queueData(newData);
        }
      } catch (e) {
        console.warn('Watchdog check failed.');
      } finally { loading = false; }
    };
    setInterval(refresh, pollInterval);
    slideshow.beforeAdvance = () => {
      const current = window.MaeNews.compose(baseData, newsData);
      if (JSON.stringify(current.slides) !== JSON.stringify(slideshow.pendingData ? slideshow.pendingData.slides : slideshow.slides)) slideshow.pendingData = current;
    };
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) {
        slideshow.beforeAdvance();
        if (slideshow.pendingData) slideshow.applyPending(false);
        refresh();
      }
    });
  }

  // Lock layout to the 2048×1152 design canvas and scale it to the viewport
  // so type, spacing, and cards stay in the same proportions on every display.
  const DESIGN_WIDTH = 2048;
  const DESIGN_HEIGHT = 1152;

  function fitDesignCanvas() {
    const root = document.querySelector('.kiosk-root');
    if (!root) return;

    const scale = Math.min(
      window.innerWidth / DESIGN_WIDTH,
      window.innerHeight / DESIGN_HEIGHT
    );
    const x = (window.innerWidth - DESIGN_WIDTH * scale) / 2;
    const y = (window.innerHeight - DESIGN_HEIGHT * scale) / 2;
    root.style.transform = 'translate(' + x + 'px, ' + y + 'px) scale(' + scale + ')';
  }

  // Application Entry Point
  window.addEventListener('DOMContentLoaded', async () => {
    fitDesignCanvas();
    window.addEventListener('resize', fitDesignCanvas);
    window.addEventListener('orientationchange', fitDesignCanvas);
    if (window.visualViewport) {
      window.visualViewport.addEventListener('resize', fitDesignCanvas);
    }

    initClock();

    const data = await loadSlideData();

    // Start Weather Service
    const weather = new window.WeatherService(data.config || {});
    weather.init();
    window.appWeather = weather;

    // Start Slideshow Engine
    const slideshow = new window.SlideshowEngine(data);
    slideshow.init();
    window.appSlideshow = slideshow;

    // Start Kiosk Controls
    const controls = new window.KioskControls(slideshow);
    controls.init();
    window.appControls = controls;

    // Start Auto-Refresh Watchdog
    setupWatchdog(slideshow);
  });
})();
