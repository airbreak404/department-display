// Fallback bundled slide configuration for offline or file:// protocol use
window.DEFAULT_SLIDES_DATA = {
  "config": {
    "defaultSlideDuration": 8500,
    "weatherRefreshIntervalMinutes": 15,
    "contentPollIntervalMinutes": 10,
    "kalamazooCoordinates": {
      "lat": 42.2576,
      "lon": -85.6433
    },
    "enableKenBurns": true
  },
  "slides": [
    {
      "id": "welcome-hero",
      "type": "hero",
      "duration": 9500,
      "tagline": "COLLEGE OF ENGINEERING AND APPLIED SCIENCES",
      "title": "Mechanical & Aerospace Engineering",
      "subtitle": "Western Michigan University • Elson S. Floyd Hall • Parkview Campus",
      "backgroundImage": "images/original3.jpg",
      "stats": [
        { "value": "ABET", "label": "Accredited Programs" },
        { "value": "12+", "label": "Cutting-Edge Research Labs" },
        { "value": "$2M+", "label": "Active Research Grants" },
        { "value": "5-Year", "label": "Accelerated BS+MS (AGDP)" }
      ]
    },
    {
      "id": "aiaa-pegasus-spotlight",
      "type": "aiaa-feature",
      "duration": 9500,
      "badge": "AEROSPACE STUDENT BRANCH",
      "title": "AIAA Pegasus Chapter at WMU",
      "subtitle": "American Institute of Aeronautics and Astronautics",
      "hub": "Floyd Hall • Room F-209",
      "website": "wmuaiaa.org",
      "social": "@wmuaiaa",
      "logo": "images/teams/aiaa-pegasus-logo.jpg",
      "projects": [
        {
          "tag": "RCAT",
          "title": "Remote Control Aircraft Team",
          "desc": "Designing, building, and flying competitive radio-controlled aircraft for the national AIAA Design/Build/Fly (DBF) competition."
        },
        {
          "tag": "ARC",
          "title": "Advanced Rocketry Club",
          "desc": "Engineering and launching high-powered competition rockets in the NASA University Student Launch Initiative (USLI)."
        },
        {
          "tag": "BPL",
          "title": "Bronco Propulsion Laboratory",
          "desc": "Pioneering student aerospace research to develop and static-test WMU's first custom solid rocket motor."
        }
      ]
    },
    {
      "id": "lab-alpe",
      "type": "lab-spotlight",
      "duration": 9000,
      "badge": "RESEARCH EXCELLENCE",
      "labName": "Aerospace Laboratory for Plasma Experiments",
      "acronym": "ALPE",
      "director": "Dr. Kristina Lemmer",
      "directorTitle": "Professor of MAE • Hallquist Endowed Professor",
      "room": "Floyd Hall Propulsion Wing",
      "image": "images/labs/alpe-lemmer.jpg",
      "highlights": [
        "Spacecraft electric propulsion and plasma diagnostic development",
        "High-vacuum space simulation & thruster plume interactions",
        "Sponsored by NASA, Air Force Office of Scientific Research, and AFRL"
      ],
      "tags": ["SPACE PROPULSION", "PLASMA PHYSICS", "HALL THRUSTERS", "VACUUM CHAMBERS"]
    },
    {
      "id": "student-teams-flagship",
      "type": "student-teams",
      "duration": 9000,
      "badge": "STUDENT INNOVATION",
      "title": "Flagship Engineering Competition Teams",
      "subtitle": "Hands-on vehicle engineering from concept to competition",
      "teams": [
        {
          "name": "Bronco Racing (Formula SAE)",
          "badge": "FSAE EV / IC",
          "logo": "images/teams/bronco-racing-logo.png",
          "desc": "Designing, fabricating, and racing open-wheel formula cars at Michigan International Speedway. Currently advancing WMU's next-gen electric vehicle platform.",
          "highlights": "Powertrain • Aerodynamics • Telemetry • Chassis",
          "meeting": "Floyd Hall Student Projects Bay",
          "social": "@broncoracing • broncoracing.org"
        },
        {
          "name": "WMU Sunseeker Solar Car",
          "badge": "SOLAR CHALLENGE",
          "logo": "images/teams/sunseeker-logo.jpg",
          "desc": "30+ year tradition designing and racing highway-capable solar electric vehicles in the Formula Sun Grand Prix and the American Solar Challenge cross-country rally.",
          "highlights": "Photovoltaics • Composites • Battery Management • Aerodynamics",
          "meeting": "Floyd Hall Solar Workshop",
          "social": "@wmusolarcar • sunseekerwmu.org"
        }
      ]
    },
    {
      "id": "lab-aero-autolab",
      "type": "dual-lab",
      "duration": 9000,
      "badge": "ADVANCED MOBILITY & PROPULSION",
      "title": "Aerodynamics & Vehicle Dynamics Centers",
      "left": {
        "title": "Applied Aerodynamics Laboratory",
        "director": "Dr. Tianshu Liu, Director",
        "features": [
          "Advanced Design Subsonic & Supersonic Wind Tunnels",
          "Small turbine engine test cell & high-speed diagnostics",
          "Pressure- and temperature-sensitive paint flow measurement"
        ],
        "image": "images/original10.jpg"
      },
      "right": {
        "title": "Automotive Lab & CAViDS",
        "director": "Dr. Claudia Fajardo, Director",
        "features": [
          "Center for Advanced Vehicle Design and Simulation",
          "Single-cylinder optical research engine with Nd:YAG laser",
          "EcoCAR Innovation Challenge in partnership with GM"
        ],
        "image": "images/labs/ecocar-team.jpg"
      }
    },
    {
      "id": "social-student-life",
      "type": "social-grid",
      "duration": 9000,
      "badge": "CAMPUS CONNECTIONS",
      "title": "Connect With WMU Engineering Orgs",
      "subtitle": "Get involved in student engineering organizations at Floyd Hall",
      "channels": [
        {
          "name": "Western Aerospace Launch",
          "acronym": "WALI",
          "badge": "CubeSat & Space",
          "handle": "@wali.wmu",
          "desc": "Small satellite design, CubeSat launch, and high-altitude ballooning.",
          "logo": "images/teams/wali-logo.png"
        },
        {
          "name": "Bronco Baja SAE",
          "acronym": "BSAE",
          "badge": "Off-Road Racing",
          "handle": "@broncobaja",
          "desc": "Rugged all-terrain vehicle design and rough-terrain endurance racing.",
          "logo": "images/teams/baja-logo.png"
        },
        {
          "name": "AIAA Pegasus Chapter",
          "acronym": "AIAA",
          "badge": "Aerospace Hub",
          "handle": "@wmuaiaa",
          "desc": "RC Aircraft (DBF), Rocketry (NASA USLI), and Bronco Propulsion Lab.",
          "logo": "images/teams/aiaa-pegasus-logo.jpg"
        },
        {
          "name": "College of Engineering",
          "acronym": "CEAS",
          "badge": "Official College",
          "handle": "@wmu_engineers",
          "desc": "Official news, student spotlights, and Floyd Hall community events.",
          "logo": "images/wmu-logo-gold.svg"
        }
      ],
      "hashtag": "#WMUEngineers • Tag your projects to be featured on this display!"
    },
    {
      "id": "senior-design-countdown",
      "type": "event-countdown",
      "duration": 8500,
      "badge": "CAPSTONE SPOTLIGHT",
      "title": "Senior Engineering Design Conference",
      "targetDate": "2026-12-08T09:00:00",
      "location": "Floyd Hall Atrium & Lecture Auditoriums",
      "image": "images/labs/senior-design.jpg",
      "description": "Graduating seniors present capstone solutions to complex industrial engineering challenges sponsored by leading manufacturing and aerospace corporations.",
      "callToAction": "Free & Open to the Public • Industry Mentors & Alumni Welcome"
    },
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
          "title": "Accelerated Graduate Degree Program (AGDP)",
          "desc": "Earn your B.S. and M.S. in Mechanical or Aerospace Engineering in 5 years. Contact your faculty advisor or graduate director."
        },
        {
          "category": "RESEARCH",
          "badgeClass": "badge-slate",
          "title": "Undergraduate Research Assistantships",
          "desc": "Opportunities open in Plasma Propulsion (ALPE), Autonomous Vehicles (EEAV), and Applied Aerodynamics."
        },
        {
          "category": "STUDENT SUCCESS",
          "badgeClass": "badge-brown",
          "title": "Tutoring & CAE Computer Lab",
          "desc": "Floyd Hall Computer Aided Engineering Center is open 24/7 with active Bronco Card access. Tutoring schedule posted in F-234."
        }
      ]
    },
    {
      "id": "wayfinding-directory",
      "type": "wayfinding",
      "duration": 8500,
      "badge": "DEPARTMENT DIRECTORY",
      "title": "Department of Mechanical & Aerospace Engineering",
      "chair": "Dr. Peter Gustafson, Department Chair (Office: Floyd Hall G-215)",
      "office": "Main Department Office: Floyd Hall, Room F-234",
      "phone": "(269) 276-3420",
      "email": "mae-info@wmich.edu",
      "hours": "Monday – Friday: 8:00 AM – 5:00 PM",
      "rooms": [
        { "label": "Chair's Office", "room": "G-215" },
        { "label": "Department Office", "room": "F-234" },
        { "label": "AIAA Pegasus Hub", "room": "F-209" },
        { "label": "Fluid Mechanics Lab", "room": "G-106 / G-107" },
        { "label": "Student Projects Bay", "room": "Floyd Hall Ground Floor" }
      ],
      "qrUrl": "https://wmich.edu/mechanical-aerospace",
      "qrLabel": "Scan to visit Department Website"
    }
  ]
};
