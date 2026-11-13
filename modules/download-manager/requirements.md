---
module: download-manager
version: 1.1.0
---

# Download Manager — Product Spec

> Dummy content. This spec exists to test the shared specs pipeline. It is not a real requirement set.

## 1. Summary

A reusable module that downloads files to the device so they can be used offline, and reports progress to the host.

## 2. Requirements

| Rule | Requirement |
| ---- | ----------- |
| RULE-DOWNLOAD-START-001 | The module shall start a download for a file location supplied by the host. |
| RULE-DOWNLOAD-PROG-001 | The module shall report download progress to the host as a percentage. |
| RULE-DOWNLOAD-CTRL-001 | The host shall be able to pause, resume and cancel a download. |
| RULE-DOWNLOAD-DONE-001 | When a download finishes, the module shall tell the host where the file is stored on the device. |
| RULE-DOWNLOAD-ERR-001 | If a download fails, the module shall tell the host the failure reason and keep any partial progress for resume. |

## 3. Acceptance Scenarios

**Scenario 1 — Download a file**
GIVEN the host supplies a reachable file location
WHEN the host starts the download
THEN progress is reported as a percentage
AND when it finishes, the host is told where the file is stored
Covers: RULE-DOWNLOAD-START-001, RULE-DOWNLOAD-PROG-001, RULE-DOWNLOAD-DONE-001

**Scenario 2 — Pause, resume and cancel**
GIVEN a download is in progress
WHEN the host pauses, then resumes, then cancels it
THEN the download stops, continues and ends in turn
Covers: RULE-DOWNLOAD-CTRL-001

**Scenario 3 — Failure**
GIVEN the network drops during a download
WHEN the download fails
THEN the host is told the reason
AND the partial progress is kept so the download can resume
Covers: RULE-DOWNLOAD-ERR-001
