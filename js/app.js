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

  // Application Entry Point
  window.addEventListener('DOMContentLoaded', async () => {
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
