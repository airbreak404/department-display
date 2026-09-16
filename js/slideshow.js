/**
 * WMU MAE Slideshow Engine
 * Supports 8 diverse broadcast templates with smooth GPU-accelerated transitions
 * and distance-tuned typography for 55" 2048x1152 display.
 */

class SlideshowEngine {
  constructor(data) {
    this.config = data.config || {};
    this.slides = data.slides || [];
    this.currentIndex = 0;
    this.isPaused = false;
    this.testMode = false;
    this.container = document.getElementById('slidesViewport');
    this.progressBar = document.getElementById('progressBarFill');
    this.counterEl = document.getElementById('progressCounter');
    
    this.slideTimer = null;
    this.progressStartTime = 0;
    this.progressElapsed = 0;
    this.currentDuration = 8500;
    this.rafId = null;
    this.countdownTimer = null;
  }

  init() {
    if (!this.slides.length) {
      console.error('No slide data available to render.');
      return;
    }
    window.appSlideshow = this;
    this.renderAllSlides();

    const params = new URLSearchParams(window.location.search);
    const targetSlide = parseInt(params.get('slide'), 10);
    const initialIndex = (!isNaN(targetSlide) && targetSlide >= 0 && targetSlide < this.slides.length) ? targetSlide : 0;

    if (params.has('pause') || params.has('slide')) {
      this.isPaused = true;
      const statusText = document.getElementById('statusText');
      const statusDot = document.getElementById('statusDot');
      if (statusText) statusText.textContent = 'PAUSED';
      if (statusDot) statusDot.classList.add('paused');
    }

    this.showSlide(initialIndex);
  }

  renderAllSlides() {
    this.container.innerHTML = '';
    this.slides.forEach((slide, idx) => {
      const slideEl = document.createElement('div');
      slideEl.className = `slide slide-${slide.type}`;
      slideEl.id = `slide-${idx}`;
      slideEl.innerHTML = this.buildSlideHtml(slide);
      this.container.appendChild(slideEl);
    });
  }

  buildSlideHtml(slide) {
    switch (slide.type) {
      case 'split-overview':
        return this.templateSplitOverview(slide);
      case 'rso-trio':
        return this.templateRsoTrio(slide);
      case 'hero':
        return this.templateHero(slide);
      case 'aiaa-feature':
        return this.templateAIAA(slide);
      case 'lab-spotlight':
        return this.templateLabSpotlight(slide);
      case 'student-teams':
        return this.templateStudentTeams(slide);
      case 'dual-lab':
        return this.templateDualLab(slide);
      case 'social-grid':
        return this.templateSocialGrid(slide);
      case 'event-countdown':
        return this.templateCountdown(slide);
      case 'announcements':
        return this.templateAnnouncements(slide);
      case 'wayfinding':
        return this.templateWayfinding(slide);
      default:
        return this.templateSplitOverview(slide);
    }
  }

  /* ---------------- TEMPLATES ---------------- */

  templateSplitOverview(slide) {
    const metricsHtml = (slide.metrics || []).map(m => `
      <div class="overview-metric-chip">
        <span class="om-val">${m.value}</span>
        <span class="om-lbl">${m.label}</span>
      </div>
    `).join('');

    const programsHtml = (slide.programs || []).map((p, i) => `
      <div class="program-chip animate-in delay-${i + 2}">
        <span class="program-chip-name">${p.name}</span>
        <span class="program-chip-note"><span class="text-gold">✦</span> ${p.note}</span>
      </div>
    `).join('');

    const tags = slide.facilities || slide.coopFeatures || [];
    const tagsHtml = tags.length ? `
      <div class="overview-facilities-bar">
        <span class="facilities-label">KEY STRENGTHS:</span>
        ${tags.map(t => `<span class="overview-tag-item"><span class="text-gold">✦</span> ${t}</span>`).join('')}
      </div>
    ` : '';

    return `
      <div class="slide-inner">
        <div class="overview-split-grid">
          <div class="overview-info-card animate-in">
            <div class="overview-info-top">
              <div class="badge-pill">${slide.badge || 'DEPARTMENT OVERVIEW'}</div>
              <div class="overview-college-tag">${slide.college || 'COLLEGE OF ENGINEERING & APPLIED SCIENCES'}</div>
              <h1 class="overview-title">${slide.title}</h1>
              <div class="overview-location">📍 ${slide.subtitle}</div>
              <p class="overview-summary">${slide.summary}</p>
              ${metricsHtml ? `<div class="overview-metrics-strip">${metricsHtml}</div>` : ''}
            </div>
            <div>
              <div class="overview-programs-grid">
                ${programsHtml}
              </div>
              ${tagsHtml}
            </div>
          </div>
          <div class="overview-photo-card animate-in delay-2">
            <div class="overview-photo-wrapper">
              <img src="${slide.image}" alt="WMU MAE Students and Engineering Labs">
              <div class="overview-photo-overlay-tag">✦ ELSON S. FLOYD HALL • WMU PARKVIEW CAMPUS</div>
            </div>
            ${slide.caption ? `<div class="overview-photo-caption"><span class="text-gold font-bold">✦</span> ${slide.caption}</div>` : ''}
          </div>
        </div>
      </div>
    `;
  }

  templateRsoTrio(slide) {
    const orgsHtml = (slide.orgs || []).map((org, i) => `
      <div class="rso-card animate-in delay-${i + 2}">
        <div>
          <div class="rso-card-header">
            <img src="${org.logo}" alt="${org.name}" class="rso-card-logo">
            <div class="rso-card-name-block">
              <div class="rso-card-subtitle">${org.subtitle}</div>
              <h2 class="rso-card-name">${org.name}</h2>
            </div>
          </div>
          <p class="rso-card-desc">${org.desc}</p>
          ${org.highlights ? `
          <div class="rso-highlights-box">
            <div class="rso-highlights-title">KEY HIGHLIGHTS & ACTIVITIES</div>
            <ul class="rso-highlights-list">
              ${org.highlights.map(h => `<li><span class="hl-bullet">✦</span> <span>${h}</span></li>`).join('')}
            </ul>
          </div>` : ''}
        </div>
        <div class="rso-card-meta">
          <div class="rso-meta-row">
            <span class="rso-meta-label">📍 LOCATION:</span>
            <span class="rso-meta-val">${org.location}</span>
          </div>
          <div class="rso-meta-row">
            <span class="rso-meta-label">🔗 CONNECT:</span>
            <span class="rso-meta-val text-gold font-bold">${org.contact}</span>
          </div>
        </div>
      </div>
    `).join('');

    return `
      <div class="slide-inner">
        <div class="rso-header-block animate-in">
          <div class="badge-pill">${slide.badge || 'STUDENT ORGANIZATIONS'}</div>
          <h1 class="rso-title">${slide.title}</h1>
          <div class="rso-subtitle">${slide.subtitle}</div>
        </div>
        <div class="rso-trio-grid">
          ${orgsHtml}
        </div>
      </div>
    `;
  }

  templateHero(slide) {
    const statsHtml = (slide.stats || []).map((s, i) => `
      <div class="stat-card animate-in delay-${i + 2}">
        <div class="stat-num">${s.value}</div>
        <div class="stat-lbl">${s.label}</div>
      </div>
    `).join('');

    return `
      ${slide.backgroundImage ? `<div class="ken-burns-bg" style="background-image: url('${slide.backgroundImage}');"></div>` : ''}
      <div class="slide-inner">
        <div class="hero-content">
          <div class="badge-pill animate-in">${slide.tagline || 'WESTERN MICHIGAN UNIVERSITY'}</div>
          <h1 class="hero-title animate-in delay-1">${slide.title}</h1>
          <p class="hero-subtitle animate-in delay-2">${slide.subtitle}</p>
          <div class="hero-stats-row">
            ${statsHtml}
          </div>
        </div>
      </div>
    `;
  }

  templateAIAA(slide) {
    const projectsHtml = (slide.projects || []).map((p, i) => `
      <div class="aiaa-project-card animate-in delay-${i + 2}">
        <div class="project-tag">${p.tag}</div>
        <h2 class="project-title">${p.title}</h2>
        <p class="project-desc">${p.desc}</p>
      </div>
    `).join('');

    return `
      <div class="slide-inner">
        <div class="badge-pill animate-in">${slide.badge}</div>
        <div class="aiaa-header-row animate-in delay-1">
          <div class="aiaa-title-block">
            <h1 class="aiaa-main-title">${slide.title}</h1>
            <div class="aiaa-sub">${slide.subtitle}</div>
          </div>
          <div class="aiaa-meta-block">
            <div class="aiaa-hub-badge">${slide.hub}</div>
            <img src="${slide.logo}" alt="AIAA Pegasus Logo" class="aiaa-logo-img">
          </div>
        </div>
        <div class="aiaa-projects-grid">
          ${projectsHtml}
        </div>
        <div class="aiaa-footer-bar animate-in delay-5">
          <span><strong>Flagship Student Aerospace Branch</strong> • Department of Mechanical & Aerospace Engineering</span>
          <span>Connect: <strong class="text-gold">${slide.social}</strong> • <strong class="text-gold">${slide.website}</strong></span>
        </div>
      </div>
    `;
  }

  templateLabSpotlight(slide) {
    const highlightsHtml = (slide.highlights || []).map(h => `
      <li><span class="hl-bullet">✦</span> <span>${h}</span></li>
    `).join('');
    
    const sponsorsHtml = (slide.sponsors || []).map(s => `
      <span class="sponsor-tag">${s}</span>
    `).join('');

    const statsHtml = (slide.stats || []).map(st => `
      <div class="cd-stat-chip">
        <span class="cd-stat-val">${st.value}</span>
        <span class="cd-stat-lbl">${st.label}</span>
      </div>
    `).join('');

    const tagsHtml = (slide.tags || []).map(t => `<span class="tag-pill">${t}</span>`).join('');

    return `
      <div class="slide-inner">
        <div class="badge-pill animate-in">${slide.badge}</div>
        <div class="lab-split-layout">
          <div class="lab-photo-frame animate-in delay-1">
            <img src="${slide.image}" alt="${slide.labName}">
            <div class="lab-photo-badge">✦ RESEARCH FACILITY SPOTLIGHT</div>
            <div class="lab-photo-overlay">
              <span class="text-gold mono-telemetry font-bold">📍 ${slide.room}</span>
              <span class="text-sand text-sm font-bold">HIGH-VACUUM SPACE SIMULATION</span>
            </div>
          </div>
          <div class="lab-details-panel">
            <div>
              <h1 class="lab-title-text animate-in delay-2">${slide.labName}</h1>
              <div class="lab-director-box animate-in delay-3">
                <div class="lab-director-name">${slide.director}</div>
                <div class="lab-director-title">${slide.directorTitle}</div>
                <div class="lab-director-loc">📍 ${slide.room} • Western Michigan University</div>
              </div>
              <div class="lab-highlights-container animate-in delay-4">
                <div class="lab-section-title">CORE RESEARCH & CAPABILITIES</div>
                <ul class="lab-highlights-list">
                  ${highlightsHtml}
                </ul>
              </div>
            </div>
            <div>
              ${statsHtml ? `<div class="lab-stats-strip animate-in delay-4">${statsHtml}</div>` : ''}
              ${sponsorsHtml ? `
              <div class="lab-sponsors-bar animate-in delay-5">
                <span class="sponsors-label">SPONSORED BY:</span>
                ${sponsorsHtml}
              </div>` : ''}
              <div class="lab-tags-row animate-in delay-5">
                ${tagsHtml}
              </div>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  templateStudentTeams(slide) {
    const teamsHtml = (slide.teams || []).map((t, i) => `
      <div class="team-card animate-in delay-${i + 2}">
        <div>
          <div class="team-card-header">
            <img src="${t.logo}" alt="${t.name}" class="team-logo">
            <div>
              <div class="project-tag">${t.badge}</div>
              <h2 class="team-name">${t.name}</h2>
            </div>
          </div>
          <p class="team-desc">${t.desc}</p>
          <div class="team-focus-box">
            <strong class="text-gold">Focus Areas:</strong> ${t.highlights}
          </div>
        </div>
        <div class="team-footer">
          <span>${t.meeting}</span>
          <span>${t.social}</span>
        </div>
      </div>
    `).join('');

    return `
      <div class="slide-inner">
        <div class="badge-pill animate-in">${slide.badge}</div>
        <h1 class="hero-title animate-in delay-1" style="text-align: left; margin-bottom: 6px;">${slide.title}</h1>
        <p class="hero-subtitle animate-in delay-1" style="text-align: left; margin-bottom: 20px;">${slide.subtitle}</p>
        <div class="teams-grid">
          ${teamsHtml}
        </div>
      </div>
    `;
  }

  templateDualLab(slide) {
    const renderLabCard = (lab, delay) => {
      const badgesHtml = (lab.badges || []).map(b => `<span class="lab-badge-chip">${b}</span>`).join('');
      return `
        <div class="team-card animate-in delay-${delay}">
          <div>
            <div class="lab-card-image-box">
              <img src="${lab.image}" alt="${lab.title}">
              <div class="lab-card-tag">📍 ${lab.facility || 'Floyd Hall'}</div>
            </div>
            <h2 class="team-name" style="margin-bottom: 4px; font-size: clamp(20px, 1.5vw, 26px);">${lab.title}</h2>
            <div class="text-gold font-bold mb-2" style="font-size: clamp(14px, 1.05vw, 17px);">${lab.director}</div>
            <ul class="lab-highlights-list" style="margin-top: 10px; margin-bottom: 0;">
              ${lab.features.map(f => `<li><span class="hl-bullet">✦</span> <span>${f}</span></li>`).join('')}
            </ul>
          </div>
          <div>
            ${badgesHtml ? `<div class="lab-badges-strip">${badgesHtml}</div>` : ''}
            ${lab.facility ? `
            <div class="rso-meta-row" style="margin-top: 14px; padding-top: 10px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
              <span class="rso-meta-label">FACILITY:</span>
              <span class="rso-meta-val">${lab.facility}</span>
            </div>` : ''}
          </div>
        </div>
      `;
    };

    return `
      <div class="slide-inner">
        <div class="badge-pill animate-in">${slide.badge}</div>
        <h1 class="slide-heading animate-in delay-1" style="text-align: left; margin-bottom: 16px;">${slide.title}</h1>
        <div class="teams-grid">
          ${renderLabCard(slide.left, 2)}
          ${renderLabCard(slide.right, 3)}
        </div>
      </div>
    `;
  }

  templateSocialGrid(slide) {
    const cardsHtml = (slide.channels || []).map((c, i) => `
      <div class="social-card animate-in delay-${i + 2}">
        <img src="${c.logo}" alt="${c.name}" class="social-card-logo">
        <div class="social-card-info">
          <div class="project-tag" style="font-size: 12px; padding: 2px 10px;">${c.badge}</div>
          <h2 class="social-card-title">${c.name}</h2>
          <div class="social-card-handle">${c.handle}</div>
          <p class="social-card-desc">${c.desc}</p>
        </div>
      </div>
    `).join('');

    return `
      <div class="slide-inner">
        <div class="badge-pill animate-in">${slide.badge}</div>
        <h1 class="hero-title animate-in delay-1" style="text-align: left; margin-bottom: 6px;">${slide.title}</h1>
        <p class="hero-subtitle animate-in delay-1" style="text-align: left; margin-bottom: 10px;">${slide.subtitle}</p>
        <div class="social-grid-layout">
          ${cardsHtml}
        </div>
        <div class="social-hashtag-bar animate-in delay-5">
          ${slide.hashtag}
        </div>
      </div>
    `;
  }

  templateCountdown(slide) {
    const statsHtml = (slide.stats || []).map(s => `
      <div class="cd-stat-chip">
        <span class="cd-stat-val">${s.value}</span>
        <span class="cd-stat-lbl">${s.label}</span>
      </div>
    `).join('');

    const highlightsHtml = (slide.highlights || []).map(h => `
      <div class="cd-hl-item"><span class="text-gold font-bold">✦</span> <span>${h}</span></div>
    `).join('');

    return `
      <div class="slide-inner">
        <div class="badge-pill animate-in">${slide.badge}</div>
        <div class="countdown-split">
          <div class="countdown-left-panel">
            <div>
              <h1 class="slide-heading animate-in delay-1" style="text-align: left; margin-bottom: 8px;">${slide.title}</h1>
              <p class="hero-subtitle animate-in delay-2" style="text-align: left; margin-bottom: 12px; font-size: clamp(15px, 1.1vw, 19px);">${slide.description}</p>
              ${statsHtml ? `<div class="countdown-stats-strip animate-in delay-2">${statsHtml}</div>` : ''}
              <div class="countdown-timer-box animate-in delay-3" id="countdownTimerContainer">
                <div class="countdown-block">
                  <div class="countdown-digits" id="cdDays">--</div>
                  <div class="countdown-label">DAYS</div>
                </div>
                <div class="countdown-block">
                  <div class="countdown-digits" id="cdHours">--</div>
                  <div class="countdown-label">HOURS</div>
                </div>
                <div class="countdown-block">
                  <div class="countdown-digits" id="cdMinutes">--</div>
                  <div class="countdown-label">MINUTES</div>
                </div>
                <div class="countdown-block">
                  <div class="countdown-digits" id="cdSeconds">--</div>
                  <div class="countdown-label">SECONDS</div>
                </div>
              </div>
              ${highlightsHtml ? `<div class="cd-highlights-list animate-in delay-3">${highlightsHtml}</div>` : ''}
            </div>
            <div class="cd-cta-banner animate-in delay-4">
              <div class="cd-cta-icon">📍</div>
              <div>
                <div class="cd-cta-loc">${slide.location}</div>
                <div class="cd-cta-action">${slide.callToAction}</div>
              </div>
            </div>
          </div>
          <div class="lab-photo-frame animate-in delay-2" style="height: 100%;">
            <img src="${slide.image}" alt="${slide.title}">
            <div class="lab-photo-badge">✦ SENIOR CAPSTONE EXPO</div>
            <div class="lab-photo-overlay">
              <span class="text-gold font-bold">ANNUAL DESIGN DEMONSTRATION</span>
              <span class="text-sand font-bold">FLOYD HALL ATRIUM</span>
            </div>
          </div>
        </div>
      </div>
    `;
  }

  templateAnnouncements(slide) {
    const itemsHtml = (slide.items || []).map((item, i) => {
      const bulletsHtml = (item.bullets || []).map(b => `
        <li><span class="ann-bullet">✓</span> <span>${b}</span></li>
      `).join('');

      return `
        <div class="announcement-card animate-in delay-${i + 2}">
          <div>
            <div class="announcement-badge ${item.badgeClass}">${item.category}</div>
            <h2 class="announcement-title">${item.title}</h2>
            <p class="announcement-desc">${item.desc}</p>
            ${bulletsHtml ? `<ul class="announcement-bullets-list">${bulletsHtml}</ul>` : ''}
          </div>
          ${item.contact ? `
          <div class="rso-meta-row" style="margin-top: 14px; padding-top: 10px; border-top: 1px solid rgba(255, 255, 255, 0.1);">
            <span class="rso-meta-label">📍 CONTACT:</span>
            <span class="rso-meta-val">${item.contact}</span>
          </div>` : ''}
        </div>
      `;
    }).join('');

    return `
      <div class="slide-inner">
        <div class="badge-pill animate-in">${slide.badge}</div>
        <h1 class="slide-heading animate-in delay-1" style="text-align: left; margin-bottom: 14px;">${slide.title}</h1>
        <div class="announcements-grid">
          ${itemsHtml}
        </div>
      </div>
    `;
  }

  templateWayfinding(slide) {
    const roomsHtml = (slide.rooms || []).map(r => `
      <div class="room-chip">
        <span class="room-label">${r.label}</span>
        <span class="room-number">${r.room}</span>
      </div>
    `).join('');

    const contactsHtml = (slide.quickContacts || []).map(c => `
      <div class="qc-chip">
        <span class="qc-dept">${c.dept}</span>
        <span class="qc-meta">${c.room} • ${c.phone}</span>
      </div>
    `).join('');

    return `
      <div class="slide-inner">
        <div class="badge-pill animate-in">${slide.badge}</div>
        <div class="wayfinding-grid">
          <div class="wayfinding-left-panel">
            <div>
              <h1 class="slide-heading animate-in delay-1" style="text-align: left; margin-bottom: 10px;">${slide.title}</h1>
              <div class="lab-director-box animate-in delay-2" style="margin-bottom: 12px;">
                <div class="lab-director-name">${slide.chair}</div>
                <div class="lab-director-title">${slide.office} • ${slide.phone}</div>
                <div class="lab-director-title" style="margin-top: 4px;">Office Hours: ${slide.hours}</div>
              </div>
              ${contactsHtml ? `<div class="quick-contacts-grid animate-in delay-2">${contactsHtml}</div>` : ''}
            </div>
            <div>
              <div class="rso-highlights-title" style="margin-bottom: 8px;">DEPARTMENT FACILITIES & HUBS</div>
              <div class="room-chips-row animate-in delay-3">
                ${roomsHtml}
              </div>
            </div>
          </div>
          <div class="qr-panel animate-in delay-3">
            <div class="qr-box">
              <img src="https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(slide.qrUrl)}" alt="Department Website QR">
            </div>
            <div class="text-gold font-bold text-xl mb-1">${slide.qrLabel}</div>
            <div class="text-sand text-base font-mono mb-3">${slide.qrUrl.replace('https://', '')}</div>
            <div class="badge-pill" style="margin-bottom: 0;">✦ SCAN WITH MOBILE CAMERA ✦</div>
          </div>
        </div>
      </div>
    `;
  }

  /* ---------------- ENGINE LIFECYCLE ---------------- */

  showSlide(index) {
    document.querySelectorAll('.slide').forEach(s => s.classList.remove('active'));

    this.currentIndex = (index + this.slides.length) % this.slides.length;
    const nextSlideEl = document.getElementById(`slide-${this.currentIndex}`);
    if (nextSlideEl) {
      nextSlideEl.classList.add('active');
    }

    const currentSlideData = this.slides[this.currentIndex];
    this.currentDuration = this.testMode ? 2000 : (currentSlideData.duration || this.config.defaultSlideDuration || 8500);

    // Setup Countdown if on countdown slide
    this.clearIntervals();
    if (currentSlideData.type === 'event-countdown') {
      this.initCountdown(currentSlideData.targetDate);
    }

    // Update Counter
    if (this.counterEl) {
      this.counterEl.textContent = `SLIDE ${this.currentIndex + 1} OF ${this.slides.length}`;
    }

    this.startProgressBar();
  }

  nextSlide() {
    this.showSlide(this.currentIndex + 1);
  }

  prevSlide() {
    this.showSlide(this.currentIndex - 1);
  }

  startProgressBar() {
    cancelAnimationFrame(this.rafId);
    clearTimeout(this.slideTimer);

    if (this.isPaused) return;

    this.progressStartTime = performance.now();
    this.progressElapsed = 0;

    const tick = (now) => {
      if (this.isPaused) return;

      this.progressElapsed = now - this.progressStartTime;
      const pct = Math.min(100, (this.progressElapsed / this.currentDuration) * 100);

      if (this.progressBar) {
        this.progressBar.style.width = `${pct}%`;
      }

      if (this.progressElapsed >= this.currentDuration) {
        this.nextSlide();
      } else {
        this.rafId = requestAnimationFrame(tick);
      }
    };

    this.rafId = requestAnimationFrame(tick);
  }

  togglePause() {
    this.isPaused = !this.isPaused;
    if (this.isPaused) {
      cancelAnimationFrame(this.rafId);
      clearTimeout(this.slideTimer);
    } else {
      this.startProgressBar();
    }
    return this.isPaused;
  }

  toggleTestMode() {
    this.testMode = !this.testMode;
    this.nextSlide();
    return this.testMode;
  }

  initCountdown(targetDateStr) {
    const target = new Date(targetDateStr).getTime();

    const updateTimer = () => {
      const now = Date.now();
      const diff = target - now;

      if (diff <= 0) {
        const dEl = document.getElementById('cdDays');
        if (dEl) dEl.textContent = '00';
        return;
      }

      const days = Math.floor(diff / (1000 * 60 * 60 * 24));
      const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      const dEl = document.getElementById('cdDays');
      const hEl = document.getElementById('cdHours');
      const mEl = document.getElementById('cdMinutes');
      const sEl = document.getElementById('cdSeconds');

      if (dEl) dEl.textContent = String(days).padStart(2, '0');
      if (hEl) hEl.textContent = String(hours).padStart(2, '0');
      if (mEl) mEl.textContent = String(minutes).padStart(2, '0');
      if (sEl) sEl.textContent = String(seconds).padStart(2, '0');
    };

    updateTimer();
    this.countdownTimer = setInterval(updateTimer, 1000);
  }

  clearIntervals() {
    if (this.countdownTimer) {
      clearInterval(this.countdownTimer);
      this.countdownTimer = null;
    }
  }
}

window.SlideshowEngine = SlideshowEngine;
