# ServiceNow CMDB - Implementation Analysis

**Extension Name:** *ServiceNow CMDB (servicenow-cmdb)*
**Universal Template Name:** *Servicenow Cmdb*
**Target Platform:** Linux

---

## Extension Overview

Web-service-based Universal Extension that integrates Stonebranch UAC with ServiceNow for IT service management and CMDB operations. Provides five actions: Create Incident, Update Incident, Update RITM, Create/Update CI (via IRE), and Get CI. All actions use HTTP Basic Authentication and the ServiceNow REST API over HTTPS. The primary CMDB use case is post-provisioning CI registration using the ServiceNow Identification and Reconciliation Engine (IRE) to prevent duplicate Configuration Items.

---

# Template Fields

## 1. Input Fields

**(action)**
- **Type**: Choice Field (Single-select)
- **Visible When**: always
- **Required When**: always
- **Options**:
  - `Create Incident` - Create a new Incident record in ServiceNow
  - `Update Incident` - Update an existing Incident record by sys_id
  - `Update RITM` - Update an existing Request Item record by sys_id
  - `Create/Update CI` - Create or update a CMDB Configuration Item via IRE
  - `Get CI` - Retrieve one or more CMDB Configuration Items
- **Default Value**: `Create Incident`
- **Validation**:
  - Must be one of the five options
- **Purpose**: Selects the ServiceNow operation to perform; controls which action-specific fields are visible

---

**(instance_url)**
- **Type**: Text Field
- **Visible When**: always
- **Required When**: always
- **Validation**:
  - Must begin with `https://`
  - Must not include a trailing slash
- **Purpose**: Base URL of the ServiceNow instance used for all API calls
- **Example**: `https://myinstance.service-now.com`

---

**(credential)**
- **Type**: Credential Field
- **Visible When**: always
- **Required When**: always
- **Validation**:
  - `user` attribute must be provided (ServiceNow username)
  - `password` attribute must be provided (ServiceNow password)
- **Purpose**: UAC Credential providing Basic Auth username (`user`) and password (`password`) for all ServiceNow API calls

---

**(short_description)**
- **Type**: Text Field
- **Visible When**: action value is equal to `Create Incident`. It is required when it's visible.
- **Required When**: action value is equal to `Create Incident`
- **Validation**:
  - Must not be empty when visible
- **Purpose**: Brief one-line summary of the Incident; maps to ServiceNow `short_description` field
- **Example**: `Application server APP-PROD-01 is unreachable`

---

**(description)**
- **Type**: Text Field (Large)
- **Visible When**: action value is equal to `Create Incident`. It is not required when it's visible.
- **Required When**: never
- **Purpose**: Detailed multi-line description of the Incident; maps to ServiceNow `description` field
- **Example**: `Server APP-PROD-01 stopped responding at 14:32 UTC. Monitoring alert triggered. No scheduled maintenance window active.`

---

**(category)**
- **Type**: Text Field
- **Visible When**: action value is equal to `Create Incident`. It is not required when it's visible.
- **Required When**: never
- **Purpose**: Incident category; maps to ServiceNow `category` field
- **Example**: `Software`

---

**(priority)**
- **Type**: Text Field
- **Visible When**: action value is equal to `Create Incident`. It is not required when it's visible.
- **Required When**: never
- **Purpose**: Incident priority; maps to ServiceNow `priority` field
- **Example**: `2`

---

**(urgency)**
- **Type**: Text Field
- **Visible When**: action value is equal to `Create Incident`. It is not required when it's visible.
- **Required When**: never
- **Purpose**: Incident urgency; maps to ServiceNow `urgency` field
- **Example**: `2`

---

**(impact)**
- **Type**: Text Field
- **Visible When**: action value is equal to `Create Incident`. It is not required when it's visible.
- **Required When**: never
- **Purpose**: Incident impact; maps to ServiceNow `impact` field
- **Example**: `2`

---

**(caller)**
- **Type**: Text Field
- **Visible When**: action value is equal to `Create Incident`. It is not required when it's visible.
- **Required When**: never
- **Purpose**: ServiceNow user ID or display name of the person reporting the Incident; maps to ServiceNow `caller_id` field
- **Example**: `john.doe`

---

**(assignment_group)**
- **Type**: Text Field
- **Visible When**: action value is equal to `Create Incident`. It is not required when it's visible.
- **Required When**: never
- **Purpose**: ServiceNow assignment group name or sys_id; maps to ServiceNow `assignment_group` field
- **Example**: `Network Operations`

---

**(assigned_to)**
- **Type**: Text Field
- **Visible When**: action value is equal to `Create Incident`. It is not required when it's visible.
- **Required When**: never
- **Purpose**: ServiceNow user to whom the Incident is assigned; maps to ServiceNow `assigned_to` field
- **Example**: `jane.smith`

---

**(incident_sys_id)**
- **Type**: Text Field
- **Visible When**: action value is equal to `Update Incident`. It is required when it's visible.
- **Required When**: action value is equal to `Update Incident`
- **Validation**:
  - Must not be empty when visible
- **Purpose**: The `sys_id` of the Incident record to update; used as the path parameter in `PUT /api/now/table/incident/{sys_id}`
- **Example**: `abc123def456abc123def456abc123de`

---

**(incident_fields_to_update)**
- **Type**: Text Field (Large)
- **Visible When**: action value is equal to `Update Incident`. It is not required when it's visible.
- **Required When**: never
- **Purpose**: JSON object string of ServiceNow Incident field name-value pairs to update; sent as the PUT request body. When empty, an empty JSON object `{}` is sent, which triggers a record touch (updates `sys_updated_on`) without changing field values.
- **Example**: `{"state": "2", "work_notes": "Investigating the issue", "priority": "1"}`

---

**(ritm_sys_id)**
- **Type**: Text Field
- **Visible When**: action value is equal to `Update RITM`. It is required when it's visible.
- **Required When**: action value is equal to `Update RITM`
- **Validation**:
  - Must not be empty when visible
- **Purpose**: The `sys_id` of the Request Item record to update; used as the path parameter in `PUT /api/now/table/sc_req_item/{sys_id}`
- **Example**: `abc123def456abc123def456abc123de`

---

**(ritm_fields_to_update)**
- **Type**: Text Field (Large)
- **Visible When**: action value is equal to `Update RITM`. It is not required when it's visible.
- **Required When**: never
- **Purpose**: JSON object string of ServiceNow RITM field name-value pairs to update; sent as the PUT request body. When empty, an empty JSON object `{}` is sent.
- **Example**: `{"state": "3", "work_notes": "Approved and in progress", "approval": "approved"}`

---

**(ci_class)**
- **Type**: Choice Field (Dynamic)
- **Visible When**: action values are `Create/Update CI,Get CI`. It is required when it's visible.
- **Required When**: action values are `Create/Update CI,Get CI`
- **Depends On**:
  - `instance_url` — base URL needed to query ServiceNow for available CMDB tables
  - `credential` — authentication needed to query ServiceNow
- **Validation**:
  - Must not be empty when visible
- **Purpose**: CMDB table/class name for the CI. Dynamically populated from ServiceNow by querying all tables whose name starts with `cmdb_ci`. Display format is `<Label> (<table_name>)`. The raw table name (extracted from the selection) is used in API calls.

---

**(ci_name)**
- **Type**: Text Field
- **Visible When**: action value is equal to `Create/Update CI`. It is required when it's visible.
- **Required When**: action value is equal to `Create/Update CI`
- **Validation**:
  - Must not be empty when visible
- **Purpose**: The name of the Configuration Item; included as the `name` attribute in the IRE `values` object. Accepts Stonebranch variable references.
- **Example**: `${ops_var_vm_name}` or `APP-PROD-01`

---

**(attributes)**
- **Type**: Array Field
- **Visible When**: action value is equal to `Create/Update CI`. It is not required when it's visible.
- **Required When**: never
- **Purpose**: Variable-length list of CI attribute key-value pairs to include in the IRE payload `values` object. Each row provides one ServiceNow CI field name and its value. Values may contain Stonebranch variable references. Attributes with empty or null values are excluded from the IRE payload.
- **Array Name Title**: `Attribute Name`
- **Array Value Title**: `Attribute Value`

---

**(data_source)**
- **Type**: Text Field
- **Visible When**: action value is equal to `Create/Update CI`. It is not required when it's visible.
- **Required When**: never
- **Default Value**: `Stonebranch`
- **Purpose**: The discovery source identifier sent to ServiceNow IRE as the top-level `source` field. Used by ServiceNow CMDB reconciliation rules to determine attribute authority. When empty, the field is omitted from the IRE payload.
- **Example**: `Stonebranch`, `ServiceNow Discovery`, `SCCM`

---

**(search_by)**
- **Type**: Choice Field (Single-select)
- **Visible When**: action value is equal to `Get CI`. It is required when it's visible.
- **Required When**: action value is equal to `Get CI`
- **Options**:
  - `Name` - Queries `sysparm_query=name=<search_value>`
  - `Sys ID` - Queries `sysparm_query=sys_id=<search_value>`
  - `Custom Query` - Passes `search_value` directly as `sysparm_query`
- **Default Value**: `Name`
- **Validation**:
  - Must be one of the three options
- **Purpose**: Determines the search mode used to locate CI records in the CMDB table

---

**(search_value)**
- **Type**: Text Field
- **Visible When**: action value is equal to `Get CI`. It is required when it's visible.
- **Required When**: action value is equal to `Get CI`
- **Validation**:
  - Must not be empty when visible
- **Purpose**: The value used with the selected search mode. Interpreted according to `search_by`: exact name match, sys_id lookup, or raw ServiceNow encoded query string.
- **Example**: `APP-PROD-01` (Name), `abc123def456abc123def456abc123de` (Sys ID), `operational_status=1^ip_address=10.10.20.15` (Custom Query)

---

**(return_fields)**
- **Type**: Text Field
- **Visible When**: action value is equal to `Get CI`. It is not required when it's visible.
- **Required When**: never
- **Validation**:
  - When provided, must be comma-separated ServiceNow CI field names with no spaces around commas
- **Purpose**: Comma-separated list of CI field names to include in the ServiceNow Table API response via `sysparm_fields`. When empty, defaults to: `sys_id,name,ip_address,operational_status,cpu_count,ram,os,short_description`
- **Example**: `sys_id,name,ip_address,operational_status,cpu_count,ram`

---

**(limit)**
- **Type**: Int Field
- **Visible When**: action value is equal to `Get CI`. It is not required when it's visible.
- **Required When**: never
- **Default Value**: `1`
- **Validation**:
  - Must be a value between 1 and 10000
- **Purpose**: Maximum number of CI records returned; passed as `sysparm_limit` to the Table API

---

## 2. Output Fields

**(incident_sys_id)**
- **Type**: Text Output
- **Visible When**: action values are `Create Incident,Update Incident`
- **Purpose**: The `sys_id` of the created or updated Incident record
- **Examples**: `"abc123def456abc123def456abc123de"`

---

**(incident_number)**
- **Type**: Text Output
- **Visible When**: action values are `Create Incident,Update Incident`
- **Purpose**: The human-readable Incident number from ServiceNow
- **Examples**: `"INC0010001"`, `"INC0042857"`

---

**(ritm_sys_id)**
- **Type**: Text Output
- **Visible When**: action value is equal to `Update RITM`
- **Purpose**: The `sys_id` of the updated Request Item record
- **Examples**: `"def456abc123def456abc123def456ab"`

---

**(ritm_number)**
- **Type**: Text Output
- **Visible When**: action value is equal to `Update RITM`
- **Purpose**: The human-readable RITM number from ServiceNow
- **Examples**: `"RITM0010001"`, `"RITM0021345"`

---

**(cmdb_action)**
- **Type**: Text Output
- **Visible When**: action value is equal to `Create/Update CI`
- **Purpose**: The IRE operation outcome reflecting what ServiceNow did to the CI
- **Examples**: `"CREATED"`, `"UPDATED"`, `"MATCHED"`

---

**(cmdb_sys_id)**
- **Type**: Text Output
- **Visible When**: action values are `Create/Update CI,Get CI`
- **Purpose**: The `sys_id` of the Configuration Item that was created, updated, or retrieved
- **Examples**: `"abc123def456abc123def456abc123de"`

---

**(cmdb_class)**
- **Type**: Text Output
- **Visible When**: action value is equal to `Create/Update CI`
- **Purpose**: The CMDB table/class name of the CI as confirmed by the IRE response
- **Examples**: `"cmdb_ci_vm_instance"`, `"cmdb_ci_server"`

---

**(cmdb_name)**
- **Type**: Text Output
- **Visible When**: action values are `Create/Update CI,Get CI`
- **Purpose**: The name of the Configuration Item as confirmed by ServiceNow
- **Examples**: `"APP-PROD-01"`, `"db-server-02"`

---

**(cmdb_status)**
- **Type**: Text Output
- **Visible When**: action value is equal to `Create/Update CI`
- **Purpose**: The overall IRE operation status string derived from the identifyreconcile response
- **Examples**: `"SUCCESS"`, `"PARTIAL_SUCCESS"`

---

**(cmdb_ip_address)**
- **Type**: Text Output
- **Visible When**: action value is equal to `Get CI`
- **Purpose**: The IP address of the retrieved CI; populated when `ip_address` is in the returned fields
- **Examples**: `"10.10.20.15"`, `"192.168.1.100"`

---

**(cmdb_operational_status)**
- **Type**: Text Output
- **Visible When**: action value is equal to `Get CI`
- **Purpose**: The operational status of the retrieved CI; populated when `operational_status` is in the returned fields
- **Examples**: `"1"` (Operational), `"2"` (Non-Operational)

---

**(cmdb_cpu_count)**
- **Type**: Text Output
- **Visible When**: action value is equal to `Get CI`
- **Purpose**: The CPU count of the retrieved CI; populated when `cpu_count` is in the returned fields
- **Examples**: `"4"`, `"8"`

---

**(cmdb_ram)**
- **Type**: Text Output
- **Visible When**: action value is equal to `Get CI`
- **Purpose**: The RAM of the retrieved CI in MB; populated when `ram` is in the returned fields
- **Examples**: `"16384"`, `"8192"`

---

**(cmdb_os)**
- **Type**: Text Output
- **Visible When**: action value is equal to `Get CI`
- **Purpose**: The operating system of the retrieved CI; populated when `os` is in the returned fields
- **Examples**: `"Linux Red Hat"`, `"Windows Server 2019"`

---

**(cmdb_short_description)**
- **Type**: Text Output
- **Visible When**: action value is equal to `Get CI`
- **Purpose**: The short description of the retrieved CI; populated when `short_description` is in the returned fields
- **Examples**: `"Production VM for order processing service"`

---

**(cmdb_result_json)**
- **Type**: Text Output
- **Visible When**: action value is equal to `Get CI`
- **Purpose**: Complete first-result CI record as a sanitized JSON string; credentials never appear in this field
- **Examples**: `"{\"sys_id\": \"abc123\", \"name\": \"APP-PROD-01\", \"ip_address\": \"10.10.20.15\"}"`

---

**(cmdb_results_json)**
- **Type**: Text Output
- **Visible When**: action value is equal to `Get CI`
- **Purpose**: All returned CI records as a sanitized JSON array string; populated only when multiple results are returned
- **Examples**: `"[{\"sys_id\": \"abc123\", ...}, {\"sys_id\": \"def456\", ...}]"`

---

## 3. Field Ordering

**Field Order (Visual Layout):**

```
┌─────────────────────────────────────────────┐
│                   action                    │  ← Full-width
├─────────────────────────────────────────────┤
│                 instance_url                │  ← Full-width
├─────────────────────────────────────────────┤
│                  credential                 │  ← Full-width (credential)
├─────────────────────────────────────────────┤
│  [Create Incident fields]                   │
│             short_description               │  ← Full-width
├─────────────────────────────────────────────┤
│                 description                 │  ← Full-width
├─────────────────────────────────────────────┤
│       category        │      priority       │  ← Half-width pair
├───────────────────────┼─────────────────────┤
│       urgency         │       impact        │  ← Half-width pair
├─────────────────────────────────────────────┤
│                   caller                    │  ← Full-width
├───────────────────────┼─────────────────────┤
│    assignment_group   │    assigned_to      │  ← Half-width pair
├─────────────────────────────────────────────┤
│  [Update Incident fields]                   │
│              incident_sys_id                │  ← Full-width
├─────────────────────────────────────────────┤
│          incident_fields_to_update          │  ← Full-width
├─────────────────────────────────────────────┤
│  [Update RITM fields]                       │
│                 ritm_sys_id                 │  ← Full-width
├─────────────────────────────────────────────┤
│            ritm_fields_to_update            │  ← Full-width
├─────────────────────────────────────────────┤
│  [Shared CI fields]                         │
│                  ci_class                   │  ← Full-width
├─────────────────────────────────────────────┤
│  [Create/Update CI fields]                  │
│                  ci_name                    │  ← Full-width
├─────────────────────────────────────────────┤
│                 attributes                  │  ← Full-width
├─────────────────────────────────────────────┤
│                 data_source                 │  ← Full-width
├─────────────────────────────────────────────┤
│  [Get CI fields]                            │
│                  search_by                  │  ← Full-width
├─────────────────────────────────────────────┤
│                 search_value                │  ← Full-width
├─────────────────────────────────────────────┤
│                 return_fields               │  ← Full-width
├─────────────────────────────────────────────┤
│         limit         │                     │  ← Half-width (limit only)
├─────────────────────────────────────────────┤
│  [Output fields — Incident]                 │
│    incident_sys_id    │   incident_number   │  ← Half-width pair
├─────────────────────────────────────────────┤
│  [Output fields — RITM]                     │
│      ritm_sys_id      │    ritm_number      │  ← Half-width pair
├─────────────────────────────────────────────┤
│  [Output fields — CI Create/Update]         │
│      cmdb_action      │    cmdb_sys_id      │  ← Half-width pair
├───────────────────────┼─────────────────────┤
│      cmdb_class       │     cmdb_name       │  ← Half-width pair
├─────────────────────────────────────────────┤
│                 cmdb_status                 │  ← Full-width
├─────────────────────────────────────────────┤
│  [Output fields — Get CI]                   │
│      cmdb_sys_id      │     cmdb_name       │  ← Half-width pair (shared)
├───────────────────────┼─────────────────────┤
│   cmdb_ip_address     │ cmdb_operational_   │  ← Half-width pair
│                       │      status         │
├───────────────────────┼─────────────────────┤
│    cmdb_cpu_count     │      cmdb_ram       │  ← Half-width pair
├───────────────────────┼─────────────────────┤
│       cmdb_os         │ cmdb_short_descr.   │  ← Half-width pair
├─────────────────────────────────────────────┤
│               cmdb_result_json              │  ← Full-width
├─────────────────────────────────────────────┤
│              cmdb_results_json              │  ← Full-width
└─────────────────────────────────────────────┘
```

---

# Actions

## Action 1: Create Incident

**Description**: Creates a new Incident record in ServiceNow using the Table API. On success, exposes the created Incident's sys_id and number as output fields.

### Input Requirements

- **instance_url**
- **credential**
- **short_description** (required)
- **description** (optional)
- **category** (optional)
- **priority** (optional)
- **urgency** (optional)
- **impact** (optional)
- **caller** (optional)
- **assignment_group** (optional)
- **assigned_to** (optional)

### Execution Flow

**Step 1: Input Validation**
- Verify `short_description` is not empty; raise `InputValidationError` (exit code 2) if empty.

**Step 2: Build Request Payload**
- Construct JSON body with `short_description` as mandatory key.
- For each optional field (`description`, `category`, `priority`, `urgency`, `impact`, `caller`, `assignment_group`, `assigned_to`): include in payload only if the field value is non-empty.
- Field name mapping to ServiceNow fields: `caller` → `caller_id`, all others map directly by field name.

**Step 3: Execute API Call**
- Send `POST` to `{instance_url}/api/now/table/incident` with Basic Auth from `credential.user` and `credential.password`.
- Set `Content-Type: application/json` and `Accept: application/json` headers.
- Apply HTTP timeout from `UE_HTTP_TIMEOUT` environment variable (default: 30 seconds).

**Step 4: Handle Response**
- HTTP 200 or 201: parse `result.sys_id` and `result.number` from response body.
- HTTP 401: raise `AuthenticationError`.
- HTTP 403: raise `AuthorizationError`.
- HTTP 400: inspect ServiceNow error detail; determine if business rule or validation error; raise `ServiceNowBusinessRuleError` or `ServiceNowValidationError` accordingly, preserving original error message.
- Connection/timeout exception: raise `ConnectionError`.

**Step 5: Set Outputs**
- Populate output field `incident_sys_id` with `result.sys_id`.
- Populate output field `incident_number` with `result.number`.

**Step 6: Write STDOUT**
- Print ASCII table (`rounded_outline` format via `tabulate`) showing: `sys_id`, `number`, `short_description`, `state`, `priority` from the response.

**Step 7: Return**
- Exit code `0`, status description: `"Incident <number> created successfully"`.

### Output Examples

**STDOUT**:
```
╭──────────────────────────────────┬─────────────┬─────────────────────────────────────┬───────┬──────────╮
│ Sys ID                           │ Number      │ Short Description                   │ State │ Priority │
├──────────────────────────────────┼─────────────┼─────────────────────────────────────┼───────┼──────────┤
│ abc123def456abc123def456abc123de │ INC0010001  │ Application server APP-PROD-01 is   │ 1     │ 2        │
│                                  │             │ unreachable                         │       │          │
╰──────────────────────────────────┴─────────────┴─────────────────────────────────────┴───────┴──────────╯
```

**Extension Output result object (JSON)**:

*The Extension output also includes `exit_code`, `status_description`, and `invocation` elements that are added automatically during implementation time.*

```json
{
  "result": {
    "sys_id": "abc123def456abc123def456abc123de",
    "number": "INC0010001",
    "short_description": "Application server APP-PROD-01 is unreachable",
    "state": "1",
    "priority": "2"
  }
}
```

### Success Criteria
1. ServiceNow responds with HTTP 200 or 201.
2. Response body contains a valid `result.sys_id` (non-empty) and `result.number`.
3. Output fields `incident_sys_id` and `incident_number` are populated.

---

## Action 2: Update Incident

**Description**: Updates an existing Incident record in ServiceNow by sys_id using the Table API. On success, exposes the updated Incident's sys_id and number as output fields.

### Input Requirements

- **instance_url**
- **credential**
- **incident_sys_id** (required)
- **incident_fields_to_update** (optional)

### Execution Flow

**Step 1: Input Validation**
- Verify `incident_sys_id` is not empty; raise `InputValidationError` (exit code 2) if empty.
- If `incident_fields_to_update` is non-empty, attempt to parse it as JSON; raise `InputValidationError` (exit code 2) if it is not valid JSON.

**Step 2: Build Request Payload**
- If `incident_fields_to_update` is non-empty: use the parsed JSON object as the PUT body.
- If `incident_fields_to_update` is empty: use an empty JSON object `{}` as the PUT body.

**Step 3: Execute API Call**
- Send `PUT` to `{instance_url}/api/now/table/incident/{incident_sys_id}` with Basic Auth.
- Set `Content-Type: application/json` and `Accept: application/json` headers.
- Apply HTTP timeout from `UE_HTTP_TIMEOUT` (default: 30 seconds).

**Step 4: Handle Response**
- HTTP 200: parse `result.sys_id` and `result.number` from response body.
- HTTP 401: raise `AuthenticationError`.
- HTTP 403: raise `AuthorizationError`.
- HTTP 400 or 422: inspect ServiceNow error detail; raise `ServiceNowBusinessRuleError` or `ServiceNowValidationError` preserving original message.
- HTTP 404: raise `ServiceNowValidationError` with message "Incident not found: {incident_sys_id}".
- Connection/timeout exception: raise `ConnectionError`.

**Step 5: Set Outputs**
- Populate output field `incident_sys_id` with `result.sys_id`.
- Populate output field `incident_number` with `result.number`.

**Step 6: Write STDOUT**
- Print ASCII table (`rounded_outline`) showing: `sys_id`, `number`, `state`, `sys_updated_on` from the response.

**Step 7: Return**
- Exit code `0`, status description: `"Incident <number> updated successfully"`.

### Output Examples

**STDOUT**:
```
╭──────────────────────────────────┬────────────┬───────┬─────────────────────────╮
│ Sys ID                           │ Number     │ State │ Updated On              │
├──────────────────────────────────┼────────────┼───────┼─────────────────────────┤
│ abc123def456abc123def456abc123de │ INC0010001 │ 2     │ 2026-09-11 14:32:00 UTC │
╰──────────────────────────────────┴────────────┴───────┴─────────────────────────╯
```

**Extension Output result object (JSON)**:

```json
{
  "result": {
    "sys_id": "abc123def456abc123def456abc123de",
    "number": "INC0010001",
    "state": "2",
    "sys_updated_on": "2026-09-11 14:32:00"
  }
}
```

### Success Criteria
1. ServiceNow responds with HTTP 200.
2. Response body contains valid `result.sys_id` and `result.number`.
3. Output fields `incident_sys_id` and `incident_number` are populated.

---

## Action 3: Update RITM

**Description**: Updates an existing Request Item (RITM) record in ServiceNow by sys_id using the Table API. On success, exposes the updated RITM's sys_id and number as output fields.

### Input Requirements

- **instance_url**
- **credential**
- **ritm_sys_id** (required)
- **ritm_fields_to_update** (optional)

### Execution Flow

**Step 1: Input Validation**
- Verify `ritm_sys_id` is not empty; raise `InputValidationError` (exit code 2) if empty.
- If `ritm_fields_to_update` is non-empty, attempt to parse as JSON; raise `InputValidationError` (exit code 2) if invalid JSON.

**Step 2: Build Request Payload**
- If `ritm_fields_to_update` is non-empty: use the parsed JSON object as the PUT body.
- If `ritm_fields_to_update` is empty: use an empty JSON object `{}` as the PUT body.

**Step 3: Execute API Call**
- Send `PUT` to `{instance_url}/api/now/table/sc_req_item/{ritm_sys_id}` with Basic Auth.
- Set `Content-Type: application/json` and `Accept: application/json` headers.
- Apply HTTP timeout from `UE_HTTP_TIMEOUT` (default: 30 seconds).

**Step 4: Handle Response**
- HTTP 200: parse `result.sys_id` and `result.number` from response body.
- HTTP 401: raise `AuthenticationError`.
- HTTP 403: raise `AuthorizationError`.
- HTTP 400 or 422: raise `ServiceNowBusinessRuleError` or `ServiceNowValidationError` preserving original message.
- HTTP 404: raise `ServiceNowValidationError` with message "RITM not found: {ritm_sys_id}".
- Connection/timeout exception: raise `ConnectionError`.

**Step 5: Set Outputs**
- Populate output field `ritm_sys_id` with `result.sys_id`.
- Populate output field `ritm_number` with `result.number`.

**Step 6: Write STDOUT**
- Print ASCII table (`rounded_outline`) showing: `sys_id`, `number`, `state`, `sys_updated_on` from the response.

**Step 7: Return**
- Exit code `0`, status description: `"RITM <number> updated successfully"`.

### Output Examples

**STDOUT**:
```
╭──────────────────────────────────┬──────────────┬───────┬─────────────────────────╮
│ Sys ID                           │ Number       │ State │ Updated On              │
├──────────────────────────────────┼──────────────┼───────┼─────────────────────────┤
│ def456abc123def456abc123def456ab │ RITM0010001  │ 3     │ 2026-09-11 14:35:00 UTC │
╰──────────────────────────────────┴──────────────┴───────┴─────────────────────────╯
```

**Extension Output result object (JSON)**:

```json
{
  "result": {
    "sys_id": "def456abc123def456abc123def456ab",
    "number": "RITM0010001",
    "state": "3",
    "sys_updated_on": "2026-09-11 14:35:00"
  }
}
```

### Success Criteria
1. ServiceNow responds with HTTP 200.
2. Response body contains valid `result.sys_id` and `result.number`.
3. Output fields `ritm_sys_id` and `ritm_number` are populated.

---

## Action 4: Create/Update CI

**Description**: Creates or updates a Configuration Item in ServiceNow CMDB exclusively via the Identification and Reconciliation Engine (IRE) endpoint. IRE determines whether to INSERT a new CI or UPDATE an existing CI based on ServiceNow identification rules. Direct Table API writes are prohibited.

### Input Requirements

- **instance_url**
- **credential**
- **ci_class** (required — dynamic choice, provides the raw table name after parsing)
- **ci_name** (required)
- **attributes** (optional — array of name/value pairs)
- **data_source** (optional, default: `Stonebranch`)

### Execution Flow

**Step 1: Input Validation**
- Verify `ci_class` selection is non-empty; extract raw table name from the selected value by parsing the format `<Label> (<table_name>)` — extract the substring inside the last pair of parentheses. Raise `InputValidationError` (exit code 2) if result is empty.
- Verify `ci_name` is non-empty; raise `InputValidationError` (exit code 2) if empty.

**Step 2: Build IRE Payload**
- Initialize `values` dict with `{"name": ci_name}`.
- Iterate over each item in the `attributes` array. For each item where `item["value"]` is not empty, not None, not `"[]"`, and not `"{}"`: add `item["name"]: item["value"]` to the `values` dict. Skip items with empty values.
- Construct the IRE payload:
  ```
  {
    "items": [
      {
        "className": <raw_table_name>,
        "values": <values_dict>
      }
    ]
  }
  ```
- If `data_source` is non-empty, add `"source": <data_source>` as a top-level key in the payload.

**Step 3: Execute API Call**
- Send `POST` to `{instance_url}/api/now/identifyreconcile` with Basic Auth.
- Set `Content-Type: application/json` and `Accept: application/json` headers.
- Apply HTTP timeout from `UE_HTTP_TIMEOUT` (default: 30 seconds).

**Step 4: Handle Response**
- HTTP 200: proceed to parse IRE result (Step 5).
- HTTP 401: raise `AuthenticationError`.
- HTTP 403: raise `AuthorizationError`.
- HTTP 400: inspect `result.identificationResults[0].errors` if present. If error message contains "identification" keyword → raise `CmdbIdentificationError` preserving ServiceNow message. Otherwise → raise `ServiceNowValidationError` preserving message.
- Connection/timeout exception: raise `ConnectionError`.

**Step 5: Parse IRE Response**
- Extract `result.identificationResults[0]` from response.
- If `identificationResults` is empty: raise `CmdbIdentificationError` with message "IRE returned no identification results".
- Check `identificationResults[0].errors` array: if non-empty, inspect error message. If "reconciliation" in message → raise `CmdbReconciliationError` preserving full error message. If "identification" in message → raise `CmdbIdentificationError`. Otherwise → raise `ServiceNowValidationError`.
- Map `operation` field to `cmdb_action`:
  - `"INSERT"` or `"insert"` → `"CREATED"`
  - `"UPDATE"` or `"update"` → `"UPDATED"`
  - `"MATCH"` or `"match"` → `"MATCHED"`
- Extract `sysId` as `cmdb_sys_id`.
- Extract `className` as `cmdb_class`.
- Determine `cmdb_name` from the `values.name` field in the submitted payload (since IRE response may not echo it).
- Derive `cmdb_status`: if `identificationResults[0].errors` is empty → `"SUCCESS"`. If `identificationResults[0].warnings` is non-empty → `"PARTIAL_SUCCESS"`.

**Step 6: Set Outputs**
- Populate output fields: `cmdb_action`, `cmdb_sys_id`, `cmdb_class`, `cmdb_name`, `cmdb_status`.

**Step 7: Write STDOUT**
- Print ASCII table (`rounded_outline`) showing: `Operation`, `Sys ID`, `CI Class`, `CI Name`, `Status`.

**Step 8: Return**
- Exit code `0`, status description: `"CI <cmdb_action>: <cmdb_name> (<cmdb_class>)"`.

### Output Examples

**STDOUT**:
```
╭─────────┬──────────────────────────────────┬────────────────────────┬──────────────┬─────────╮
│ Operation │ Sys ID                         │ CI Class               │ CI Name      │ Status  │
├─────────┬─┼──────────────────────────────────┼────────────────────────┼──────────────┼─────────┤
│ CREATED │ │ abc123def456abc123def456abc123de │ cmdb_ci_vm_instance    │ APP-PROD-01  │ SUCCESS │
╰─────────┴─┴──────────────────────────────────┴────────────────────────┴──────────────┴─────────╯
```

**Extension Output result object (JSON)**:

```json
{
  "result": {
    "cmdb_action": "CREATED",
    "cmdb_sys_id": "abc123def456abc123def456abc123de",
    "cmdb_class": "cmdb_ci_vm_instance",
    "cmdb_name": "APP-PROD-01",
    "cmdb_status": "SUCCESS"
  }
}
```

### Success Criteria
1. ServiceNow IRE responds with HTTP 200.
2. `identificationResults[0].errors` is empty.
3. `sysId` is non-empty in the IRE response.
4. All five `cmdb_*` output fields are populated.
5. Original ServiceNow error message is preserved if IRE returns identification or reconciliation errors.

---

## Action 5: Get CI

**Description**: Retrieves one or more Configuration Items from ServiceNow CMDB using the Table API. Supports search by Name, Sys ID, or Custom Query. Returns CI attributes as both individual output fields and a full JSON string.

### Input Requirements

- **instance_url**
- **credential**
- **ci_class** (required — dynamic choice, provides raw table name after parsing)
- **search_by** (required)
- **search_value** (required)
- **return_fields** (optional)
- **limit** (optional, default: 1)

### Execution Flow

**Step 1: Input Validation**
- Extract raw table name from `ci_class` selection by parsing `<Label> (<table_name>)` format; raise `InputValidationError` (exit code 2) if empty.
- Verify `search_value` is non-empty; raise `InputValidationError` (exit code 2) if empty.

**Step 2: Build Query Parameters**
- Determine `sysparm_query`:
  - If `search_by` = `Name`: `sysparm_query = "name=" + search_value`
  - If `search_by` = `Sys ID`: `sysparm_query = "sys_id=" + search_value`
  - If `search_by` = `Custom Query`: `sysparm_query = search_value` (passed as-is)
- Determine `sysparm_fields`:
  - If `return_fields` is non-empty: strip whitespace from each comma-separated field name, use as-is.
  - If `return_fields` is empty: use `"sys_id,name,ip_address,operational_status,cpu_count,ram,os,short_description"`.
- Determine `sysparm_limit`: use `limit` field value (default: 1).

**Step 3: Execute API Call**
- Send `GET` to `{instance_url}/api/now/table/{raw_table_name}` with query parameters `sysparm_query`, `sysparm_fields`, `sysparm_limit`.
- Use Basic Auth. Set `Accept: application/json`.
- Apply HTTP timeout from `UE_HTTP_TIMEOUT` (default: 30 seconds).

**Step 4: Handle Response**
- HTTP 200: proceed to Step 5.
- HTTP 401: raise `AuthenticationError`.
- HTTP 403: raise `AuthorizationError`.
- HTTP 400: raise `ServiceNowValidationError` preserving original message (may indicate invalid table name or query).
- Connection/timeout exception: raise `ConnectionError`.

**Step 5: Process Results**
- Parse `result` array from response body.
- If `result` is empty (zero records):
  - Write to STDOUT: `"No CI found matching search criteria."`
  - Raise `NotFoundError` with message `"Not Found: No CI found for [<search_by>: <search_value>]"`.
- If `result` has one or more records:
  - Set `first_result` = `result[0]`.
  - For each field in the resolved `sysparm_fields` list: populate the corresponding output field using prefix `cmdb_`. For example, `ip_address` → `cmdb_ip_address`. If a field is not in the predefined output field list (i.e., it was a custom return field), skip output field population for that field (it is still captured in `cmdb_result_json`).
  - Sanitize `first_result`: remove any keys whose values contain or equal credential data (credential values are never placed in result objects by the extension).
  - Populate `cmdb_result_json` with sanitized JSON string of `first_result`.
  - Populate `cmdb_sys_id` from `first_result["sys_id"]`.
  - Populate `cmdb_name` from `first_result["name"]`.
  - If `len(result) > 1`:
    - Populate `cmdb_results_json` with sanitized JSON array string of all results.
    - Write to STDOUT: note "Returning N results. Individual output fields reflect the first result. Full results in cmdb_results_json." followed by ASCII table of first result.
    - Exit code `0`, status description: `"<N> CIs found. First result shown in output fields."`
  - If `len(result) == 1`:
    - Write to STDOUT: ASCII table of the single CI record's attributes.
    - Exit code `0`, status description: `"CI found: <cmdb_name> (<raw_table_name>)"`

**Step 6: Write STDOUT**
- Print ASCII table (`rounded_outline`) with column headers derived from the resolved field list, values from the first result.
- When N > 1: prepend the note about multiple results before the table.

**Step 7: Return**
- Exit code `0` with appropriate status description (single result or multiple results).

### Output Examples

**STDOUT (single result)**:
```
╭──────────────────────────────────┬─────────────┬────────────────┬────────────────────┬───────────┬───────┬──────────────────┬──────────────────────────────────────╮
│ Sys ID                           │ Name        │ IP Address     │ Operational Status │ CPU Count │ RAM   │ OS               │ Short Description                    │
├──────────────────────────────────┼─────────────┼────────────────┼────────────────────┼───────────┼───────┼──────────────────┼──────────────────────────────────────┤
│ abc123def456abc123def456abc123de │ APP-PROD-01 │ 10.10.20.15   │ 1                  │ 4         │ 16384 │ Linux Red Hat    │ Production VM for order processing   │
╰──────────────────────────────────┴─────────────┴────────────────┴────────────────────┴───────────┴───────┴──────────────────┴──────────────────────────────────────╯
```

**STDOUT (multiple results)**:
```
Returning 3 results. Individual output fields reflect the first result. Full results in cmdb_results_json.

╭──────────────────────────────────┬─────────────┬────────────────┬────────────────────┬───────────┬───────┬──────────────────┬────────────────────────────────────╮
│ Sys ID                           │ Name        │ IP Address     │ Operational Status │ CPU Count │ RAM   │ OS               │ Short Description                  │
├──────────────────────────────────┼─────────────┼────────────────┼────────────────────┼───────────┼───────┼──────────────────┼────────────────────────────────────┤
│ abc123def456abc123def456abc123de │ APP-PROD-01 │ 10.10.20.15   │ 1                  │ 4         │ 16384 │ Linux Red Hat    │ Production VM (first result shown) │
╰──────────────────────────────────┴─────────────┴────────────────┴────────────────────┴───────────┴───────┴──────────────────┴────────────────────────────────────╯
```

**Extension Output result object (JSON)**:

```json
{
  "result": {
    "cmdb_sys_id": "abc123def456abc123def456abc123de",
    "cmdb_name": "APP-PROD-01",
    "cmdb_ip_address": "10.10.20.15",
    "cmdb_operational_status": "1",
    "cmdb_cpu_count": "4",
    "cmdb_ram": "16384",
    "cmdb_os": "Linux Red Hat",
    "cmdb_short_description": "Production VM for order processing",
    "cmdb_result_json": "{\"sys_id\": \"abc123...\", \"name\": \"APP-PROD-01\", ...}",
    "result_count": 1
  }
}
```

### Success Criteria
1. ServiceNow Table API responds with HTTP 200.
2. At least one CI record is returned.
3. `cmdb_sys_id` and `cmdb_name` output fields are populated from the first result.
4. `cmdb_result_json` contains the sanitized full first CI record.
5. When multiple results: `cmdb_results_json` contains all records and STDOUT includes the N-results note.
6. When zero results: task fails with return code 1 and `NOT_FOUND_ERROR` status.

---

# Progress Reporting

Progress Reporting (percentage of completion report) is not required. The extension writes operation progress and result information to STDOUT using ASCII tables. Log messages at appropriate levels are written to STDERR using the standard Log Level field.

---

# Dynamic Choice Field Population

## ci_class

**Purpose**: Dynamically populate the CI Class dropdown with all available CMDB CI table names from the target ServiceNow instance, displayed as `<Label> (<table_name>)` format for human-readable selection.

**Fields**:
- `instance_url` — required to form the API base URL for querying tables
- `credential` — required for Basic Auth to query ServiceNow
- `ci_class` — this field (the one being populated)

**Trigger**: User-initiated action to populate the CI Class dropdown (clicking the refresh/load button in UAC UI)

**Execution Flow**:

1. Retrieve `instance_url` and `credential` field values from the current task form context.
2. Validate that both `instance_url` and `credential` are non-empty; return empty list and log error if either is missing.
3. Send `GET` to `{instance_url}/api/now/table/sys_db_object` with query parameters:
   - `sysparm_query=name STARTSWITH cmdb_ci`
   - `sysparm_fields=name,label`
   - `sysparm_limit=1000`
   - Basic Auth from `credential.user` and `credential.password`.
4. Apply HTTP timeout of 30 seconds.
5. Parse the `result` array from the response.
6. For each entry in `result`: construct display string as `<label> (<name>)`. If `label` is empty or null, use `<name> (<name>)` as fallback.
7. Sort the resulting list alphabetically.
8. Return the sorted list of strings to UAC.

**Returned to UAC**:
```json
["Computer (cmdb_ci_computer)", "Server (cmdb_ci_server)", "VM Instance (cmdb_ci_vm_instance)", "..."]
```

**Error Handling**:
- Exception is `AuthenticationError` (HTTP 401): Return empty list, log error "Authentication failed while loading CI classes"
- Exception is `AuthorizationError` (HTTP 403): Return empty list, log error "Insufficient permissions to query CMDB tables"
- Exception is connection/timeout: Return empty list, log error "Connection to ServiceNow failed while loading CI classes: <reason>"
- Exception is HTTP 400 or other API error: Return empty list, log error with ServiceNow error detail

---

# Cancellation Behavior

Default UAC cancellation behavior applies. No custom cancellation logic is required. When the UAC framework sends a TERM signal, the extension process terminates. The `requests` library HTTP session may be interrupted mid-request; no cleanup logic beyond the default TERM signal handling is needed since the extension creates no temporary files or persistent state.

---

# Re-Run Behavior

Re-runs are treated as initial executions for all actions. No special re-run logic is implemented.

For the Create/Update CI action specifically: re-running the same task will trigger IRE again. ServiceNow IRE will UPDATE or MATCH the existing CI rather than create a duplicate, provided CI attributes satisfy the identification rules. This is inherent ServiceNow IRE behavior and requires no custom extension logic.

---

# Dynamic Commands

No Dynamic commands should be implemented. The only programmable runtime behavior beyond the main execution is the `ci_class` dynamic choice field population, which is documented in the Dynamic Choice Field Population section.

---

# Utility Modules

## Required Utility Modules

### 1. ServiceNow API Client

**Purpose**: Encapsulates all HTTP communication with the ServiceNow REST API, providing a consistent interface for all actions to make authenticated requests, handle common HTTP error patterns, and close connections on completion.

**Required Capabilities:**

**Session Management:**
- Initialize a `requests.Session` with Basic Auth from `credential.user` and `credential.password`
- Set default headers: `Content-Type: application/json`, `Accept: application/json`
- Read `UE_HTTP_TIMEOUT` environment variable; default to 30 seconds if not set or not a valid integer
- Close the session after each task execution (both success and failure paths)

**HTTP Operations:**
- Execute `POST` requests with JSON body: `post(url, payload_dict)`
- Execute `PUT` requests with JSON body: `put(url, payload_dict)`
- Execute `GET` requests with query parameters: `get(url, params_dict)`
- Apply the configured timeout to all requests

**Response Validation:**
- For all responses: check HTTP status code and raise appropriate custom exceptions
- HTTP 401 → raise `AuthenticationError` with message "Authentication Error: Invalid ServiceNow credentials"
- HTTP 403 → raise `AuthorizationError` with message "Authorization Error: Insufficient permissions for this operation"
- HTTP 400 or 422: extract ServiceNow error detail from response body (typically in `error.message` or `error.detail`); categorize as `ServiceNowBusinessRuleError` or `ServiceNowValidationError` based on the presence of business-rule-indicative keywords in the message
- HTTP 404: raise `ServiceNowValidationError` with message including the requested path
- HTTP 200 and 201: return parsed JSON response body as dict
- `requests.exceptions.ConnectionError`, `requests.exceptions.SSLError`, DNS failure → raise `ConnectionError` with message "Connection Error: Unable to reach ServiceNow instance at <instance_url>"
- `requests.exceptions.Timeout` → raise `ConnectionError` with message "Connection Error: Request timed out after <N> seconds"

**Credential Safety:**
- Never log, print, or include `credential.user` or `credential.password` in any exception message, STDOUT, STDERR, or output field

**Used By**: All five actions and the CI Class dynamic choice field population

---

### 2. CI Class Name Parser

**Purpose**: Extracts the raw ServiceNow table name from the dynamic choice display format `<Label> (<table_name>)` used by the `ci_class` field.

**Required Capabilities:**
- Parse a string of format `<Label> (<table_name>)` and return `table_name`
- Handle edge cases: if the string does not contain parentheses, return the entire string as-is
- If the string is empty, return empty string (caller handles validation)
- Strip surrounding whitespace from the extracted table name

**Used By**: Create/Update CI action (Step 1), Get CI action (Step 1), CI Class dynamic choice field population is the inverse — it builds this format.

---

### 3. IRE Response Parser

**Purpose**: Parses the ServiceNow `identifyreconcile` API response, extracts CI operation outcome, and maps operation codes to human-readable action names.

**Required Capabilities:**

**Result Extraction:**
- Extract `identificationResults` list from `result` key in response
- Validate list is non-empty; raise `CmdbIdentificationError` if empty
- Access `identificationResults[0]` as the primary result

**Error Detection:**
- Check `errors` list in primary result; if non-empty, inspect error message text
- Route to `CmdbIdentificationError` or `CmdbReconciliationError` based on keyword matching in error message; preserve full original ServiceNow error message

**Operation Mapping:**
- Map `operation` field: `"INSERT"` or `"insert"` → `"CREATED"`, `"UPDATE"` or `"update"` → `"UPDATED"`, `"MATCH"` or `"match"` → `"MATCHED"`, any other value → `"UNKNOWN"`

**Status Derivation:**
- If `errors` is empty and `warnings` is empty → `"SUCCESS"`
- If `errors` is empty and `warnings` is non-empty → `"PARTIAL_SUCCESS"`

**Used By**: Create/Update CI action (Step 5)

---

### 4. Output Table Formatter

**Purpose**: Produces consistently formatted ASCII tables for STDOUT using the `tabulate` library with `tablefmt="rounded_outline"`.

**Required Capabilities:**

**Table Rendering:**
- Accept a list of column headers and a list of row value lists; return a formatted ASCII table string
- Accept a dict of field-name to value mappings for single-record display; render as two-column table (Field, Value)
- Print the rendered string to STDOUT

**Multi-result Note:**
- Prepend a plain-text note before the table when multiple CI results are returned: `"Returning N results. Individual output fields reflect the first result. Full results in cmdb_results_json."`

**Used By**: All five actions (STDOUT output steps)

---

### 5. JSON Sanitizer

**Purpose**: Converts dict or list objects to JSON strings, ensuring that credential values never appear in output.

**Required Capabilities:**
- Serialize a dict or list to a compact JSON string (no indentation for output fields; optional indentation for STDOUT readability)
- Accept a set of values to exclude: if any dict value matches an excluded value, replace it with `"[REDACTED]"` before serialization
- Caller provides `{credential.password}` as the exclusion set

**Used By**: Get CI action (cmdb_result_json and cmdb_results_json population)

---

## Exception Mapping Strategy

**HTTP Communication Errors:**
- Connection failure, DNS error, SSL error → `ConnectionError` (exit code 1, transient — retry may succeed)
- Request timeout → `ConnectionError` (exit code 1, transient)

**ServiceNow API Response Errors:**
- HTTP 401 → `AuthenticationError` (exit code 1, user configuration error — non-transient)
- HTTP 403 → `AuthorizationError` (exit code 1, user configuration error — non-transient)
- HTTP 400/422 — general payload/field issue → `ServiceNowValidationError` (exit code 1, user input/config error)
- HTTP 400/422 — business rule triggered → `ServiceNowBusinessRuleError` (exit code 1, user config/ServiceNow config error)
- HTTP 404 → `ServiceNowValidationError` (exit code 1, user input error — record not found)

**CMDB-Specific Errors:**
- IRE identification failure → `CmdbIdentificationError` (exit code 1, user input or ServiceNow config error)
- IRE reconciliation failure → `CmdbReconciliationError` (exit code 1, user input or ServiceNow config error)

**Get CI Not Found:**
- Zero results from Table API query → `NotFoundError` (exit code 1, user input — no matching record)

**Input Validation Errors:**
- Missing required field, invalid JSON in fields_to_update → `InputValidationError` (exit code 2, user input error — non-transient)

**Exit Code Guide:**
- Exit code 0: Successful execution
- Exit code 1: All runtime errors (authentication, authorization, connection, ServiceNow API errors, CMDB errors, not found)
- Exit code 2: Input validation error (missing required field, malformed user-provided JSON)

---

# Dependencies

## 1. External API Dependencies

**1. ServiceNow Table API — Incident**
- **Endpoint**: `{instance_url}/api/now/table/incident`
- **Purpose**: Create new Incident records (POST) and update existing Incident records (PUT)
- **Protocol**: HTTPS
- **Method**: POST (create), PUT (update by sys_id)
- **Authentication**: HTTP Basic Auth (`user:password`)
- **Response Format**: JSON
- **Data Retrieved/Sent**: Incident field values; response includes `sys_id`, `number`, and all incident fields

**2. ServiceNow Table API — RITM**
- **Endpoint**: `{instance_url}/api/now/table/sc_req_item/{sys_id}`
- **Purpose**: Update existing Request Item records
- **Protocol**: HTTPS
- **Method**: PUT
- **Authentication**: HTTP Basic Auth
- **Response Format**: JSON
- **Data Retrieved/Sent**: RITM field values; response includes `sys_id`, `number`

**3. ServiceNow Identification and Reconciliation Engine**
- **Endpoint**: `{instance_url}/api/now/identifyreconcile`
- **Purpose**: Create or update CMDB Configuration Items; prevents duplicates via identification rules
- **Protocol**: HTTPS
- **Method**: POST
- **Authentication**: HTTP Basic Auth
- **Response Format**: JSON
- **Data Retrieved/Sent**: Sends `items` array with `className` and `values`; receives `identificationResults` with `operation`, `sysId`, `errors`, `warnings`

**4. ServiceNow Table API — CMDB CI Table**
- **Endpoint**: `{instance_url}/api/now/table/{ci_class_table_name}`
- **Purpose**: Query Configuration Items by name, sys_id, or custom query
- **Protocol**: HTTPS
- **Method**: GET
- **Authentication**: HTTP Basic Auth
- **Response Format**: JSON
- **Data Retrieved/Sent**: Query parameters `sysparm_query`, `sysparm_fields`, `sysparm_limit`; response is `result` array of CI records

**5. ServiceNow Table API — DB Object (CI Class population)**
- **Endpoint**: `{instance_url}/api/now/table/sys_db_object`
- **Purpose**: Retrieve all available CMDB CI table names and labels for dynamic choice field population
- **Protocol**: HTTPS
- **Method**: GET
- **Authentication**: HTTP Basic Auth
- **Response Format**: JSON
- **Data Retrieved/Sent**: Query `name STARTSWITH cmdb_ci`, returns `name` and `label` fields; up to 1000 records

**General API Requirements:**
- ServiceNow minimum version: Tokyo (required for `identifyreconcile` endpoint availability)
- A valid ServiceNow username and password with permissions to create/update Incident, sc_req_item, and CMDB CI records; read access to `sys_db_object`
- All connections must use HTTPS

---

## 2. Python version dependency

Python `>= 3.11` as specified in `extension.yml`.

---

## 3. Target Platform

Linux (x86_64). C extension modules with a confirmed `manylinux_2_17_x86_64` wheel are viable. All dependencies selected for this extension are pure-Python, so no platform-specific wheel constraints apply.

---

## 4. Python Library Dependencies

**1. requests**
- **Purpose**: HTTP client for all ServiceNow REST API calls; handles Basic Auth headers, SSL/TLS, timeouts, session management, and response parsing
- **Version**: `==2.34.2`
- **Installation**: `pip install requests==2.34.2`
- **Usage**: Instantiated as a `requests.Session` in the ServiceNow API Client utility; used by all five actions and the dynamic choice field population
- **Features Used**: `Session`, `Session.get`, `Session.post`, `Session.put`, `Session.close`, Basic Auth via `HTTPBasicAuth`, timeout parameter, `response.json()`, `response.status_code`, `requests.exceptions.ConnectionError`, `requests.exceptions.Timeout`, `requests.exceptions.SSLError`

**2. tabulate**
- **Purpose**: ASCII table formatting for STDOUT output
- **Version**: `==0.10.0`
- **Installation**: `pip install tabulate==0.10.0`
- **Usage**: Used in the Output Table Formatter utility, called from all five action STDOUT output steps
- **Features Used**: `tabulate()` function with `tablefmt="rounded_outline"`

---

## 5. Python Standard Library Dependencies

**1. json**
- **Purpose**: JSON serialization and deserialization
- **Version**: Standard library (Python 3.11+)
- **Installation**: Built-in
- **Usage**: Parsing `incident_fields_to_update` and `ritm_fields_to_update` user input; serializing result objects for `cmdb_result_json` and `cmdb_results_json` output fields; serializing extension output
- **Features Used**: `json.loads()`, `json.dumps()`

**2. os**
- **Purpose**: Environment variable access
- **Version**: Standard library
- **Installation**: Built-in
- **Usage**: Reading `UE_HTTP_TIMEOUT` environment variable in the ServiceNow API Client
- **Features Used**: `os.environ.get()`

---

## 6. CLI Tool Dependencies

No Dependencies.

---

## 7. Environment Variables

**UE_HTTP_TIMEOUT** (integer, optional):
- **Purpose**: HTTP request timeout in seconds applied to all ServiceNow API calls
- **Default**: `30` seconds if not set or not a valid integer
- **Usage**: Read once during ServiceNow API Client initialization; applied to every HTTP request via the `timeout` parameter
- **Examples**: `30`, `60`, `120`
