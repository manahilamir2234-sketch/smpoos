# SMPOOS – Smart Maritime Port Operations Optimisation System

Python prototype dashboard for HarbourView International Port operations: berths and other locations, internal routes, personnel, and operational alerts.

This coursework artefact loads the four Moodle CSV files, exposes an authenticated Dash control centre, and supports CRUD, role-aware alert filtering, a five-second monitoring refresh, simulated email delivery, and Plotly analytics.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [System Architecture](#system-architecture)
4. [Directory Structure](#directory-structure)
5. [Installation Instructions](#installation-instructions)
6. [Dependencies](#dependencies)
7. [Data Sources](#data-sources)
8. [Usage Instructions](#usage-instructions)
9. [Testing](#testing)
10. [Known Issues / Limitations](#known-issues--limitations)
11. [Future Enhancements](#future-enhancements)
12. [Contributors](#contributors)
13. [Licensing](#licensing)
14. [References & Acknowledgements](#references--acknowledgements)

---

## Project Overview

HarbourView needs a single place to see berth status, route availability and safety alerts. SMPOOS is a Level 7 coursework prototype that demonstrates that workflow on synthetic CSV data. Target users are harbourmasters, supervisors, safety officers and (read-oriented) dock roles. Constraints: no live AIS, CSV storage only, admin login via environment variables.

---

## Key Features

| Feature | Why it exists | How it works (brief) |
|---|---|---|
| Login + consent + logout | Secure admin entry | Credentials from `.env`; consent checkbox; Logout clears session |
| Asset / route / user / alert CRUD | Brief management requirement | Modals + CSV rewrite via `SMPOOS` |
| Role selector (RBAC prototype) | Authorised changes only | Write roles enforced in callbacks; alert severity focus by role |
| Dashboard widgets | Real-time monitoring theme | 5s refresh, audit list, simulated wind/tide/visibility, acknowledge |
| Analytics page | Reporting requirement | Plotly charts + heatmap, date filter, berth suggestion |
| Simulated email log | Brief “email delivery” path | `email_utils.send_notification_email` |
| GDPR helpers | Portability / erasure theme | `export_user_data` / `erase_user_data` |

---

## System Architecture

Layers: browser UI (Dash + Bootstrap) → callback modules → `SMPOOS` OOP controller (`PortEntity` subclasses, enums, audit log) → CSV files under `data/`. Simulation and RBAC helpers sit beside the controller. See `reports/architecture_diagram.html` in the parent coursework folder for a diagram.

Technologies: Dash, Dash Bootstrap Components, Plotly, pandas, matplotlib, seaborn, pytest, python-dotenv.

---

## Directory Structure

```
smpoos_software_artefact/
├── data/                 # Moodle CSV sources
├── src/
│   ├── callbacks/        # auth, CRUD, realtime, rbac, analytics
│   ├── utils/            # auth, rbac, email, charts, simulation
│   ├── smpoos_logic.py   # OOP domain + persistence
│   ├── layouts.py
│   └── components.py
├── tests/                # pytest suite
├── requirements.txt
├── .env.example
├── README.md
└── smpoos_app.py
```

---

## Installation Instructions

Requires **Python 3.11+**.

```bash
cd smpoos_software_artefact
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # edit if you change admin credentials
python smpoos_app.py
```

Open http://localhost:8050  
Default admin (from `.env.example`): `admin` / `admin123`

---

## Dependencies

| Package | Purpose |
|---|---|
| dash | Interactive control centre |
| dash-bootstrap-components | Layout / cards / forms (brief-approved) |
| plotly | Interactive charts |
| pandas | Aggregations for analytics |
| matplotlib / seaborn | Static charts for report evidence |
| python-dotenv | Admin credentials |
| pytest | Automated tests |

---

## Data Sources

Four **synthetic** CSV files (ethics: no real operational or personal data):

- `smpoos_locations.csv` – location_id, name, type, status, capacity_tonnes  
- `smpoos_routes.csv` – route_id, start/end, route_type, distance_km, status  
- `smpoos_notifications.csv` – notification_id, alert_type, location_id, severity, message, timestamp  
- `smpoos_users.csv` – user_id, name, role, email, active  

Assumption: IDs are stable strings as supplied on Moodle.

---

## Usage Instructions

1. Start the app, tick consent, and log in (`admin` / `admin123` by default).  
2. Use **Active Role** in the sidebar; use **Logout** to clear the session.  
3. Dashboard refreshes metrics (including simulated env widgets) roughly every five seconds; select an alert and **Acknowledge**.  
4. Asset Registry / Routes / Personnel / Notifications support CRUD for write-enabled roles.  
5. Strategic Analytics: set a date range to refresh charts; berth suggestion text updates with the filter.

---

## Testing

```bash
python -m pytest tests/ -v
```

Coverage includes entity validation, CRUD + CSV round-trip, RBAC helpers, auth defaults, email simulation log, stats summary, GDPR export/erase, berth suggestion. Current suite: **20** tests.

---

## Known Issues / Limitations

- CSV files are not safe for concurrent multi-user writes.  
- AIS / environmental feeds are simulated.  
- Email delivery is logged locally, not sent via SMTP.  
- WCAG gaps remain (skip link, formal screen-reader testing).  
- Desktop-first layout.

---

## Future Enhancements

Live AIS API, PostgreSQL backend, real SMTP, stronger identity provider, berth map overlays, ML congestion prediction.

---

## Contributors

- Developer: Manahil  
- Student ID: 2515128  
- Module: CPS7002 Assessment (retake / resubmission)  
- Institution: St Mary’s University  

---

## Licensing

Academic coursework only. Not for commercial deployment.

---

## References & Acknowledgements

Assessment brief CPS7002 (Canetta, 2026); Dash / Plotly / pandas / pytest documentation. AI tools may have assisted planning or wording checks; the runnable system and tested claims are the author’s responsibility.
