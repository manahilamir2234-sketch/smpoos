# SMPOOS - Smart Maritime Port Operations Optimization System

A Python dashboard that can be used to oversee port operations, port infrastructure, port routes, staff and port operation notifications.

SMPOOS represents a prototype system for maritime management purposes in HarbourView International Port. This system provides a centralized platform for tracking vessel routes, environmental conditions, and the usage of port resources, being built purely on Python code.

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

### System Context
The increasing number of ships and complexity in their activities poses a problem for HarbourView International Port. This involves difficulties arising from manual control of berths and hazardous zones and related problems concerning communication and safety.

### Project Objectives
- Centralized management of the port facilities like berths, yards, docks.
- Event alerting system depending on the severity of events.
- Monitoring of traffic and availability of resources in real time.
- Access control for ensuring security.

### Project Scope
The scope of this prototype includes (i) the user interface, (ii) creation/reading/updating/deleting information about the port and its resources, and (iii) visualizations useful for decision-making. The prototype will rely on synthetic data.

---

## Key Features

- **Dashboard Interface**: Metrics that include active berth, open routes, and danger zones, displayed in widgets.
- **Assets Management**: A fully fledged CRUD interface for managing ports infrastructure, which includes search capabilities and filter options based on status.
- **Operations Analysis**: Visual analysis related to berth occupancy, busy periods, and effective routes.
- **Alert System**: Weather alerts, equipment failure, and congestion warnings, categorized into different levels of severity.
- **Admin Access Control**: An advanced access control module with session management through environment variables.
- **Activity Log Monitoring**: Automated monitoring of changes made to the system.

---

## System Architecture

SMPOOS system is designed using a modular architecture:
- **Front End (Visualization Engine)**: Developed using Dash and Plotly for graph and table based visual representations.
- **Processing Logic**: Python based object-oriented classes present in src/smpoos_logic.py that handle business logic and perform CRUD operations.
- **Data Manager**: Handler class managing the data stored in CSV files.
- **Integration Between Front End and Back End**: Using callbacks in Dash.

### Technologies Employed
- **Dash**: Primary web application framework.
- **Plotly**: Visual representation of data.
- **Pandas**: Data management and analysis.
- **Python ABC / Enum**: Object-Oriented Programming support.

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
- **Locations**: Berths, Storage Sites, Refueling Docks, etc. (ID, Name, Type, Status, Capacity).
- **Routes**: Shipping Routes, AGV Routes, Truck Routes (Start Point, End Point, Length, Status).
- **Notifications**: System notifications (Type, Severity, Content, Time Stamp).
- **Users**: User records (Name, Role, Email ID, Status).

---

## Usage Instructions

1. **Access**: Open http://localhost:8050 using your chosen internet browser.
2. **Login**: Enter the login details that are admin and admin123.
3. **Dashboard**: View the statistics with an interval of five seconds.
4. **Management**: Go to the Assets or Routes tab to manage records such as creation, deletion, and modification.
5. **Analysis**: For analysis, go to the Strategic Analytics tab.

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

- **Concurrency**: The program is built for single-user usage, and there is no provision of multi-user locking of files.
- **AIS Data**: The tracking of vessels is artificial; live AIS data is not supported.
- **Network**: GUI design takes into account common desktop display configurations.

---

## Future Improvements

- **AIS Live**: Support for live AIS vessel data is expected in future versions.
- **Machine Learning**: Implementation of machine learning techniques to predict port congestion.
- **PostgreSQL Back-end**: Migrating from storing data in .csv format to PostgreSQL.
- **Interface for Mobile Device**: Design of an adaptive interface for mobile devices.

---

## Contributors

- **Developer**: Manahil
- **Student ID**: 2515128
- **Project**: CPS7002 Assessment 2
- **Institution**: St Mary's University
