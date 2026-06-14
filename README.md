# Oppizi QA Tech Test
## Francisco Roldan — QA Engineer

---

## Overview

This repository contains the complete submission for the Oppizi QA Engineering technical assessment. It covers system architecture diagrams, API test automation, and a manual test suite across three parts.

**Candidate:** Francisco Roldan
**Role:** QA Engineer
**Repository:** https://github.com/roldn/Oppizi-RoldanFrancisco-QATechTest

---

## Repository Structure

```
Oppizi-RoldanFrancisco-QATechTest/
│
├── README.md                                        ← this file
│
├── Part 1 – System Journeys and Architecture/
│   ├── Oppizi_System_Diagrams.drawio                ← 3 editable diagrams
│   └── README.md                                    ← setup and navigation guide
│
├── Part 2 – API Testing + Automation/
│   ├── Oppizi – Open Charge Map API Tests.postman_collection.json
│   ├── Oppizi – OCM API (Environment).postman_environment.json
│   ├── run_tests.sh                                 ← Mac / Linux runner
│   ├── run_tests.bat                                ← Windows runner
│   ├── README.md                                    ← full setup guide
│   ├── scripts/
│   │   ├── generate_report.py                       ← custom HTML report generator
│   │   └── parse_results.py                         ← QA terminal analysis
│   └── reports/
│       ├── OCM_RUN_SAMPLE_custom_report.html        ← sample report from a real run
│       └── OCM_RUN_SAMPLE_results.json              ← raw Newman JSON output
│
└── Part 3 – Manual Testing/
    ├── Oppizi_Manual_Test_Suite_Part3.docx          ← full manual test suite
    └── README.md                                    ← document guide
```

---

## Part 1 — System Journeys and Architecture

**File:** `Part 1 – System Journeys and Architecture/Oppizi_System_Diagrams.drawio`

Three integration diagrams built in draw.io covering the two core system journeys of the Oppizi platform:

**Journey 1 – Campaign Creation**
Swimlane sequence diagram showing the API integration chain from the Admin Dashboard through the Campaign API, Geo Service, QR Service, and Campaign DB. Highlights validation gates, error paths, and the status transition to `Draft`.

**Journey 2 – Agent Flyer Scan**
Swimlane sequence diagram showing the scan flow from the Field Agent mobile app through the Agent API, Geofence Service, QR Validation, Delivery Log DB, and Audit Log. Highlights the synchronous gate chain and async audit write.

**Component Interaction Overview**
Four-layer component diagram showing all services and their integration relationships across both journeys — Client, API/Gateway, Data Services, and Storage/Reporting.

→ See `Part 1 – System Journeys and Architecture/README.md` for setup and navigation instructions.

---

## Part 2 — API Testing + Automation

**API under test:** Open Charge Map v3 (`https://api.openchargemap.io/v3/`)
**Tool:** Postman / Newman

A full API test suite with automated execution and a custom-built HTML report generator.

**Test coverage — 72 assertions across 25 requests:**

| Endpoint | Tests | Categories covered |
|---|---|---|
| `GET /poi/` | 13 requests | Status, performance SLA, schema, business logic, negative |
| `GET /referencedata/` | 12 requests | Status, performance SLA, schema, business logic, negative |

**Key test highlights:**
- Haversine-based geofencing validation (POI-08) — verifies all returned stations fall within the requested radius
- Cross-endpoint referential integrity (REF-11) — validates that every `ConnectionTypeID` found in live POI data exists in the reference catalogue
- Boundary and negative scenarios including ocean coordinates, missing API key, and duplicate QR detection

**Automation runner:**
A single command runs all tests, generates a JSON result file, and automatically opens a custom HTML report in the browser:

```bash
# Mac / Linux
OCM_API_KEY=your-key-here ./run_tests.sh
```

```bat
:: Windows
set OCM_API_KEY=your-key-here
run_tests.bat
```

**Custom HTML report features:**
- Pass rate donut chart with live score
- Performance metrics: P50, P90, P95, SLA verdict
- Interactive results table filterable by Pass / Fail / POI / REF
- Per-failure QA root cause analysis
- Post-run risk register with action owners

→ See `Part 2 – API Testing + Automation/README.md` for full setup, installation prerequisites, and troubleshooting guide.

---

## Part 3 — Manual Testing

**File:** `Part 3 – Manual Testing/Oppizi_Manual_Test_Suite_Part3.docx`

**Scenario:** Route Conflict Detection and Reassignment Auditing

A comprehensive manual test suite for the Oppizi route reassignment feature, covering the full set of constraints: reassignment only before campaign start, no overlapping agent schedules, location type matching, audit log immutability, confirmation email delivery, and 24-hour post-reassignment lock.

**Deliverables inside the document:**

| Section | Content |
|---|---|
| Test Case Index | All 20 test cases with ID, category, priority, and dataset mapping |
| Detailed Test Cases | Step-by-step test cases with preconditions and expected results |
| Test Data | Campaign/route reference table + agent reference table |
| Audit & Email Verification | Step-by-step procedures for audit API and Mailtrap validation |
| Sample Bug Report | Fully populated defect report (BUG-2025-001) |
| Assumptions & Risk Register | 8 documented assumptions + 7 risk entries |
| Regression Impact Checklist | 10 modules with risk ratings and specific regression scenarios |

**20 test cases across 4 categories:**

| Category | Count | IDs |
|---|---|---|
| Functional | 5 | TC-F-01 → TC-F-05 |
| Negative | 5 | TC-N-01 → TC-N-05 |
| Edge | 5 | TC-E-01 → TC-E-05 |
| Permissions | 5 | TC-P-01 → TC-P-05 |

→ See `Part 3 – Manual Testing/README.md` for document navigation guide.

---

## How to run the API tests (quick start)

**Prerequisites:** Node.js + Newman installed. See Part 2 README for installation instructions.

```bash
# 1. Enter the Part 2 folder
cd "Part 2 – API Testing + Automation"

# 2. Mac — make the script executable (first time only)
chmod +x run_tests.sh

# 3. Run all tests
OCM_API_KEY=your-api-key-here ./run_tests.sh
```

The custom HTML report opens automatically in your browser when the run completes.
Results are saved in `Part 2 – API Testing + Automation/reports/`.

---

## Getting an API key

The Open Charge Map API key is free:

1. Go to **https://openchargemap.org** and sign in
2. Click your username in the top navigation bar → **My Profile**
3. Navigate to **My Apps** → **Register An Application**
4. Enter any name and save — your API key appears on that page

---

## Tech stack

| Tool | Purpose |
|---|---|
| draw.io | Architecture and sequence diagrams |
| Postman | API test collection authoring |
| Newman | CLI test runner |
| Python 3 | Custom HTML report generator |
| newman-reporter-htmlextra | Raw HTML fallback report |

---

*Oppizi QA Engineering Technical Assessment — Francisco Roldan*
