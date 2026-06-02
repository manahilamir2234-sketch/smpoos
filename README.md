# SMPOOS - Smart Maritime Port Operations Optimisation System

A Python-based dashboard for managing port operations, infrastructure, routes, personnel, and operational notifications.

SMPOOS is a maritime management prototype designed for HarbourView International Port to address the complexities of modern logistics. The system provides a unified interface for monitoring vessel paths, environmental status, and port asset utilization, built using Pure Python logic without external CSS frameworks.

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
10. [Known Issues/Limitations](#known-issueslimitations)
11. [Future Enhancements](#future-enhancements)
12. [Contributors](#contributors)
13. [Licensing](#licensing)
14. [References & Acknowledgements](#references--acknowledgements)
15. [Appendix](#appendix)

---

## Project Overview

### System Scenario
HarbourView International Port faces increasing vessel traffic and operational complexity. Manual tracking of berths and hazards leads to communication delays and safety risks.

### Core Objectives
- Centralize port asset management (berths, yards, docks).
- Automate operational notifications based on event severity.
- Provide real-time visibility into port traffic and resource occupancy.
- Implement secure, role-based access for different port personnel.

### Scope
This prototype focuses on the core management dashboard, CRUD operations for port data, and visual analytics for decision support. It uses synthetic data to simulate a live port environment.

---

## Key Features

- **Interactive Dashboard**: Real-time metrics widgets showing active berths, open routes, and critical hazards.
- **Asset Registry**: Full CRUD management for port infrastructure with search and status filtering.
- **Operational Analytics**: Strategic charts for berth utilization, peak activity hours, and route efficiency.
- **Notification Engine**: Severity-based alert system for weather warnings, equipment failure, and congestion.
- **Admin Authentication**: Secure login system with session persistence and environment variable configuration.
- **Audit Logging**: Automated tracking of all system modifications for accountability.

---

## System Architecture

SMPOOS uses a modular layered architecture:

- **Frontend (Visualisation Engine)**: Built with Dash and Plotly to generate interactive charts and tables.
- **Processing Logic**: Object-oriented Python classes in `src/smpoos_logic.py` manage the business rules and CRUD operations.
- **Data Ingestion**: A dedicated handler reads and writes to CSV files, providing a lightweight persistence layer.
- **Communication**: Components communicate via Dash callbacks, ensuring the UI stays synchronized with the underlying data state.

### Technologies Used
- **Dash**: Core web framework.
- **Plotly**: Interactive data visualization.
- **Pandas**: Data manipulation and analytics.
- **Python ABC/Enum**: For robust object-oriented structure.

---

## Directory Structure

```
smpoos_software_artefact/
├── data/                       # CSV Data Repositories
│   ├── smpoos_locations.csv
│   ├── smpoos_routes.csv
│   ├── smpoos_notifications.csv
│   └── smpoos_users.csv
├── src/                        # Source Code
│   ├── callbacks/              # Dash Callback Logic
│   ├── utils/                  # Simulation & Auth Helpers
│   ├── smpoos_logic.py         # Business Logic & Entities
│   ├── layouts.py              # UI Page Definitions
│   └── components.py           # Reusable UI Widgets
├── tests/                      # Unit Tests
├── requirements.txt            # Project Dependencies
├── .env                        # Secure Credentials
├── .gitignore                  # Version Control Rules
├── README.md                   # System Documentation
└── smpoos_app.py               # Main Entry Point
```

---

## Installation Instructions

### Prerequisites
- Python 3.11+
- pip

### Setup Steps
1. **Clone/Extract** the project folder.
2. **Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Run Application**:
   ```bash
   python smpoos_app.py
   ```

---

## Dependencies

- **Dash**: Used to build the interactive web-based dashboard and UI components.
- **Dash Bootstrap Components**: Provides structural layout elements (Containers, Rows, Tabs).
- **Plotly**: Powers the interactive charts for strategic analytics.
- **Pandas**: Handles data ingestion, filtering, and statistical analysis.
- **Pytest**: Framework used for unit testing the logic and CRUD operations.

---

## Data Sources

The system uses four synthetic CSV files. 

**IMPORTANT ETHICS NOTE**: All data used in this system is entirely synthetic and generated for academic prototyping purposes. No real-world operational data or personal information is used.

### Data Dictionary
- **Locations**: Berths, Storage Yards, Fuel Docks, etc. (ID, Name, Type, Status, Capacity).
- **Routes**: Shipping Lanes, AGV Routes, Truck Paths (Start, End, Distance, Status).
- **Notifications**: System alerts (Type, Severity, Message, Timestamp).
- **Users**: Personnel records and role assignments (Name, Role, Email, Active Status).

---

## Usage Instructions

1. **Access**: Open http://localhost:8050 in your browser.
2. **Login**: Use `admin` / `admin123`.
3. **Dashboard**: Observe the 5-second auto-refreshing metrics and live alert feed.
4. **Management**: Navigate to Assets or Routes to add/edit/delete data.
5. **Analytics**: Use the Strategic Analytics tab to view trends and performance metrics.

---

## Testing

The system is verified using the **pytest** framework.

**Coverage**:
- Entity validation logic.
- CRUD operation success/failure.
- CSV persistence integrity.
- Role-based filtering.

**Execution**:
```bash
python -m pytest tests/ -v
```

---

## Known Issues/Limitations

- **Concurrency**: Designed for single-admin use; no multi-user file locking.
- **AIS Feed**: Vessel tracking is simulated; no live AIS integration.
- **Network**: UI layout is optimized for standard desktop resolutions.

---

## Future Enhancements

- **Live AIS Integration**: Connecting to real-world vessel data feeds.
- **Machine Learning**: Predictive models for berth congestion forecasting.
- **Database Backend**: Migrating from CSV to PostgreSQL for scalability.
- **Mobile Access**: Developing a responsive interface for field workers.

---

## Contributors

- **Developer**: Manahil
- **Student ID**: [ID]
- **Project**: CPS7002 Assessment 2
- **Institution**: St Mary's University

---

## Licensing

This project is for academic purposes only and is not intended for commercial deployment.

---

## References & Acknowledgements

- **Dash Documentation**: Official guides for component development.
- **Plotly Python Library**: Visualization standards.
- **Academic Sources**: Design decisions informed by maritime logistics case studies.

---

## Appendix

### Accessibility Considerations
The dashboard uses high-contrast text and standard HTML elements to ensure readability across different browser environments.

### Benchmark Results
The system maintains a sub-200ms response time for local CSV operations and UI callback execution under standard prototype data loads.
