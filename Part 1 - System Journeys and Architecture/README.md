# Oppizi – System Journeys & Architecture Diagrams
### Part 1 – System Journeys and Architecture

---

## What's in this folder?

```
Part 1 – System Journeys and Architecture/
│
└── Oppizi_System_Diagrams.drawio    ← the 3 architecture and integration diagrams
```

---

## What does the `.drawio` file contain?

The file contains **3 diagrams** on separate pages within the same file:

### Diagram 1 — Journey 1: Campaign Creation
Swimlane sequence diagram showing the complete campaign creation flow from the Admin UI to the database.

**Systems involved:**
- Admin UI (Campaign Dashboard)
- Campaign API
- Geo Service
- QR Service
- Campaign DB

**Flow represented:**
1. Admin sends `POST /campaigns` from the dashboard
2. Campaign API validates the geographic area with the Geo Service (`validateArea()`)
3. Campaign API checks QR code pool availability (`checkQRPool()`)
4. Campaign API checks flyer stock levels (`checkFlyerStock()`)
5. If all validations pass → `INSERT` into Campaign DB with status `Draft`
6. If any validation fails → returns `400` error to the Admin UI

---

### Diagram 2 — Journey 2: Agent Flyer Scan
Swimlane sequence diagram showing the complete flow when a field agent scans a flyer using the mobile app.

**Systems involved:**
- Field Agent App (Mobile)
- Agent API
- Geofence Service
- QR Validation Service
- Delivery Log DB
- Audit Log / Reporting

**Flow represented:**
1. App fetches the assigned route (`GET /routes/:id`)
2. Agent scans the flyer QR code → App sends `POST /scans` with `{qr, lat, lng, timestamp}`
3. Agent API verifies the agent is within the permitted zone (`verifyLocation()`)
4. If out of zone → `403 out-of-zone (STOP)`
5. Agent API validates the QR code against the campaign (`validateQR()`)
6. If QR is invalid or duplicate → `422 (STOP)`
7. If all checks pass → `INSERT delivery_entry` into Delivery Log DB
8. Asynchronous write to Audit Log (`async → auditLog()`)
9. App receives `200 OK` with `delivery_id`

---

### Diagram 3 — Component Interaction Overview
Component diagram showing all systems and their integration relationships across both journeys.

**Layers represented:**
- **Client Layer:** Campaign Dashboard (web) · Field Agent App (mobile)
- **API / Gateway Layer:** Campaign API · Agent API
- **Data Services:** Geo Service · QR Service · Route Optimizer · Audit Log
- **Storage / Reporting:** Campaign DB · Delivery Log DB · Reporting Engine

---

## How to open and edit the file

### Option A — draw.io online (no installation required)
1. Go to **https://app.diagrams.net**
2. Click **Open Existing Diagram**
3. Select `Oppizi_System_Diagrams.drawio`
4. The 3 diagrams appear as tabs at the bottom of the screen

### Option B — draw.io desktop app (recommended)
1. Download from **https://github.com/jgraph/drawio-desktop/releases**
2. Open the `.drawio` file directly with the app

### Option C — VS Code
1. Install the **"Draw.io Integration"** extension by Henning Dieterichs
2. Open the `.drawio` file directly in VS Code

---

## Navigating between diagrams

Once the file is open in draw.io, the 3 diagrams appear as **tabs** at the bottom of the screen:

```
[ Journey 1 – Campaign Creation ] [ Journey 2 – Agent Flyer Scan ] [ Component Overview ]
```

Click each tab to switch between diagrams.

---

## Visual conventions

| Element | Meaning |
|---|---|
| Solid thick line | Synchronous call (request) |
| Dashed line | Response or asynchronous call |
| Red line | Error / failure path |
| Dark blue swimlane | Client layer (UI / App) |
| Purple swimlane | API / Gateway layer |
| Green swimlane | Data services |
| Red swimlane | Database / Storage |
| Light blue swimlane | Audit Log / Reporting |

---

## Integration test checkpoints

### Journey 1
- Geo Service must validate geographic boundary edge cases
- QR Service must return `409` when the pool is exhausted
- DB must rollback if any intermediate validation fails
- Status `Draft` is only assigned if **all** validations pass
- `campaign_id` in the response must match the DB record

### Journey 2
- Geofence Service must return `403` if GPS coordinates fall outside the campaign zone
- Duplicate QR must return a **different** error code from an invalid QR
- `delivery_entry` must **not be created** if the geofence or QR validation fails
- Audit Log must record even failed scans (observability requirement)
- `delivery_id` in the `200 OK` must match the DB record
- Async Audit Log write must **not block** the `200` response to the agent

---

## Exporting the diagrams

To export as image or PDF from draw.io:

1. Select the diagram you want to export (click the corresponding tab)
2. Go to **File → Export As** and choose the format:
   - **PNG / SVG** → for documentation or presentations
   - **PDF** → for formal document delivery
   - **XML** → to share the editable source

---

*Oppizi QA Engineering — Part 1: System Journeys and Architecture*
