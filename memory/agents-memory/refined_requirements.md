# Universal Extension Requirements (Refined)

**Extension Name:** Servicenow Cmdb (`servicenow-cmdb`)
**Original Generated:** Not specified in source requirements
**Refined:** 2026-09-11
**Agent_id:** Not specified
**Requirements Completeness:** High Detail
**Target Platform:** Linux (x86_64)

---

# Table of Contents

1. [Overview](#overview)
2. [Actions](#actions)
   - 2.1 [Action 1: Create Incident](#action-1-create-incident)
   - 2.2 [Action 2: Update Incident](#action-2-update-incident)
   - 2.3 [Action 3: Update RITM](#action-3-update-ritm)
   - 2.4 [Action 4: Create/Update CI](#action-4-createupdate-ci)
   - 2.5 [Action 5: Get CI](#action-5-get-ci)
3. [Input Requirements](#input-requirements)
   - 3.1 [Connection Parameters](#31-connection-parameters)
   - 3.2 [Action Selection](#32-action-selection)
   - 3.3 [Create Incident Fields](#33-create-incident-fields)
   - 3.4 [Update Incident Fields](#34-update-incident-fields)
   - 3.5 [Update RITM Fields](#35-update-ritm-fields)
   - 3.6 [Create/Update CI Fields](#36-createupdate-ci-fields)
   - 3.7 [Get CI Fields](#37-get-ci-fields)
4. [Output Requirements](#output-requirements)
   - 4.1 [On Success](#41-on-success)
   - 4.2 [On Error](#42-on-error)
5. [Authentication Requirements](#authentication-requirements)
6. [Environment Variables](#environment-variables)
7. [Operational Behavior](#operational-behavior)
8. [Implementation Notes](#implementation-notes)
   - 8.1 [Python Compatibility](#81-python-compatibility)
   - 8.2 [Target Platform](#82-target-platform)
   - 8.3 [Third-Party Services and Tools](#83-third-party-services-and-tools)
   - 8.4 [Error Handling](#84-error-handling)
   - 8.5 [Resource Cleanup](#85-resource-cleanup)
9. [Requirements Summary](#requirements-summary)
10. [Document Change History](#document-change-history)
11. [References](#references)

---

# Overview

This document defines the complete requirements for the **Servicenow Cmdb** Universal Extension — a Stonebranch UAC integration that provides five ServiceNow automation actions: Create Incident, Update Incident, Update RITM, Create/Update CI, and Get CI.

**Integration Purpose:** Enable Stonebranch UAC workflows to interact with ServiceNow for IT service management and CMDB operations. The primary CMDB use case is post-provisioning registration — after a VM or other resource is created by Stonebranch, its details are written into the ServiceNow CMDB using the Identification and Reconciliation Engine (IRE) to prevent duplicate Configuration Items. The integration also supports standard Incident and RITM lifecycle management, and CI retrieval to expose CMDB attributes as downstream workflow variables.

---

# Actions

## Action 1: Create Incident

**Functional Requirements:**

1. The extension must create a new Incident record in ServiceNow using the Table API endpoint `POST /api/now/table/incident`.
2. The action must accept standard ServiceNow Incident fields as input (short description, description, category, priority, urgency, impact, assignment group, caller, and assigned to).
3. On success, the extension must expose the created Incident's `sys_id` and `number` as task output fields.
4. The action must not expose ServiceNow authentication credentials in logs or output.

---

## Action 2: Update Incident

**Functional Requirements:**

1. The extension must update an existing Incident record in ServiceNow using the Table API endpoint `PUT /api/now/table/incident/{sys_id}`.
2. The action must accept the target Incident's `sys_id` as a required input to identify the record to update.
3. The action must accept standard ServiceNow Incident fields as input for the fields to update.
4. On success, the extension must confirm the updated Incident's `sys_id` and `number` as task output fields.
5. The action must not expose ServiceNow authentication credentials in logs or output.

---

## Action 3: Update RITM

**Functional Requirements:**

1. The extension must update an existing Request Item (RITM) record in ServiceNow using the Table API endpoint `PUT /api/now/table/sc_req_item/{sys_id}`.
2. The action must accept the target RITM's `sys_id` as a required input to identify the record to update.
3. The action must accept standard ServiceNow RITM fields as input for the fields to update.
4. On success, the extension must confirm the updated RITM's `sys_id` and `number` as task output fields.
5. The action must not expose ServiceNow authentication credentials in logs or output.

---

## Action 4: Create/Update CI

**Functional Requirements:**

1. The extension must create or update a Configuration Item (CI) in ServiceNow CMDB using the Identification and Reconciliation Engine (IRE) endpoint `POST /api/now/identifyreconcile`.
2. The action must NOT use direct Table API writes (`POST /api/now/table/cmdb_ci_*`) for CI creation or update; IRE must be used exclusively to prevent duplicate CIs.
3. The extension must allow ServiceNow IRE to determine whether to INSERT a new CI or UPDATE an existing CI based on identification rules.
4. The CI class must be selectable from a dynamically populated list of available CMDB classes (see Section 3.6).
5. The CI attributes must be provided as a variable-length list of key-value pairs, where values may contain Stonebranch workflow variable references (e.g., `${ops_var_vm_name}`).
6. Empty attribute values (`null`, `""`, `[]`, `{}`) must be excluded from the IRE payload before submission.
7. The extension must parse the IRE response and expose the operation result as task output fields: `cmdb_action`, `cmdb_sys_id`, `cmdb_class`, `cmdb_name`, `cmdb_status`.
8. The `cmdb_action` output field must reflect the IRE operation outcome: `CREATED`, `UPDATED`, or `MATCHED`.
9. If ServiceNow IRE returns identification or reconciliation errors, the original ServiceNow error message must be preserved and exposed — not replaced with a generic error.
10. The Discovery Source field must be included in the IRE payload when provided by the user.

**IRE Payload Structure:**

The extension must build the IRE payload dynamically with the following structure:

```json
{
  "items": [
    {
      "className": "<selected_ci_class>",
      "values": {
        "<attribute_name>": "<attribute_value>",
        "<attribute_name>": "<attribute_value>"
      }
    }
  ]
}
```

- `className` must come from the selected CI Class field value (e.g., `cmdb_ci_vm_instance`).
- The `values` object must be built dynamically from the provided attribute key-value pairs.
- Attributes with empty values must be excluded from the payload.

---

## Action 5: Get CI

**Functional Requirements:**

1. The extension must retrieve one or more Configuration Items from ServiceNow CMDB using the Table API endpoint `GET /api/now/table/{ci_class}`.
2. The action must support three search modes selectable by the user: by Name, by Sys ID, and by Custom Query.
3. When searching by Name, the extension must query using `sysparm_query=name=<value>`.
4. When searching by Sys ID, the extension must query using `sysparm_query=sys_id=<value>`.
5. When searching by Custom Query, the extension must pass the user-provided value directly as `sysparm_query`.
6. The extension must limit the number of returned results using the `sysparm_limit` parameter.
7. The extension must control which CI fields are returned using the `sysparm_fields` parameter.
8. When Return Fields is empty, the extension must default to returning the following field set: `sys_id, name, ip_address, operational_status, cpu_count, ram, os, short_description`.
9. When no CI matches the search criteria, the task must fail with return code 1 and a `NOT_FOUND_ERROR` status.
10. When exactly one CI is returned, the requested fields must be exposed as individual task output fields (`cmdb_sys_id`, `cmdb_name`, etc.) and the full CI object must be exposed as `cmdb_result_json`.
11. When multiple CIs are returned, individual output fields must be populated from the first result, `cmdb_result_json` must contain the first result, and `cmdb_results_json` must contain the complete array of all results.
12. When multiple CIs are returned, STDOUT must include the note: `"Returning N results. Individual output fields reflect the first result. Full results in cmdb_results_json."`
13. ServiceNow authentication credentials must never appear in CI output or logs.

---

# Input Requirements

## 3.1 Connection Parameters

- **ServiceNow Instance URL** (Text, Required): The base URL of the ServiceNow instance.
  - Example: `https://myinstance.service-now.com`
  - Applicability: All actions

- **Credential** (Credential, Required): UAC credential containing the ServiceNow username (`user` attribute) and password (`password` attribute) for Basic Authentication.
  - Applicability: All actions

---

## 3.2 Action Selection

- **Action** (Choice, Required): Selects which ServiceNow operation to perform. Controls which fields are shown in the task form.
  - Available options:
    - `Create Incident`
    - `Update Incident`
    - `Update RITM`
    - `Create/Update CI`
    - `Get CI`
  - Default presented option: `Create Incident`
  - Each option shows only the fields relevant to that action (all other action-specific fields are hidden).

---

## 3.3 Create Incident Fields

Shown only when Action = `Create Incident`.

- **Short Description** (Text, Required): Brief summary of the Incident.
  - Example: `Application server APP-PROD-01 is unreachable`
  - Applicability: Create Incident

- **Description** (Plain Text, Optional): Detailed description of the Incident.
  - Applicability: Create Incident

- **Category** (Text, Optional): Incident category.
  - Example: `Software`
  - Applicability: Create Incident

- **Priority** (Text, Optional): Incident priority.
  - Example: `2`
  - Applicability: Create Incident

- **Urgency** (Text, Optional): Incident urgency.
  - Applicability: Create Incident

- **Impact** (Text, Optional): Incident impact.
  - Applicability: Create Incident

- **Caller** (Text, Optional): ServiceNow user ID or name of the caller.
  - Applicability: Create Incident

- **Assignment Group** (Text, Optional): ServiceNow assignment group name or sys_id.
  - Applicability: Create Incident

- **Assigned To** (Text, Optional): ServiceNow user to whom the Incident is assigned.
  - Applicability: Create Incident

---

## 3.4 Update Incident Fields

Shown only when Action = `Update Incident`.

- **Incident Sys ID** (Text, Required): The `sys_id` of the Incident to update.
  - Example: `abc123def456abc123def456abc123de`
  - Applicability: Update Incident

- **Fields to Update** (Plain Text, Optional): One or more ServiceNow Incident field values to update. Standard ServiceNow Incident fields apply.
  - Applicability: Update Incident

---

## 3.5 Update RITM Fields

Shown only when Action = `Update RITM`.

- **RITM Sys ID** (Text, Required): The `sys_id` of the Request Item to update.
  - Example: `abc123def456abc123def456abc123de`
  - Applicability: Update RITM

- **Fields to Update** (Plain Text, Optional): One or more ServiceNow RITM field values to update. Standard ServiceNow sc_req_item fields apply.
  - Applicability: Update RITM

---

## 3.6 Create/Update CI Fields

Shown only when Action = `Create/Update CI`.

- **CI Class** (Dynamic Choice, Required): The ServiceNow CMDB table/class name for the CI.
  - Dynamically populated by querying ServiceNow for all tables whose name begins with `cmdb_ci`.
  - Display format: `<Label> (<table_name>)` — e.g., `VM Instance (cmdb_ci_vm_instance)`, `Server (cmdb_ci_server)`, `Computer (cmdb_ci_computer)`.
  - The value sent to ServiceNow (used in the IRE payload `className`) must be the actual table name (e.g., `cmdb_ci_vm_instance`), not the display label.
  - Applicability: Create/Update CI

- **CI Name** (Text, Required): The name of the Configuration Item.
  - Example: `${ops_var_vm_name}` or `APP-PROD-01`
  - Applicability: Create/Update CI

- **Attributes** (Array Field, Optional): Variable-length list of CI attribute key-value pairs to include in the IRE payload.
  - Column 1 title: `Attribute Name` — the ServiceNow CI field name (e.g., `ip_address`, `cpu_count`, `ram`).
  - Column 2 title: `Attribute Value` — the value for that field; may contain Stonebranch variable references (e.g., `${ops_var_vm_ip}`).
  - Example rows:
    | Attribute Name | Attribute Value      |
    |----------------|----------------------|
    | name           | ${ops_var_vm_name}   |
    | ip_address     | ${ops_var_vm_ip}     |
    | cpu_count      | ${ops_var_vm_cpu}    |
    | ram            | ${ops_var_vm_ram}    |
    | os             | ${ops_var_vm_os}     |
  - Applicability: Create/Update CI

- **Data Source / Discovery Source** (Text, Optional): The discovery source identifier sent to ServiceNow IRE to identify which system is creating or updating the CI. Used by ServiceNow CMDB reconciliation rules to determine attribute authority.
  - Default Value: `Stonebranch`
  - Example: `Stonebranch`, `ServiceNow Discovery`, `SCCM`
  - Applicability: Create/Update CI

---

## 3.7 Get CI Fields

Shown only when Action = `Get CI`.

- **CI Class** (Dynamic Choice, Required): The ServiceNow CMDB table/class to query.
  - Dynamically populated identically to the Create/Update CI action's CI Class field.
  - Display format: `<Label> (<table_name>)`.
  - Applicability: Get CI

- **Search By** (Choice, Required): The search mode used to locate CI records.
  - Available options:
    - `Name` — queries `sysparm_query=name=<Search Value>`
    - `Sys ID` — queries `sysparm_query=sys_id=<Search Value>`
    - `Custom Query` — passes `<Search Value>` directly as `sysparm_query`
  - Default presented option: `Name`
  - Applicability: Get CI

- **Search Value** (Text, Required): The value used with the selected Search By mode.
  - Example (Name): `APP-PROD-01`
  - Example (Sys ID): `abc123def456abc123def456abc123de`
  - Example (Custom Query): `operational_status=1^ip_address=10.10.20.15`
  - Applicability: Get CI

- **Return Fields** (Text, Optional): Comma-separated list of ServiceNow CI field names to include in the response. Passed as `sysparm_fields` to the Table API.
  - Example: `sys_id,name,ip_address,operational_status,cpu_count,ram`
  - Default behavior when empty: returns the standard field set — `sys_id, name, ip_address, operational_status, cpu_count, ram, os, short_description`.
  - Field hint must document: `"Comma-separated CI fields to return. Default: sys_id, name, ip_address, operational_status, cpu_count, ram, os, short_description"`
  - Applicability: Get CI

- **Limit** (Integer, Optional): Maximum number of CI records to return. Passed as `sysparm_limit`.
  - Default Value: `1`
  - Applicability: Get CI

---

# Output Requirements

## 4.1 On Success

### Action 1: Create Incident — Success

- **Return code:** `0`
- **Status description:** `"Incident <number> created successfully"`
- **Output fields:**
  - `incident_sys_id` (Text): The `sys_id` of the created Incident record.
  - `incident_number` (Text): The Incident number (e.g., `INC0010001`).
- **STDOUT output:** ASCII table (`rounded_outline` format) showing the created Incident's key fields.
- **Success Criteria:**
  1. ServiceNow responds with HTTP 200 or 201.
  2. The response body contains a valid `sys_id` and `number`.
  3. The `incident_sys_id` and `incident_number` output fields are populated.

### Action 2: Update Incident — Success

- **Return code:** `0`
- **Status description:** `"Incident <number> updated successfully"`
- **Output fields:**
  - `incident_sys_id` (Text): The `sys_id` of the updated Incident record.
  - `incident_number` (Text): The Incident number.
- **STDOUT output:** ASCII table (`rounded_outline` format) confirming the updated Incident.
- **Success Criteria:**
  1. ServiceNow responds with HTTP 200.
  2. The response body confirms the updated record.
  3. The `incident_sys_id` and `incident_number` output fields are populated.

### Action 3: Update RITM — Success

- **Return code:** `0`
- **Status description:** `"RITM <number> updated successfully"`
- **Output fields:**
  - `ritm_sys_id` (Text): The `sys_id` of the updated RITM record.
  - `ritm_number` (Text): The RITM number (e.g., `RITM0010001`).
- **STDOUT output:** ASCII table (`rounded_outline` format) confirming the updated RITM.
- **Success Criteria:**
  1. ServiceNow responds with HTTP 200.
  2. The response body confirms the updated record.
  3. The `ritm_sys_id` and `ritm_number` output fields are populated.

### Action 4: Create/Update CI — Success

- **Return code:** `0`
- **Status description:** `"CI <cmdb_action>: <cmdb_name> (<cmdb_class>)"`
- **Output fields:**
  - `cmdb_action` (Text): The IRE operation outcome — `CREATED`, `UPDATED`, or `MATCHED`.
  - `cmdb_sys_id` (Text): The `sys_id` of the created or updated CI.
  - `cmdb_class` (Text): The CI class name (e.g., `cmdb_ci_vm_instance`).
  - `cmdb_name` (Text): The CI name.
  - `cmdb_status` (Text): The overall status of the IRE operation.
- **STDOUT output:** ASCII table (`rounded_outline` format) showing the IRE operation result fields.
- **Success Criteria:**
  1. ServiceNow IRE responds with HTTP 200.
  2. The response body contains a valid `sys_id` and operation status.
  3. All five `cmdb_*` output fields are populated.
  4. The original ServiceNow error message is preserved if IRE returns error details.

### Action 5: Get CI — Success

**Single result:**
- **Return code:** `0`
- **Status description:** `"CI found: <cmdb_name> (<cmdb_class>)"`
- **Output fields:**
  - `cmdb_sys_id` (Text): CI `sys_id`.
  - `cmdb_name` (Text): CI name.
  - Additional fields dynamically based on the `Return Fields` parameter or the default field set (e.g., `cmdb_ip_address`, `cmdb_operational_status`, `cmdb_cpu_count`, `cmdb_ram`, `cmdb_os`, `cmdb_short_description`). Field names are prefixed with `cmdb_`.
  - `cmdb_result_json` (Text): Complete CI record as a sanitized JSON string.
- **STDOUT output:** ASCII table (`rounded_outline` format) showing the returned CI attributes.
- **Success Criteria:**
  1. ServiceNow Table API responds with HTTP 200.
  2. Exactly one CI record is returned.
  3. All requested output fields are populated.
  4. `cmdb_result_json` contains the full CI record.

**Multiple results:**
- **Return code:** `0`
- **Status description:** `"<N> CIs found. First result shown in output fields."`
- **Output fields:**
  - Individual `cmdb_*` fields populated from the **first** result in the response.
  - `cmdb_result_json` (Text): The first CI record as a sanitized JSON string.
  - `cmdb_results_json` (Text): All returned CI records as a sanitized JSON array string.
- **STDOUT output:** ASCII table for the first result with a note: `"Returning N results. Individual output fields reflect the first result. Full results in cmdb_results_json."`
- **Success Criteria:**
  1. ServiceNow Table API responds with HTTP 200.
  2. More than one CI record is returned.
  3. Individual output fields reflect the first result.
  4. `cmdb_results_json` contains the complete array.

**No results:**
- **Return code:** `1`
- **Status description:** `"Not Found: No CI found for [<search_by>: <search_value>]"`
- **Output fields:** All `cmdb_*` output fields are empty.
- **STDOUT output:** `"No CI found matching search criteria."`
- See Section 4.2 for `NOT_FOUND_ERROR` details.

---

## 4.2 On Error

**Failure Scenarios:**

| Scenario | Description | Root Causes | Return Code | Status Description Pattern |
|----------|-------------|-------------|-------------|---------------------------|
| `AUTHENTICATION_ERROR` | ServiceNow rejected the credentials | Invalid username or password; HTTP 401 response | `1` | `"Authentication Error: Invalid ServiceNow credentials"` |
| `AUTHORIZATION_ERROR` | Credentials are valid but lack permission | Insufficient ServiceNow role; HTTP 403 response | `1` | `"Authorization Error: Insufficient permissions for this operation"` |
| `CONNECTION_ERROR` | Cannot reach the ServiceNow instance | Network failure, DNS resolution failure, SSL error, timeout | `1` | `"Connection Error: Unable to reach ServiceNow instance at <url>"` |
| `SERVICENOW_VALIDATION_ERROR` | ServiceNow rejected the request payload | Invalid field value, mandatory field missing, invalid table name; HTTP 400 response | `1` | `"Validation Error: <ServiceNow error detail>"` |
| `SERVICENOW_BUSINESS_RULE_ERROR` | ServiceNow business rule blocked the operation | Business rule condition triggered; HTTP 400 or 422 response | `1` | `"Business Rule Error: <ServiceNow error detail>"` |
| `NOT_FOUND_ERROR` | No record matched the search criteria | No CI matched name/sys_id/custom query; Get CI returned zero results | `1` | `"Not Found: No CI found for [<search_by>: <search_value>]"` |
| `CMDB_IDENTIFICATION_ERROR` | ServiceNow IRE could not identify the CI | IRE identification rule failure, ambiguous match | `1` | `"CMDB Identification Error: <ServiceNow IRE error detail>"` |
| `CMDB_RECONCILIATION_ERROR` | ServiceNow IRE reconciliation failed | Attribute reconciliation conflict, invalid discovery source | `1` | `"CMDB Reconciliation Error: <ServiceNow IRE error detail>"` |

**Error handling rules:**
- The original ServiceNow error message must always be preserved in the status description and STDERR; no error may be replaced with a generic message.
- Credentials (passwords, OAuth tokens, Authorization headers, client secrets) must never appear in STDERR, STDOUT, or output fields.
- All errors use return code `1`.

**Input Validation:**
- Input validation errors use return code `2`.
- The CI Class field must be validated as non-empty for Create/Update CI and Get CI.
- The CI Name field must be validated as non-empty for Create/Update CI.
- The Search Value field must be validated as non-empty for Get CI.
- The Incident Sys ID field must be validated as non-empty for Update Incident.
- The RITM Sys ID field must be validated as non-empty for Update RITM.

---

# Authentication Requirements

All ServiceNow API calls must use **HTTP Basic Authentication**. A single UAC Credential field provides both the username and password:

- The `user` attribute of the credential provides the ServiceNow username.
- The `password` attribute of the credential provides the ServiceNow password.

Basic Auth credentials are sent on every request via the HTTP `Authorization` header. The extension must never log, print, or expose the credential values. All ServiceNow connections must use HTTPS.

---

# Environment Variables

- **`UE_HTTP_TIMEOUT`** (Integer, default: `30`): HTTP request timeout in seconds applied to all ServiceNow API calls. Set at the UAC Agent level, Business Service level, or individual task definition level. If not set, the extension defaults to 30 seconds. This variable is not exposed as a template field.

---

# Operational Behavior

**Dynamic Choice Fields:**
The CI Class field is a dynamic choice on both Create/Update CI and Get CI actions. When the user opens the dropdown, the extension queries ServiceNow for all tables whose name begins with `cmdb_ci` and returns them as selectable options. The display label format is `<Human Label> (<table_name>)` (e.g., `VM Instance (cmdb_ci_vm_instance)`). The value passed to ServiceNow in API calls is the raw table name (e.g., `cmdb_ci_vm_instance`).

**Cancel Action:**
Standard UAC task cancellation behavior applies. No special cancel handling is required beyond what the UAC framework provides.

**Re-run Capability:**
The extension supports task re-run via standard UAC mechanisms. For Create/Update CI, re-running the same task will trigger IRE again; ServiceNow IRE will UPDATE the existing CI rather than CREATE a duplicate, provided the CI attributes match the identification rules.

**Progress Reporting:**
The extension must write operation progress and results to STDOUT using ASCII tables in `rounded_outline` format (via `tabulate` library). Log messages must be clear and actionable.

**Dynamic Commands:**
No dynamic commands are required beyond the CI Class dynamic choice field population.

---

# Implementation Notes

## 8.1 Python Compatibility

Targeting compatibility for Python `>= 3.11` as specified in the extension configuration (`extension.yml`).

## 8.2 Target Platform

Target UAC agent platform: **Linux (x86_64)**.

C extension modules with a confirmed `manylinux_2_17_x86_64` wheel are viable in addition to pure-Python modules. All dependencies used in this extension are pure-Python and have no platform-specific wheel requirements.

## 8.3 Third-Party Services and Tools

**ServiceNow REST API**
- ServiceNow is the target external service for all integration actions.
- API minimum version: Tokyo (the IRE endpoint `POST /api/now/identifyreconcile` must be available).
- Integration approach: All calls use ServiceNow REST API over HTTPS with Basic Authentication.
- Endpoints used:
  - `POST /api/now/table/incident` — Create Incident
  - `PUT /api/now/table/incident/{sys_id}` — Update Incident
  - `PUT /api/now/table/sc_req_item/{sys_id}` — Update RITM
  - `POST /api/now/identifyreconcile` — Create/Update CI via IRE
  - `GET /api/now/table/{ci_class}` — Get CI
  - `GET /api/now/table/cmdb_metadata` or equivalent — Dynamic CI Class population (tables starting with `cmdb_ci`)

**Python dependency: `requests==2.34.2`**
- Purpose: HTTP client for all ServiceNow REST API calls.
- Type: Pure Python — no platform wheel constraint.
- Handles: Basic Auth headers, SSL/TLS, HTTP timeouts, response parsing.

**Python dependency: `tabulate==0.10.0`**
- Purpose: ASCII table formatting for STDOUT output using `tablefmt="rounded_outline"`.
- Type: Pure Python — no platform wheel constraint.

## 8.4 Error Handling

**Error categories:**
- Connection errors (network, DNS, SSL, timeout) → `CONNECTION_ERROR`
- Authentication failures (HTTP 401) → `AUTHENTICATION_ERROR`
- Authorization failures (HTTP 403) → `AUTHORIZATION_ERROR`
- Payload/field validation failures (HTTP 400) → `SERVICENOW_VALIDATION_ERROR` or `SERVICENOW_BUSINESS_RULE_ERROR`
- Not found (zero results from Get CI) → `NOT_FOUND_ERROR`
- IRE identification failures → `CMDB_IDENTIFICATION_ERROR`
- IRE reconciliation failures → `CMDB_RECONCILIATION_ERROR`

**Error handling strategy:**
- The original ServiceNow error detail must be preserved in all error responses.
- Errors must never be silently ignored.
- Credentials must never appear in error output.
- HTTP 400 responses from IRE must be inspected to distinguish business rule errors from validation errors from CMDB-specific errors.

## 8.5 Resource Cleanup

**Cleanup scenarios:**
- HTTP connections: The `requests` library session must be closed after each task execution to release connection resources.
- No temporary files or persistent state are created by the extension.

**Strategy:** All cleanup must occur at task completion, whether success or failure.

---

# Requirements Summary

| # | Requirement Area | Key Decision |
|---|-----------------|--------------|
| 1 | Action scope | All 5 actions implemented from scratch: Create Incident, Update Incident, Update RITM, Create/Update CI, Get CI |
| 2 | Authentication | HTTP Basic Auth via single UAC Credential field (username + password) |
| 3 | HTTP library | `requests==2.34.2` (pure Python, UAC-recommended) |
| 4 | CI Attributes input | Array Field with columns "Attribute Name" and "Attribute Value" |
| 5 | Data Source field | Text field with default value `Stonebranch` |
| 6 | Get CI — no results | Fail (rc=1) with `NOT_FOUND_ERROR` |
| 7 | Get CI — multiple results | Individual fields from first result + `cmdb_results_json` for all; STDOUT note indicating N results |
| 8 | Get CI — empty Return Fields | Default field set: `sys_id, name, ip_address, operational_status, cpu_count, ram, os, short_description` |
| 9 | STDOUT format | ASCII table using `tabulate==0.10.0` with `tablefmt="rounded_outline"` |
| 10 | HTTP timeout | `UE_HTTP_TIMEOUT` environment variable, default 30 seconds |
| 11 | Create/Update CI API | IRE endpoint `POST /api/now/identifyreconcile` exclusively — no direct Table API writes |
| 12 | CI Class field | Dynamic choice — all CMDB tables beginning with `cmdb_ci`, displayed as `<Label> (<table_name>)` |
| 13 | Empty attribute filtering | Empty values excluded from IRE payload before submission |
| 14 | Error taxonomy | 8 categories: `AUTHENTICATION_ERROR`, `AUTHORIZATION_ERROR`, `SERVICENOW_BUSINESS_RULE_ERROR`, `SERVICENOW_VALIDATION_ERROR`, `NOT_FOUND_ERROR`, `CONNECTION_ERROR`, `CMDB_IDENTIFICATION_ERROR`, `CMDB_RECONCILIATION_ERROR` |
| 15 | Platform | Linux (x86_64) — `manylinux_2_17_x86_64` wheels viable |
| 16 | Python version | `>= 3.11` |

---

# Document Change History

- **2026-09-11 (date of original requirements):** Initial requirements — High Detail. Covered CMDB actions (Create/Update CI, Get CI) with IRE API, input/output fields, error taxonomy, and UI visibility rules. Incident/RITM referenced as existing functionality.
- **2026-09-11:** Comprehensive refinement based on 10 clarification questions and user feedback. Decisions captured: all 5 actions implemented from scratch; Basic Auth; `requests==2.34.2`; Array Field for CI attributes; Text field with default for Discovery Source; Get CI no-result behavior (fail rc=1); Get CI multi-result individual field population from first result; default Return Fields set; tabulate ASCII table STDOUT; `UE_HTTP_TIMEOUT` environment variable.

---

# References

- Original Requirements Document: `memory/requirements.md`
- Original Requirements Q&A Document: `memory/agents-memory/requirements-QnA.md`
