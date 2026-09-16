/**
 * Main Application Bootstrap & Kiosk Lifecycle
 */

(function () {
  'use strict';

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

  // Load Slides Configuration (Network with local fallback)
  async function loadSlideData() {
    try {
      const response = await fetch('data/slides.json?t=' + Date.now(), { cache: 'no-store' });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (err) {
      console.warn('slides.json fetch failed, using fallback bundled data:', err.message);
      return window.DEFAULT_SLIDES_DATA || {};
    }
  }

  // Background Watchdog for Auto-Updates
  function setupWatchdog(slideshow) {
    const pollInterval = (slideshow.config.contentPollIntervalMinutes || 10) * 60 * 1000;
    
    setInterval(async () => {
      try {
        const newData = await loadSlideData();
        if (newData && newData.slides && JSON.stringify(newData.slides) !== JSON.stringify(slideshow.slides)) {
          console.log('Slide updates detected! Refreshing presentation in background...');
          slideshow.slides = newData.slides;
          slideshow.renderAllSlides();
          slideshow.showSlide(slideshow.currentIndex);
        }
      } catch (e) {
        console.warn('Watchdog check failed:', e);
      }
    }, pollInterval);
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

    // Start Slideshow Engine
    const slideshow = new window.SlideshowEngine(data);
    slideshow.init();

    // Start Kiosk Controls
    const controls = new window.KioskControls(slideshow);
    controls.init();

    // Start Auto-Refresh Watchdog
    setupWatchdog(slideshow);
  });
})();
