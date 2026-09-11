<!-- generated: 2026-09-11T00:00:00 -->

# Fields Analysis — Universal Extension v1.0.0

> Source: `template.json` (canonical). `fields.yml` is present but empty — all field definitions are in `template.json`.

## Complete Field Table

| # | name | label | fieldType | fieldMapping | required | requireIfVisible | showIfField | showIfFieldValue | requireIfField | requireIfFieldValue | fieldRestriction | hint |
|---|------|-------|-----------|--------------|----------|-----------------|-------------|-----------------|----------------|---------------------|-----------------|------|
| 0 | action | Action | Choice | Choice Field 1 | false | false | — | — | — | — | No Restriction | Select the ServiceNow operation to perform. |
| 1 | instance_url | Instance URL | Text | Text Field 1 | true | false | — | — | — | — | No Restriction | Base URL of the ServiceNow instance (e.g. https://myinstance.service-now.com). Must begin with https:// and must not include a trailing slash. |
| 2 | credential | Credential | Credential | Credential Field 1 | true | false | — | — | — | — | No Restriction | UAC Credential providing the ServiceNow username (user) and password for Basic Auth. |
| 3 | short_description | Short Description | Text | Text Field 2 | false | true | Choice Field 1 | Create Incident | — | — | No Restriction | Brief one-line summary of the Incident. Maps to ServiceNow short_description. |
| 4 | description | Description | Text | Large Text Field 1 | false | false | Choice Field 1 | Create Incident | — | — | No Restriction | Detailed multi-line description of the Incident. Maps to ServiceNow description. |
| 5 | category | Category | Text | Text Field 3 | false | false | Choice Field 1 | Create Incident | — | — | No Restriction | Incident category. Maps to ServiceNow category (e.g. Software). |
| 6 | priority | Priority | Text | Text Field 4 | false | false | Choice Field 1 | Create Incident | — | — | No Restriction | Incident priority. Maps to ServiceNow priority (e.g. 2). |
| 7 | urgency | Urgency | Text | Text Field 5 | false | false | Choice Field 1 | Create Incident | — | — | No Restriction | Incident urgency. Maps to ServiceNow urgency (e.g. 2). |
| 8 | impact | Impact | Text | Text Field 6 | false | false | Choice Field 1 | Create Incident | — | — | No Restriction | Incident impact. Maps to ServiceNow impact (e.g. 2). |
| 9 | caller | Caller | Text | Text Field 7 | false | false | Choice Field 1 | Create Incident | — | — | No Restriction | ServiceNow user ID or display name of the person reporting the Incident. Maps to caller_id. |
| 10 | assignment_group | Assignment Group | Text | Text Field 8 | false | false | Choice Field 1 | Create Incident | — | — | No Restriction | ServiceNow assignment group name or sys_id. Maps to assignment_group. |
| 11 | assigned_to | Assigned To | Text | Text Field 9 | false | false | Choice Field 1 | Create Incident | — | — | No Restriction | ServiceNow user to whom the Incident is assigned. Maps to assigned_to. |
| 12 | incident_sys_id | Incident Sys ID | Text | Text Field 10 | false | true | Choice Field 1 | Update Incident | — | — | No Restriction | The sys_id of the Incident to update. Required when action is Update Incident. |
| 13 | incident_fields_to_update | Incident Fields to Update | Text | Large Text Field 2 | false | false | Choice Field 1 | Update Incident | — | — | No Restriction | JSON object of Incident field name-value pairs to update. Leave empty to touch the record without changes. |
| 14 | ritm_sys_id | RITM Sys ID | Text | Text Field 11 | false | true | Choice Field 1 | Update RITM | — | — | No Restriction | The sys_id of the Request Item (RITM) to update. |
| 15 | ritm_fields_to_update | RITM Fields to Update | Text | Large Text Field 3 | false | false | Choice Field 1 | Update RITM | — | — | No Restriction | JSON object of RITM field name-value pairs to update. Leave empty to touch the record without changes. |
| 16 | ci_class | CI Class | Choice (Dynamic) | Choice Field 2 | false | false | Choice Field 1 | Create/Update CI,Get CI | — | — | No Restriction | CMDB table/class for the CI. Click refresh to load available classes from ServiceNow. Format: Label (table_name). |
| 17 | ci_name | CI Name | Text | Text Field 12 | false | true | Choice Field 1 | Create/Update CI | — | — | No Restriction | Name of the Configuration Item to create or update. Accepts Stonebranch variable references. |
| 18 | attributes | Attributes | Array | Array Field 1 | false | false | Choice Field 1 | Create/Update CI | — | — | No Restriction | Additional CI attribute key-value pairs for the IRE payload. Entries with empty values are excluded. |
| 19 | data_source | Data Source | Text | Text Field 13 | false | false | Choice Field 1 | Create/Update CI | — | — | No Restriction | Discovery source identifier sent to ServiceNow IRE (e.g. Stonebranch). Default value: Stonebranch. |
| 20 | search_by | Search By | Choice | Choice Field 3 | false | false | Choice Field 1 | Get CI | — | — | No Restriction | Determines the search mode: by Name, by Sys ID, or by a custom encoded query string. Default: Name. |
| 21 | search_value | Search Value | Text | Text Field 14 | false | true | Choice Field 1 | Get CI | — | — | No Restriction | Value used with the selected search mode: exact name, sys_id, or raw encoded query string. |
| 22 | return_fields | Return Fields | Text | Text Field 15 | false | false | Choice Field 1 | Get CI | — | — | No Restriction | Comma-separated CI field names for sysparm_fields. Leave empty for defaults: sys_id,name,ip_address,operational_status,cpu_count,ram,os,short_description. |
| 23 | limit | Limit | Integer | Integer Field 1 | false | false | Choice Field 1 | Get CI | — | — | No Restriction | Maximum number of CI records to return (1–10000). Default: 1. |
| 24 | incident_number | Incident Number | Text | Text Field 16 | false | false | Choice Field 1 | Create Incident,Update Incident | — | — | Output Only | The human-readable Incident number from ServiceNow (populated by extension). |
| 25 | ritm_number | RITM Number | Text | Text Field 17 | false | false | Choice Field 1 | Update RITM | — | — | Output Only | The human-readable RITM number from ServiceNow (populated by extension). |
| 26 | cmdb_action | CMDB Action | Text | Text Field 18 | false | false | Choice Field 1 | Create/Update CI | — | — | Output Only | The IRE operation outcome: CREATED, UPDATED, or MATCHED (populated by extension). |
| 27 | cmdb_sys_id | CMDB Sys ID | Text | Text Field 19 | false | false | Choice Field 1 | Create/Update CI,Get CI | — | — | Output Only | The sys_id of the CI created, updated, or retrieved (populated by extension). extensionStatus=true. |
| 28 | cmdb_class | CMDB Class | Choice | Choice Field 4 | false | false | Choice Field 1 | Create/Update CI | — | — | No Restriction | CMDB table/class name confirmed by IRE response (populated by extension). |
| 29 | cmdb_name | CMDB Name | Choice | Choice Field 5 | false | false | Choice Field 1 | Create/Update CI,Get CI | — | — | No Restriction | CI name confirmed by ServiceNow (populated by extension). |
| 30 | cmdb_status | CMDB Status | Choice | Choice Field 6 | false | false | Choice Field 1 | Create/Update CI | — | — | No Restriction | Overall IRE operation status: SUCCESS or PARTIAL_SUCCESS (populated by extension). |
| 31 | cmdb_operational_status | CMDB Operational Status | Integer | Integer Field 2 | false | false | Choice Field 1 | Get CI | — | — | Output Only | Operational status of the retrieved CI. 1=Operational, 2=Non-Operational (populated by extension). |
| 32 | cmdb_cpu_count | CMDB CPU Count | Integer | Integer Field 3 | false | false | Choice Field 1 | Get CI | — | — | Output Only | CPU count of the retrieved CI (populated by extension). |
| 33 | cmdb_ram | CMDB RAM (MB) | Integer | Integer Field 4 | false | false | Choice Field 1 | Get CI | — | — | Output Only | RAM of the retrieved CI in MB (populated by extension). |
| 34 | cmdb_result_count | CMDB Result Count | Integer | Integer Field 5 | false | false | Choice Field 1 | Get CI | — | — | Output Only | Total number of CI records returned by the search query (populated by extension). |
| 35 | cmdb_result_json | CMDB Result JSON | Text | Large Text Field 4 | false | false | Choice Field 1 | Get CI | — | — | Output Only | Complete first CI record as a sanitized JSON string (populated by extension). |
| 36 | cmdb_results_json | CMDB Results JSON | Text | Text Field 20 | false | false | Choice Field 1 | Get CI | — | — | Output Only | All returned CI records as a sanitized JSON array string (populated by extension). |

## Cross-References

### Always-Required Fields
- `instance_url` (Text Field 1) — required: true, always visible
- `credential` (Credential Field 1) — required: true, always visible

### Conditionally-Required Fields (requireIfVisible: true)
- `short_description` — required when visible; visible when `action` = **Create Incident**
- `incident_sys_id` — required when visible; visible when `action` = **Update Incident**
- `ritm_sys_id` — required when visible; visible when `action` = **Update RITM**
- `ci_name` — required when visible; visible when `action` = **Create/Update CI**
- `search_value` — required when visible; visible when `action` = **Get CI**

### Field Visibility Dependencies (showIfField / showIfFieldValue)
All conditional fields depend on `action` (`Choice Field 1`):

| Visible when action = | Fields shown |
|-----------------------|-------------|
| Create Incident | short_description, description, category, priority, urgency, impact, caller, assignment_group, assigned_to, incident_number (output) |
| Update Incident | incident_sys_id, incident_fields_to_update, incident_number (output) |
| Update RITM | ritm_sys_id, ritm_fields_to_update, ritm_number (output) |
| Create/Update CI | ci_class, ci_name, attributes, data_source, cmdb_action (output), cmdb_sys_id (output), cmdb_class (output), cmdb_name (output), cmdb_status (output) |
| Get CI | ci_class, search_by, search_value, return_fields, limit, cmdb_sys_id (output), cmdb_name (output), cmdb_operational_status (output), cmdb_cpu_count (output), cmdb_ram (output), cmdb_result_count (output), cmdb_result_json (output), cmdb_results_json (output) |

- `ci_class` is shared between **Create/Update CI** and **Get CI** — it is a dynamic-choice field populated via `instance_url` + `credential` at runtime.
- `cmdb_sys_id` is shared between **Create/Update CI** and **Get CI**.
- `cmdb_name` is shared between **Create/Update CI** and **Get CI**.
- `incident_number` is shared between **Create Incident** and **Update Incident**.

### Dynamic Choice Fields
- `ci_class` (`Choice Field 2`) — `choiceDynamic: true`; populated at runtime using `choiceFields: ["Text Field 1", "Credential Field 1"]` (i.e., `instance_url` + `credential`)

### Mutually Exclusive Options
The `action` field drives four fully exclusive UI sections. Only fields for the selected action are shown at any one time:
- **Create Incident** and **Update Incident** share only `incident_number` (output)
- **Create/Update CI** and **Get CI** share `ci_class`, `cmdb_sys_id`, `cmdb_name`
- All other fields are exclusive to a single action value

### Output-Only Fields (fieldRestriction: Output Only)
- `incident_number`, `ritm_number`, `cmdb_action`, `cmdb_sys_id`, `cmdb_operational_status`, `cmdb_cpu_count`, `cmdb_ram`, `cmdb_result_count`, `cmdb_result_json`, `cmdb_results_json`

### Extension Status Field
- `cmdb_sys_id` — `extensionStatus: true` (used as the primary extension status indicator)
