/**
 * Kiosk Mode Controls & User Interaction
 * Manages fullscreen, arrow stepping, pause/resume, and idle cursor hiding
 */

class KioskControls {
  constructor(slideshow) {
    this.slideshow = slideshow;
    this.idleTimeout = null;
    this.statusDot = document.getElementById('statusDot');
    this.statusText = document.getElementById('statusText');
  }

  init() {
    this.bindKeyboard();
    this.bindIdleCursor();
    this.bindClicks();
  }

  bindKeyboard() {
    document.addEventListener('keydown', (e) => {
      switch (e.key) {
        case 'ArrowRight':
        case 'n':
        case 'N':
          this.slideshow.nextSlide();
          break;

        case 'ArrowLeft':
        case 'p':
        case 'P':
          this.slideshow.prevSlide();
          break;

        case ' ':
          e.preventDefault();
          this.togglePause();
          break;

        case 'f':
        case 'F':
          this.toggleFullscreen();
          break;

        case 't':
        case 'T':
          this.toggleTestMode();
          break;

        case 'r':
        case 'R':
          window.location.reload();
          break;
      }
    });
  }

  togglePause() {
    const isPaused = this.slideshow.togglePause();
    if (this.statusDot) {
      this.statusDot.classList.toggle('paused', isPaused);
    }
    if (this.statusText) {
      this.statusText.textContent = isPaused ? 'PAUSED' : 'LIVE';
    }
  }

  toggleTestMode() {
    const active = this.slideshow.toggleTestMode();
    if (this.statusText) {
      this.statusText.textContent = active ? 'PREVIEW (2S)' : 'LIVE';
    }
  }

  toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch((err) => {
        console.warn(`Error attempting to enable fullscreen: ${err.message}`);
      });
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  }

  bindClicks() {
    // Optional click on status pill to pause/play
    const pill = document.querySelector('.kiosk-status-pill');
    if (pill) {
      pill.style.cursor = 'pointer';
      pill.addEventListener('click', (e) => {
        e.stopPropagation();
        this.togglePause();
      });
    }

    // Double-click anywhere on the screen to toggle fullscreen
    document.addEventListener('dblclick', () => {
      this.toggleFullscreen();
    });
  }

  bindIdleCursor() {
    const resetIdle = () => {
      document.body.classList.remove('idle-cursor');
      clearTimeout(this.idleTimeout);
      this.idleTimeout = setTimeout(() => {
        document.body.classList.add('idle-cursor');
      }, 3000);
    };

    window.addEventListener('mousemove', resetIdle, { passive: true });
    window.addEventListener('mousedown', resetIdle, { passive: true });
    window.addEventListener('keydown', resetIdle, { passive: true });
    resetIdle();
  }
}

window.KioskControls = KioskControls;
