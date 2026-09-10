# Western Michigan University - Department of Mechanical & Aerospace Engineering Display Board

A broadcast-grade digital signage board system built for Western Michigan University's Department of Mechanical and Aerospace Engineering (MAE) in **Elson S. Floyd Hall** on the **Parkview Campus**.

Designed and tuned specifically to run on an **Ubuntu 24.04 LTS iMac (iMac13,2)** driving a **55-inch commercial display ("BBY 55\"")** at **2048 × 1152 (16:9)** in **Firefox under Wayland**.

---

## 🌟 Key Features

* **Official WMU Branding**: Uses official **WMU Brown (`#532E1F`)**, **WMU Gold (`#F1C500`)**, dark glassmorphism, and brand typography (**Montserrat** and **JetBrains Mono**).
* **Distance-Scaled Typography**: Fluid scaling tuned for a 55-inch display viewed across a busy department hallway (10–30 feet).
* **Data-Driven Architecture**: All slide contents, announcements, events, and lab highlights are configured in `data/slides.json`. Update slides without touching HTML, CSS, or JS code!
* **AIAA Pegasus Chapter Spotlight**: Dedicated showcase for WMU's flagship aerospace branch, including **RCAT** (Design/Build/Fly), **ARC** (NASA Student Launch Initiative), and **BPL** (Bronco Propulsion Lab solid rocket motor).
* **Flagship Student Engineering Teams**: Rich presentation cards for **Bronco Racing (Formula SAE)**, **WMU Sunseeker (Solar Car)**, **WALI (CubeSat)**, and **Bronco Baja SAE**.
* **Live Kalamazoo Weather**: Real-time Parkview Campus weather powered by Open-Meteo with automatic offline caching.
* **Senior Design Conference Countdown**: Live ticking countdown timer to the Capstone Conference in the Floyd Hall Atrium.
* **Kiosk Reliability (Wayland + Firefox)**:
  * Hardware-accelerated CSS animations (`translate3d`, `opacity`).
  * Auto-hiding mouse cursor after 3 seconds of stillness.
  * Continuous background watchdog that auto-updates slides every 10 minutes without screen flickering or restarts.
  * Offline fallback mode so it runs seamlessly even if the network drops.

---

## 🖥️ Hardware & Display Profile

* **Host Computer**: Apple iMac 13,2 (Late 2012 27" iMac)
  * CPU: Intel Core i5-3470S (4 cores)
  * RAM: 8.0 GiB
  * GPU: NVIDIA GeForce Kepler (NVE7 / GK104)
  * OS: Ubuntu 24.04.5 LTS (Noble Numbat), GNOME 46 on Wayland
* **Display**: 55-inch Display ("BBY 55\"")
  * Resolution: **2048 × 1152** @ 59.91 Hz (16:9)
  * Scale: 100%

---

## 🚀 Quick Start

### 1. Running Locally
Simply open `index.html` in Firefox:
```bash
firefox index.html
```
Or use the provided Wayland kiosk launcher:
```bash
./scripts/launch-kiosk.sh
```

### 2. Auto-Start on Ubuntu Boot
To configure the display to start automatically when the Ubuntu machine powers on:

1. Open **Startup Applications** in GNOME:
   ```bash
   gnome-session-properties
   ```
2. Click **Add**:
   * **Name**: WMU MAE Department Display
   * **Command**: `/home/thoward/Repos/department-display/scripts/launch-kiosk.sh`
   * **Comment**: Auto-launch Firefox digital signage in kiosk mode

---

## ⌨️ Keyboard Controls

| Key | Action |
| :--- | :--- |
| **`Space`** | **Pause / Resume** the auto-advancing slideshow (status pill updates to `PAUSED`) |
| **`→` / `N`** | Step to the **Next** slide immediately |
| **`←` / `P`** | Step to the **Previous** slide immediately |
| **`F` / `F11`** | Toggle **Fullscreen** mode |
| **`T`** | Toggle **Fast Preview Mode** (2 seconds per slide for quick review) |
| **`R`** | Force **Reload** the display |

---

## 📝 Customizing Slides (`data/slides.json`)

To add, remove, or edit slides, open `data/slides.json`. The application will automatically detect changes and hot-update!

### Example 1: Editing Department Announcements
```json
{
  "id": "announcements-board",
  "type": "announcements",
  "duration": 8500,
  "badge": "DEPARTMENT NOTICE BOARD",
  "title": "Department Notices & Academic Advising",
  "items": [
    {
      "category": "ACADEMIC",
      "badgeClass": "badge-gold",
      "title": "Your Announcement Title Here",
      "desc": "Details about upcoming advising, classes, or deadlines."
    }
  ]
}
```

### Example 2: Updating Senior Design Countdown Date
```json
{
  "id": "senior-design-countdown",
  "type": "event-countdown",
  "title": "Senior Engineering Design Conference",
  "targetDate": "2026-12-08T09:00:00",
  "location": "Floyd Hall Atrium & Lecture Auditoriums"
}
```

---

## 📂 File Structure

```
department-display/
├── index.html                  # Main display shell & HUD (2048x1152 optimized)
├── README.md                   # Documentation and user manual
├── scripts/
│   └── launch-kiosk.sh         # Linux/Wayland Firefox launch script
├── data/
│   ├── slides.json             # Content configuration file (all slides, events, labs, social)
│   └── fallback.js             # Offline backup data if JSON fetch fails
├── css/
│   ├── style.css               # WMU brand styling, 55" distance scaling, glassmorphism
│   ├── animations.css          # Kinetic transitions, Ken Burns, particles
│   └── typography.css          # Montserrat & Georgia font configurations
├── js/
│   ├── app.js                  # Initialization & coordination
│   ├── slideshow.js            # Auto-advancing engine, progress bar, transitions
│   ├── weather.js              # Live Kalamazoo weather service with caching
│   └── controls.js             # Kiosk controls (F11, Arrows, Space, idle cursor)
└── images/
    ├── wmu-logo-gold.svg       # WMU official gold crest / logo
    ├── original.jpg ... 12.jpg # Original department photos
    ├── labs/                   # ALPE, Wind Tunnel, Auto Lab photos
    └── teams/                  # AIAA Pegasus, Formula SAE, Sunseeker, Baja, WALI
```

---

## 🌐 Deploying to GitHub Pages

To deploy changes to GitHub Pages:
```bash
git add .
git commit -m "Revamp MAE department display board"
git push origin master
```

View the live board anytime at:
[https://airbreak404.github.io/department-display/](https://airbreak404.github.io/department-display/)
