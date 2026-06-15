# Oppizi – Open Charge Map API Test Suite
### Part 2 – API Testing and Automation

---

## Table of Contents

1. [Repository Structure](#1-repository-structure)
2. [Obtain an API Key](#2-obtain-an-api-key)
3. [Option A — Run Tests in Postman (Visual Interface)](#3-option-a--run-tests-in-postman-visual-interface)
   - 3.1 [Requirement](#31-requirement)
   - 3.2 [Import the Files](#32-import-the-files)
   - 3.3 [Configure the Environment](#33-configure-the-environment)
   - 3.4 [Run the Tests](#34-run-the-tests)
   - 3.5 [Review the Results](#35-review-the-results)
4. [Option B — Run Tests from the Terminal (Automated)](#4-option-b--run-tests-from-the-terminal-automated)
   - 4.1 [Verify Prerequisites](#41-verify-prerequisites)
   - 4.2 [Installation on Mac](#42-installation-on-mac)
   - 4.3 [Installation on Windows](#43-installation-on-windows)
   - 4.4 [Navigate to the Project Folder](#44-navigate-to-the-project-folder)
   - 4.5 [Run the Tests](#45-run-the-tests)
   - 4.6 [Terminal Output During Execution](#46-terminal-output-during-execution)
   - 4.7 [Output Files](#47-output-files)
5. [Test Cases](#5-test-cases)
   - 5.1 [GET /poi/ — 13 Tests](#51-get-poi--13-tests)
   - 5.2 [GET /referencedata/ — 12 Tests](#52-get-referencedata--12-tests)
6. [Environment Variables](#6-environment-variables)
7. [Troubleshooting](#7-troubleshooting)

---

## 1. Repository Structure

```
Part 2 – API Testing + Automation/
|
|-- Oppizi – Open Charge Map API Tests.postman_collection.json   <- Postman tests suite
|-- Oppizi – OCM API (Environment).postman_environment.json      <- environment variables
|-- run_tests.sh          <- automated execution script (Mac / Linux)
|-- run_tests.bat         <- automated execution script (Windows)
|-- README.md             <- this document
|
|-- scripts/
|   |-- generate_report.py   <- generates the HTML test report
|   |-- parse_results.py     <- detailed QA analysis output in terminal
|
|-- reports/
    |-- OCM_RUN_SAMPLE_custom_report.html   <- sample report output
    |-- OCM_RUN_SAMPLE_results.json         <- sample results in JSON format
```

Each test run generates new timestamped files in the `reports/` directory. Existing files are never overwritten.

---

## 2. Obtain an API Key

An API key is required to authenticate requests against the Open Charge Map API. It is free and takes approximately two minutes to set up.

1. Go to **https://openchargemap.org**
2. Click **Sign In** in the top-right corner and create an account, or log in if you already have one
3. Once logged in, click your name in the top navigation bar
4. Select **My Profile** from the dropdown menu
5. Navigate to the **My Apps** section within your profile page
6. Click **Register An Application**
7. Enter any application name (for example: `Oppizi Test`) and save
8. Your **API key** will appear on the same page — copy it

**Important:** Do not share your API key or commit it to any public repository.

---

## 3. Option A — Run Tests in Postman (Visual Interface)

This option is recommended if you want to inspect requests and responses one by one with full detail. It works the same way on Mac and Windows.

### 3.1 Requirement

Postman must be installed. Download it for free at: **https://postman.com/downloads**

---

### 3.2 Import the Files

- Open Postman
- Click **Import** in the top-left corner
- Select or drag both of the following files:
  - `Oppizi – Open Charge Map API Tests.postman_collection.json`
  - `Oppizi – OCM API (Environment).postman_environment.json`
- Confirm the import

---

### 3.3 Configure the Environment

Without this step, all tests will fail because the API key is not set.

- In the **top-right corner** of Postman, locate the environment selector (it will display **"No Environment"**)
- Click it and select **"Oppizi – OCM API (Environment)"**
- Click the **eye icon** next to the selector
- Find the variable named **`apiKey`**
- Click the **Current Value** field and paste your API key
- Close the panel

---

### 3.4 Run the Tests

- In the left-hand panel, locate the collection **"Oppizi – Open Charge Map API Tests"**
- Right-click it and select **Run collection**
- In the window that opens, click **Run Oppizi – Open Charge Map API Tests**

---

### 3.5 Review the Results

Results appear in Postman after the run completes:

- **Green** — the test passed
- **Red** — the test failed; the exact error message appears below the test name
- Click any test to view the full request and response details

---

## 4. Option B — Run Tests from the Terminal (Automated)

This option runs all tests in a single command and automatically generates a professional HTML report. Follow the installation section that corresponds to your operating system.

---

### 4.1 Verify Prerequisites

Before proceeding, check whether the required tools are already installed.

**On Mac — open Terminal and run:**
```bash
node --version
npm --version
newman --version
```

**On Windows — open Command Prompt and run:**
```bat
node --version
npm --version
newman --version
```

If all three commands return a version number, skip to [Section 4.4](#44-navigate-to-the-project-folder). If any command returns an error, follow the installation steps for your operating system below.

---

### 4.2 Installation on Mac

Run the following commands **in order**, one at a time.

**Step 1 — Install Homebrew**
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
Note: This command will prompt for your Mac login password. Nothing will appear on screen while you type — no asterisks, no dots. This is normal behavior. Type your password and press Enter.

**Step 2 — Install NVM** (Node Version Manager)
```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
```

**Step 3 — Reload the terminal**
```bash
source ~/.zshrc
```
If this returns an error, try `source ~/.bash_profile` instead, or close and reopen the terminal.

**Step 4 — Install Node.js**
```bash
nvm install --lts
nvm use --lts
```

**Step 5 — Verify the installation**
```bash
node --version
npm --version
```
Both commands must return a version number before continuing.

**Step 6 — Install Newman**
```bash
npm install -g newman newman-reporter-htmlextra
```

**Step 7 — Verify Newman**
```bash
newman --version
```
The command should return a version number such as `6.2.2`.

---

### 4.3 Installation on Windows

**Step 1 — Install Node.js**

- Go to **https://nodejs.org**
- Click the green **LTS** button to download the installer
- Run the downloaded `.msi` file
- Follow the installer prompts: click **Next**, accept the license agreement, leave all default options unchanged, and click **Install**
- When prompted, allow the installer to make changes to your system
- Click **Finish** when the installation completes
- **Close and reopen Command Prompt** before continuing — this is required for the new commands to be recognized

**Step 2 — Verify Node.js**

Open a new Command Prompt window and run:
```bat
node --version
npm --version
```
Both must return a version number before continuing.

**Step 3 — Install Newman**
```bat
npm install -g newman newman-reporter-htmlextra
```
This command downloads and installs Newman and the HTML report generator. It may take one to two minutes.

**Step 4 — Verify Newman**
```bat
newman --version
```
The command should return a version number such as `6.2.2`.

---

### 4.4 Navigate to the Project Folder

**On Mac:**
```bash
cd "/path/to/Part 2 – API Testing + Automation"
```
Tip: type `cd ` (with a trailing space) and drag the folder from Finder into the terminal window. The path will be filled in automatically. Press Enter.

**On Windows:**
```bat
cd "C:\path\to\Part 2 – API Testing + Automation"
```
Tip: open File Explorer, navigate to the project folder, click on the address bar at the top, and copy the full path. Then paste it into Command Prompt after `cd `.

To verify you are in the correct folder, run the following command and confirm that the `.json` files are listed:

- Mac: `ls`
- Windows: `dir`

---

### 4.5 Run the Tests

**On Mac / Linux:**

Grant execution permission to the script (first time only):
```bash
chmod +x run_tests.sh
```

Then run:
```bash
OCM_API_KEY=YOUR_API_KEY_HERE ./run_tests.sh
```

**On Windows:**
```bat
set OCM_API_KEY=YOUR_API_KEY_HERE
run_tests.bat
```

Replace `YOUR_API_KEY_HERE` with the API key obtained in Section 2.

---

### 4.6 Terminal Output During Execution

The terminal will display progress similar to the following:

```
+--------------------------------------------------------------+
|       OPPIZI – Open Charge Map API Test Automation          |
+--------------------------------------------------------------+

  API key configured
  Newman: 6.2.2
  Collection: Oppizi – Open Charge Map API Tests.postman_collection.json
  Environment: Oppizi – OCM API (Environment).postman_environment.json

Run ID    : OCM_RUN_20260614_143022
Timestamp : 2026-06-14 14:30:22

Running tests...

  POI – GET /poi/
    POI-01 – Status code is 200          PASS
    POI-02 – Response time under 1000ms  PASS
    POI-03 – Response is a JSON array    PASS
    ...

GENERATING REPORT...
  HTML report generated
```

The full run takes approximately 30 to 40 seconds.

---

### 4.7 Output Files

Two files are created automatically in the `reports/` folder after each run:

| File | Description | How to Open |
|---|---|---|
| `OCM_RUN_..._custom_report.html` | Full visual test report | Opens automatically in your browser |
| `OCM_RUN_..._results.json` | Raw run data in JSON format | Share with the team or use for CI integration |

The HTML report opens automatically in your default browser and includes:

- **Scorecard** — pass rate, total tests, passed count, failed count, duration
- **Performance** — P50, P90, P95 metrics and SLA thresholds
- **Results table** — filterable by Pass / Fail / POI / REF
- **Failure analysis** — root cause for each failure with recommendations
- **Risk register** — identified risks and action owners

A sample report is available at `reports/OCM_RUN_SAMPLE_custom_report.html`.

---

## 5. Test Cases

### 5.1 GET /poi/ — 13 Tests

| ID | Category | Description |
|---|---|---|
| POI-01 | Status | HTTP 200 response |
| POI-02 | Performance | Response time under 1000ms |
| POI-03 | Schema | Body is a JSON array |
| POI-04 | Schema | Each POI contains ID, UUID, AddressInfo, and Connections |
| POI-05 | Schema | AddressInfo contains Latitude, Longitude, and CountryID |
| POI-06 | Schema | Connections contain ID and ConnectionTypeID |
| POI-07 | Business Logic | Result count does not exceed the `maxresults` parameter |
| POI-08 | Business Logic | All stations are within the specified search radius |
| POI-09 | Business Logic | Country filter returns only stations from the specified country |
| POI-10 | Business Logic | No duplicate IDs in the response |
| POI-11 | Business Logic | All coordinates are geographically valid |
| POI-12 | Negative | Requests without an API key are rejected |
| POI-13 | Negative | Coordinates in the ocean return zero results |

### 5.2 GET /referencedata/ — 12 Tests

| ID | Category | Description |
|---|---|---|
| REF-01 | Status | HTTP 200 response |
| REF-02 | Performance | Response time under 1000ms |
| REF-03 | Schema | Body is a JSON object |
| REF-04 | Schema | Contains all 10 required catalog keys |
| REF-05 | Schema | All values are non-empty arrays |
| REF-06 | Schema | ConnectionTypes contain ID and Title |
| REF-07 | Schema | Countries contain ID and ISOCode |
| REF-08 | Business Logic | No duplicate IDs in any list |
| REF-09 | Business Logic | All ISOCodes are 2-character strings |
| REF-10 | Business Logic | At least one StatusType is marked as operational |
| REF-11 | Business Logic | All ConnectionTypeIDs referenced by POI exist in the catalog |
| REF-12 | Negative | Requests without an API key are rejected |

---

## 6. Environment Variables

The following variables can be modified in `Oppizi – OCM API (Environment).postman_environment.json` to target a different city or adjust search parameters:

| Variable | Default Value | Description |
|---|---|---|
| `apiKey` | *(empty — required)* | Your Open Charge Map API key |
| `lat` | `51.5074` | Latitude of the search center point (London) |
| `lng` | `-0.1278` | Longitude of the search center point (London) |
| `distance` | `10` | Search radius in kilometers |
| `maxresults` | `10` | Maximum number of results per request |
| `countrycode` | `GB` | ISO country code (AR = Argentina, US = United States) |

---

## 7. Troubleshooting

### `newman` is not recognized as a command

Newman is not installed or the installation did not complete successfully. Run the following:

**Mac:**
```bash
npm install -g newman newman-reporter-htmlextra
```

**Windows:**
```bat
npm install -g newman newman-reporter-htmlextra
```

If `npm` itself is not recognized, Node.js is not installed. Return to [Section 4.2](#42-installation-on-mac) (Mac) or [Section 4.3](#43-installation-on-windows) (Windows).

---

### `node` or `npm` is not recognized as a command

Node.js is not installed or the Command Prompt was not restarted after installation. Close the terminal window completely, reopen it, and run `node --version` again. If the error persists, reinstall Node.js following the steps in [Section 4.2](#42-installation-on-mac) or [Section 4.3](#43-installation-on-windows).

---

### Error: `could not load environment` or `no such file or directory`

There are two possible causes:

**Cause A — You are not in the correct directory.**
Run `ls` (Mac) or `dir` (Windows) and verify that the `.json` files are listed. If they are not, navigate to the correct directory. See [Section 4.4](#44-navigate-to-the-project-folder).

**Cause B — You are running Newman directly instead of using the provided script.**
Always use `./run_tests.sh` on Mac or `run_tests.bat` on Windows. The scripts locate all required files automatically.

If you must run Newman directly, note that file names contain special characters and spaces that require quoting:

Mac:
```bash
newman run "Oppizi – Open Charge Map API Tests.postman_collection.json" \
  --environment "Oppizi – OCM API (Environment).postman_environment.json" \
  --env-var "apiKey=YOUR_API_KEY"
```

Windows:
```bat
newman run "Oppizi – Open Charge Map API Tests.postman_collection.json" ^
  --environment "Oppizi – OCM API (Environment).postman_environment.json" ^
  --env-var "apiKey=YOUR_API_KEY"
```

---

### All tests fail with `403 Forbidden`

There are two possible causes:

**Cause A — Incorrect or expired API key.**
Verify that the key is valid and active at:
https://openchargemap.org — My Profile — My Apps

**Cause B — Corporate network or VPN is blocking the request.**
Some networks block the domain `api.openchargemap.io`. Try connecting via a personal Wi-Fi network or mobile hotspot.

---

### Error: `Permission denied: ./run_tests.sh` (Mac only)

The script does not have execution permissions. Run:
```bash
chmod +x run_tests.sh
```
This is required only once, the first time you use the script.

---

### No characters appear while typing a password in the terminal (Mac only)

This is standard security behavior on Mac. When entering a password in the terminal, nothing is displayed on screen — no asterisks, no dots, no characters of any kind. Type your password normally and press Enter.

---

### Error: `source ~/.zshrc` returns an error (Mac only)

If your Mac is configured to use bash instead of zsh, run:
```bash
source ~/.bash_profile
```
Alternatively, close and reopen the terminal window.

---

### REF tests are slow or fail on response time

The `/referencedata/` endpoint returns the full reference catalog and is significantly heavier than `/poi/`. Response times between 1000ms and 1500ms are expected. If performance failures are not relevant to your evaluation, they can be disregarded — they do not affect the functional correctness of the API.

---

### POI-12 and REF-12 receive `403` instead of the expected `401`

This is a known behavior of the Open Charge Map API gateway. The server returns `403 Forbidden` rather than `401 Unauthorized` for requests missing an API key. This is not a defect in the test suite or in the API. It is documented in the Risk Register section of the HTML report.

---

*Oppizi QA Engineering — Part 2: API Testing and Automation*
*Open Charge Map API v3*
