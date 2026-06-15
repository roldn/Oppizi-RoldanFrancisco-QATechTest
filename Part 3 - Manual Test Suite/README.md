# Oppizi – Part 3: Manual Test Suite
## Route Conflict Detection & Reassignment Auditing
---

## Table of Contents

- [Contents](#contents)
- [How to Open](#how-to-open)
- [Document Structure](#document-structure)
- [Test Case Summary](#test-case-summary)
- [Test Environment Requirements](#test-environment-requirements)
- [Execution Order](#execution-order)
- [Audit Verification Quick Reference](#audit-verification-quick-reference)
- [Related Deliverables](#related-deliverables)

---

## Contents

| File | Description |
|---|---|
| `Oppizi_Manual_Test_Suite_Part3.docx` | Full test suite document (open in Word or Google Docs) |
| `README.md` | This file |

---

## How to Open

Download `Oppizi_Manual_Test_Suite_Part3.docx` and open it in:
- **Microsoft Word** (recommended — full fidelity)
- **Google Docs** — File → Import → select the .docx file
- **LibreOffice Writer** — File → Open

---

## Document Structure

| Section | Content |
|---|---|
| **1. Test Case Index** | Summary table — all 20 test cases with ID, title, category, priority |
| **2. Detailed Test Cases** | Step-by-step test cases grouped by category |
| **3. Test Data** | Campaign/route reference table + agent reference table |
| **4. Audit & Email Verification** | Step-by-step audit API and Mailtrap verification procedures |
| **5. Sample Bug Report** | Fully populated defect report (BUG-2025-001) |
| **6. Assumptions & Risks** | 8 assumptions + 7 risk register entries |
| **7. Regression Checklist** | 10 modules with impact rating and specific regression scenarios |

---

## Test Case Summary

**20 test cases across 4 categories:**

| Category | Count | IDs |
|---|---|---|
| Functional | 5 | TC-F-01 → TC-F-05 |
| Negative | 5 | TC-N-01 → TC-N-05 |
| Edge | 5 | TC-E-01 → TC-E-05 |
| Permissions | 5 | TC-P-01 → TC-P-05 |

**Feature constraints covered:**

- Route reassignment only before campaign start date
- No overlapping schedule for receiving agent (cross-campaign)
- Location type must match (indoor/outdoor)
- Audit log entry on every reassignment attempt (success and failure)
- Confirmation email to both agents on success
- 24-hour lock after reassignment

---

## Test Environment Requirements

- **Auth:** Manager account (`manager@oppizi.com`), super-admin account, read-only manager account, field agent accounts
- **Email sink:** [Mailtrap](https://mailtrap.io) or [Mailhog](https://github.com/mailhog/MailHog) — configure SMTP in the test environment to redirect all outbound email
- **Audit API:** `GET /v1/audit?routeId=<id>` accessible with manager credentials
- **Test data:** Seed campaigns, routes, and agents as specified in Section 3 before executing the suite
- **Clock control:** TC-E-01 requires either a test-clock API or pre-seeded campaign data with start time set to the exact test execution time

---

## Execution Order

Run test cases in this sequence to minimise state dependencies:

1. **TC-F-01** first — creates the reassignment state that TC-F-02, TC-F-03, TC-F-04 depend on
2. **TC-N-** cases — can run independently, no shared state
3. **TC-E-02** — run in isolation, requires a clean route with no prior lock
4. **TC-P-** cases — run with separate browser sessions per role
5. **TC-F-05** — requires pre-seeded data aged 24 h + 1 min (use seeded DB snapshot)

---

## Audit Verification Quick Reference

```
GET /v1/audit?routeId=R-01&limit=1
Authorization: Bearer <manager_token>

Expected response:
{
  "routeId": "R-01",
  "campaignId": "campaign-alpha",
  "fromAgentId": "<uuid>",
  "toAgentId": "<uuid>",
  "managerId": "<uuid>",
  "action": "REASSIGN",
  "timestamp": "2025-01-15T09:00:00.000Z"
}
```

---

## Related Deliverables

- **Part 1:** System journey diagrams (`/part1/`)
- **Part 2:** Postman API test collection (`/part2/`)
