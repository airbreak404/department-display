# WMU Mechanical & Aerospace Engineering Display

[![Pages Status](https://img.shields.io/badge/GitHub%20Pages-Active-success.svg)](https://airbreak404.github.io/department-display/)
[![Display Target](https://img.shields.io/badge/Canvas-2048%C3%971152-F1C500.svg)](https://airbreak404.github.io/department-display/)
[![Platform](https://img.shields.io/badge/Ubuntu-24.04%20LTS-E95420.svg)](https://ubuntu.com)
[![Status](https://img.shields.io/badge/Deployment-24%2F7%20Kiosk-brightgreen.svg)](https://airbreak404.github.io/department-display/)

Digital signage and hallway kiosk for the Department of Mechanical and Aerospace Engineering at Western Michigan University. Located in Elson S. Floyd Hall (Parkview Campus), this system runs 24/7 to showcase student engineering teams, research facilities, department announcements, and live Kalamazoo weather.

**Live Presentation:** [https://airbreak404.github.io/department-display/](https://airbreak404.github.io/department-display/)

---

## System Architecture

```
                                  +------------------------------------+
                                  | GitHub Repository & CI             |
                                  | airbreak404/department-display     |
                                  +------------------+-----------------+
                                                     |
                                            git push | (Auto deploy)
                                                     v
+-------------------------------+         +----------------------------+
| Windows Workstation           |         | GitHub Pages (CDN)         |
| mae-display start/stop/reload |         | Web presentation           |
+---------------+---------------+         +--------------+-------------+
                |                                        ^
       SSH command forwarding                            | ETag polling
                v                                        | (every 15 min)
+---------------+----------------------------------------v-------------+
| Remote Kiosk Machine (Ubuntu 24.04 LTS, 10.80.143.128)               |
|                                                                      |
|  * Management CLI: ~/.local/bin/mae-display                          |
|  * Service: department-kiosk.service (under systemd-inhibit)         |
|  * Launcher: ~/.local/bin/kiosk-launcher.sh + 15s Wi-Fi keepalive    |
|  * RAM Disk Cache: /dev/shm/kiosk-chrome-cache/                      |
|                                                                      |
|  +-------------------------------+  +-------------------------------+|
|  | Window 1: 55" Insignia TV     |  | Window 2: 27" iMac Workstation||
|  | DP-3 at 2048x1152 (+2560,0)   |  | DP-1 at 2560x1440 (+0,0)      ||
|  | 24/7 locked fullscreen kiosk  |  | Windowed human-work opt-out   ||
|  +-------------------------------+  +-------------------------------+|
+----------------------------------------------------------------------+
```

### Proportional Layout Scaling (`fitDesignCanvas`)
The presentation is authored to a fixed **2048 × 1152** reference coordinate space. On load and resize, `js/app.js` calculates a uniform viewport transform:
- Layout, typography, card spacing, and badge chips scale in proportion across any aspect ratio or resolution.
- Typography is tuned for Floyd Hall hallway viewing distances (10–30 ft), with hero text at `131px` and body copy at `37px`.

---

## Management CLI (`mae-display`)

The kiosk is managed using the `mae-display` CLI. It can be run from the Linux kiosk host or forwarded over SSH from a Windows terminal.

### Available Commands
```bash
mae-display status          # Check systemd service, Chrome PIDs, and active displays
mae-display reload          # Trigger zero-flicker CDP reload without restarting browser
mae-display restart         # Restart systemd kiosk service
mae-display stop            # Stop kiosk and close Chrome instances cleanly
mae-display start           # Start kiosk service
mae-display logs            # View recent kiosk journalctl logs
mae-display sync            # Check GitHub Pages and reload if updated
mae-display screenshot tv   # Capture live hallway TV screenshot
mae-display screenshot mac  # Capture iMac desk display screenshot
```

### Windows Workstation Setup
The local repository includes `mae-display.cmd` and `mae-display.ps1` in `AppData\Local\agy\bin\` (which is on the system `PATH`), allowing you to type `mae-display status` or `mae-display reload` directly from PowerShell or Command Prompt.

---

## Slide Content & Data Model

Slide definitions are stored in [`data/slides.json`](data/slides.json) and mirrored in [`data/fallback.js`](data/fallback.js) for offline or local preview.

### Slide Inventory (20 Slides)
1. **Department Overview**: Degrees, enrollment metrics, Floyd Hall headquarters.
2. **Bronco Racing (Formula SAE)**: Authentic #122 open-cockpit racecar on track.
3. **Bronco Baja SAE**: Authentic Bronco Baja competition buggy on dirt track.
4. **Sunseeker Solar Car Project**: Authentic Sunseeker solar racecar competing at Formula Sun Grand Prix.
5. **AIAA Pegasus Chapter**: Aerospace rocketry and flight competition division.
6. **Western Aerospace Launch Initiative (WALI)**: SmallSat/CubeSat flight hardware and OPS-Cube mission.
7. **Autonomous Vehicles at WMU**: Aurrigo autonomous vehicle and sensor research.
8. **ASME Student Section**: Mechanical engineering professional network and design team.
9. **SMASH Hub**: Solid Mechanics & Structures Hub student research project center.
10. **Bronco Robotics**: Student robotics builders in the Floyd Hall maker space.
11. **ALPE Research Facility**: Space propulsion and vacuum plasma research lab.
12. **Applied Aerodynamics Wind Tunnel**: Floyd Hall wind tunnel car testing model with faculty/students.
13. **Automotive CAViDS Center**: Autonomous and vehicle dynamics testing laboratory.
14. **Senior Engineering Design Conference**: Live countdown to the annual capstone expo.
15. **Engineering Careers & Co-ops**: Career placement metrics, corporate recruiters, and internships.
16. **Announcement 1**: Accelerated Graduate Degree Program (AGDP) advising.
17. **Announcement 2**: Paid undergraduate research assistantships.
18. **Announcement 3**: CAE Center 24/7 access and walk-in peer tutoring.
19. **Wayfinding Directory**: MAE Department Main Office (Floyd Hall F-234), quick contacts, and QR portal.
20. **Wayfinding Facilities**: Campus map of Floyd Hall labs, machine bays, and student spaces.

---

## 24/7 Kiosk Hardening

The kiosk host includes multiple layers of 24/7 hardening:
1. **Wi-Fi Low-Power Sleep (`lps`) Prevention**:
   The Realtek USB Wi-Fi dongle (`rtw88_8822bu`) drops connection when entering USB power-saving. An active 15-second heartbeat ping in `kiosk-launcher.sh` targets the local subnet gateway (`10.80.140.1`), keeping the network interface continuously active without generating external internet traffic.
2. **Systemd Sleep & Idle Inhibitor**:
   The `department-kiosk.service` unit runs under `systemd-inhibit --what=idle:sleep`, actively preventing OS-level suspend, sleep, or GNOME screen lockouts.
3. **DPMS Hardware Lockdown**:
   The watchdog loop continuously re-enforces `xset dpms force on; xset -dpms s off s noblank`.
4. **RAM Disk Caching**:
   Chrome disk caches are mounted on `/dev/shm/kiosk-chrome-cache/{tv,mac}` (tmpfs in RAM), completely eliminating mechanical HDD wear and stutter.
5. **Zero-Flicker Chrome DevTools Protocol (CDP) Reloads**:
   Content updates reload dynamically via `Page.reload` on port `9222` without killing the browser process or flickering the screen.

---

## Project Structure

```
department-display/
├── .github/
│   └── workflows/
│       └── validate.yml      # CI workflow for JSON and asset validation
├── css/
│   ├── animations.css        # Smooth slide transitions & ambient animations
│   ├── style.css             # Layout, HUD, and glassmorphism styling
│   └── typography.css        # Distance-tuned typography scale (2048x1152)
├── data/
│   ├── fallback.js           # Offline bundled data fallback
│   └── slides.json           # Active slide deck content & timing
├── images/
│   ├── labs/                 # Facility photos (ALPE, CAViDS, Senior Design)
│   ├── teams/                # Authentic RSO competition photos and logos
│   ├── wmu-brandmark-official.svg
│   └── wmu-logo-official-dark.svg
├── js/
│   ├── app.js                # App bootstrap, canvas scaler, live clock
│   ├── controls.js           # Keyboard navigation (Space, F, arrows)
│   ├── slideshow.js          # Slide render engine & progress tracker
│   └── weather.js            # Live Open-Meteo weather service (Kalamazoo)
├── .gitignore
├── index.html                # Kiosk shell & HUD container
└── README.md
```

---

## Continuous Deployment & Sync

Changes pushed to `master` are automatically deployed to GitHub Pages. Within 15 minutes, the remote display detects the updated content signature (ETag / Last-Modified) via `department-kiosk-sync.timer` and issues a seamless zero-flicker background reload. Immediate reloads can be triggered anytime via `mae-display reload`.

---

## Local Development

To run the display locally:
```bash
# Start a simple HTTP server
python -m http.server 8000

# Open in browser
open http://localhost:8000
```

### Keyboard Shortcuts
- `Space`: Pause / Resume slide cycling
- `Right Arrow` / `N`: Next slide
- `Left Arrow` / `P`: Previous slide
- `F`: Toggle fullscreen
- `T`: Toggle 2-second fast preview mode
- `R`: Refresh presentation
