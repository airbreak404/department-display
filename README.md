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
| Remote Kiosk Machine (Ubuntu 24.04 LTS, <kiosk-host-ip>)             |
|                                                                      |
|  * Management CLI: ~/.local/bin/mae-display                          |
|  * Service: department-kiosk.service (under systemd-inhibit)         |
|  * Encrypted IP Beacon: department-kiosk-ip-beacon.timer (every 2m)  |
|  * Wi-Fi Keepalive: department-kiosk-net-keepalive.timer (every 60s) |
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

The kiosk is managed using the `mae-display` CLI. It can be run locally from the Linux kiosk host or forwarded over SSH from a Windows terminal.

### Available Commands
```bash
mae-display status             # Check systemd service, Chrome PIDs, and active displays
mae-display reload             # Trigger zero-flicker CDP reload without restarting browser
mae-display restart            # Restart systemd kiosk service
mae-display stop               # Stop kiosk and close Chrome instances cleanly
mae-display start              # Start kiosk service
mae-display logs               # View recent kiosk journalctl logs
mae-display incidents          # View recent incidents and autonomous reboot requests
mae-display sync               # Check GitHub Pages and reload if updated
mae-display screenshot tv      # Capture live hallway TV screenshot
mae-display screenshot mac     # Capture iMac desk display screenshot
mae-display set-ip <new_ip>    # Manually verify and update kiosk IP address in SSH config
mae-display <new_ip>           # Shorthand to verify and set a new kiosk IP
```

### Windows Workstation Client & Zero-Touch Self-Healing
The local workstation environment includes `mae-display.cmd` and `mae-display-resolve.ps1` in `AppData\Local\agy\bin\` (on `PATH`) and integrated into the PowerShell profile (`$PROFILE`):

1. **Direct Fast-Path**: Probes the currently configured IP on port 22. If reachable, executes immediately (< 1 second).
2. **Encrypted Beacon Auto-Discovery**: If the kiosk's dynamic DHCP IP has rotated, the client queries the zero-credential encrypted rendezvous endpoint, decrypts the AES-256-CBC payload in memory, cryptographically verifies the kiosk's pinned Ed25519 host key (`ssh -o BatchMode=yes`), updates `~/.ssh/config` automatically, and runs the command.
3. **Zero Network Scanning**: Operates strictly point-to-point without sending sequential SYN scans across campus subnets.
4. **Persistent Sessions**: SSH connection uses `ServerAliveInterval 30` and `ServerAliveCountMax 3` to keep terminal sessions active across campus firewalls.

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

## 24/7 Kiosk Hardening & Security Architecture

The kiosk host includes multiple layers of 24/7 hardening and defensive security:
1. **Wi-Fi Low-Power Sleep (`lps`) Prevention**:
   The Realtek USB Wi-Fi dongle (`rtw88_8822bu`) drops connection when entering USB power-saving. A dedicated user systemd service and timer (`department-kiosk-net-keepalive.timer`) sends an ICMP ping to the local subnet gateway every 60 seconds (dynamically resolved via `ip route`), keeping the network interface continuously active and maintaining DHCP lease stability without generating external internet traffic.
2. **Zero-Credential Encrypted IP Beacon**:
   An independent systemd timer (`department-kiosk-ip-beacon.timer`) runs every 2 minutes. When network changes occur, it encrypts the new local IP with AES-256-CBC and PBKDF2 (10,000 iterations, SHA-256) and publishes the ciphertext. It requires **zero GitHub tokens, passwords, or accounts on the kiosk**, ensuring that filesystem inspection yields no usable credentials.
3. **Cryptographic SSH & Host Key Pinning**:
   - Remote SSH daemon has password authentication permanently disabled (`PasswordAuthentication no`).
   - Host key is pinned via Ed25519 in client `~/.ssh/known_hosts`, mathematically preventing spoofing or man-in-the-middle attacks.
   - `fail2ban` monitors port 22 with automated ban policies.
4. **Local Loopback Service Isolation**:
   Chrome DevTools Protocol (CDP) on port `9222` and systemd-resolved on port `53` are strictly bound to `127.0.0.1` loopback only, never exposed across the network.
5. **Systemd Sleep & Idle Inhibitor**:
   The `department-kiosk.service` unit runs under `systemd-inhibit --what=idle:sleep`, actively preventing OS-level suspend, sleep, or GNOME screen lockouts.
6. **DPMS Hardware Lockdown**:
   The watchdog loop continuously re-enforces `xset dpms force on; xset -dpms s off s noblank`.
7. **RAM Disk Caching**:
   Chrome disk caches are mounted on `/dev/shm/kiosk-chrome-cache/{tv,mac}` (tmpfs in RAM), completely eliminating mechanical HDD wear and stutter.
8. **Zero-Flicker Chrome DevTools Protocol (CDP) Reloads**:
   Content updates reload dynamically via `Page.reload` on port `9222` without killing the browser process or flickering the screen.
9. **Autonomous Watchdog Reboot Escalation**:
   After X11 remains unreachable for 180 continuous seconds, the watchdog requests `systemctl --no-ask-password reboot -i`, falling back to `loginctl --no-ask-password reboot`. X11 probes have timeouts, and the outage timer also runs when no graphical session is available at service startup. The service starts under the lingering user manager's default target and remains running when the graphical-session target stops. A locked, persistent guard permits at most two automated reboot requests per rolling 15-minute window, including failed requests; invalid guard state blocks escalation. Incidents are recorded in `~/.local/state/kiosk/incidents.log` and available through `mae-display incidents`.

   With an estimated 90-second boot, expected recovery is about 4.5 minutes plus polling/probe time. This is a recovery target, not a guaranteed outage bound: reboot authorization, a functioning watchdog/kernel, and a successful boot are required. When the guard trips, automatic reboot requests stop until a slot expires.

   **Deployment prerequisite:** reboot, multiple-session reboot, and inhibitor-bypass authorization must work without interactive authentication even after the graphical login ends. On October 6, the active watchdog passed the first two checks but inhibitor bypass required authentication; inactive-session defaults also required authentication. A service-scoped polkit rule has been prepared in the host's `kiosk-self-healing-20261006.GhpsSn` rollback bundle, but still requires administrator installation. Until then, unattended recovery relies on the active local session's permissions and absence of blocking shutdown inhibitors.
10. **iMac Human-Work Protection**:
    Both presentation windows open fullscreen at startup. During routine health checks, only the hallway TV has its geometry and fullscreen state enforced. The iMac window may be moved, minimized, or taken out of fullscreen; closing it relaunches only that window. The existing `~/.config/kiosk-mac-disabled` flag suppresses iMac relaunch. TV browser recovery can still rebuild both windows because they share one Chrome process tree.

The launcher has no `--frame-throttle-fps` limit. Other Chrome flags, GPU settings, and presentation CSS remain unchanged by this recovery update; the existing display modes determine the native refresh rates.

---

## Project Structure

```
department-display/
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
