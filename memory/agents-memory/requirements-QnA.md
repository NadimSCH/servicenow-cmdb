# Requirements Completeness Assessment

**Level: High Detail**

The requirements are comprehensive for the two new CMDB actions — precise API endpoints (POST `/api/now/identifyreconcile` for IRE, GET `/api/now/table/{class}` for queries), input/output field definitions, an 8-category error taxonomy, UI conditional visibility rules, an IRE payload example, and 18 test scenarios are all clearly specified. The use case example (VM creation → CMDB registration) eliminates ambiguity in the core business logic.

What is already well-established:
- Both CMDB action names, purposes, and APIs are unambiguous
- IRE payload structure and empty-value filtering rules are precise
- Output field names for Create/Update CI (`cmdb_action`, `cmdb_sys_id`, `cmdb_class`, `cmdb_name`, `cmdb_status`) are fully defined
- Dynamic CI Class display format (`VM Instance (cmdb_ci_vm_instance)`) is specified
- The 8 error categories are named and distinguish CMDB-specific failures from standard HTTP errors
- UI visibility rules (show fields per selected action) are fully described

The open decisions targeted by these questions are: implementation scope (Incident/RITM alongside CMDB), authentication mechanism, field-type choices for ambiguous inputs, and behavioral edge cases in Get CI.

---

# Platform Compatibility

**Platform Compatibility from Requirements**: Linux (x86_64) — confirmed in `memory/environment.md` (Build Platform: OS Linux, Architecture x86_64)

**Platform Compatibility Agreement**: Linux-only — `manylinux_2_17_x86_64` wheel compatibility applies; C extension modules with a confirmed `manylinux_2_17_x86_64` wheel are viable in addition to pure-Python modules.

---

# Python Modules and Versions

## Researched Modules

**requests**
- **Module Purpose**: HTTP client for all ServiceNow REST API calls — IRE endpoint, Table API queries (Get CI, CI class metadata, Incident/RITM), and authentication via Basic Auth headers
- **Version**: 2.34.2
- **Type**: Pure Python

**tabulate**
- **Module Purpose**: ASCII table formatting for human-readable STDOUT output; displays CI attribute results and operation summaries in a clean `rounded_outline` table format
- **Version**: 0.10.0
- **Type**: Pure Python

## Agreed Python Modules and Versions

| Module Name | Module Purpose | Version | Type |
|---|---|---|---|
| [To be filled once answers are applied] | | | |

---

# Question Rationale

The requirements are precise about APIs, field names, and error categories. The ten questions below target five areas that remain open:

1. **Implementation scope** — The workspace is a fresh skeleton; no existing Incident/RITM code is present. Without clarifying whether all 5 actions are built here, the implementation plan cannot be scoped.
2. **Authentication design** — No auth method is specified. The choice determines the credential field structure and how auth headers are built.
3. **Ambiguous input field types** — Two fields are described with "or" wording ("Text or Choice" for Data Source; "Key/Value style" for Attributes). Resolving these determines template.json field design.
4. **Get CI edge-case behavior** — No-result handling and multi-result individual-field population are not specified. These decisions affect return codes, output field population, and downstream workflow integration.
5. **Operational configuration** — HTTP timeout and STDOUT format are design decisions that affect dependencies and user experience.

---

# Clarifying Questions for Requirements Refinement

## Critical Decision Path Questions

**Question 1**: What is the scope of actions to implement in this workspace?

- **Question Type**: New Discussion Topic
- **Context & Resources**: The requirements reference "the existing Stonebranch ServiceNow Universal Integration that already supports Incident/RITM functionality." However, the current workspace (`extension-code/` and `servicenow-cmdb/`) contains only a fresh extension skeleton — an empty `ACTION_MAPPER`, placeholder action choices ("print", "log"), and no ServiceNow API code. The UI requirements section lists all five actions together in the final Action selector: `Create Incident, Update Incident, Update RITM, Create/Update CI, Get CI`. Test cases 17 and 18 explicitly expect "Existing Incident functionality still passes" and "Existing RITM functionality still passes." Since no Incident/RITM code exists in this workspace, a decision is needed on scope before implementation begins.

  Available options:

  - **O1 — Implement all 5 actions from scratch in this workspace**: Build `Create Incident`, `Update Incident`, `Update RITM` (using standard ServiceNow Table API: `POST /api/now/table/incident`, `PUT /api/now/table/incident/{sys_id}`, `PUT /api/now/table/sc_req_item/{sys_id}`), alongside `Create/Update CI` and `Get CI`. All 18 test cases (including 17 and 18) are covered in this workspace.
  - **O2 — Implement CMDB actions only (Create/Update CI and Get CI)**: The Incident/RITM actions are out of scope for this workspace. Tests 17 and 18 are deferred. The final extension will have only 2 actions in the Action selector.

- **Question Dependencies**: All other questions are compatible with either option. Option O2 removes Incident/RITM field requirements from scope.
- **Recommended Answer**: O1 — Implement all 5 actions from scratch. The workspace is a clean slate with no external code to integrate. Building all 5 actions is the only self-contained path that satisfies all 18 stated test cases and produces the complete 5-action integration described in the UI requirements.
- **Rationale**: O2 produces an incomplete integration that fails tests 17 and 18 and does not match the "Add these actions to the existing Action selector" UI requirement. O1 infers standard Incident/RITM fields from the ServiceNow Table API, which is well-documented and straightforward to implement alongside the CMDB actions.
- **Trade-offs**: O1 requires implementing Incident/RITM field specifications from inference (field names, required vs. optional) since the requirements only describe CMDB fields in detail. O2 is narrower but leaves the integration incomplete.
- **Requirement Impact**: If O2 is selected, remove test cases 17–18, and remove `Create Incident`, `Update Incident`, `Update RITM` from the Action choice field.
- **User's Answer**: O1 — Implement all 5 actions from scratch

---

**Question 2**: What authentication mechanism should the ServiceNow integration use?

- **Question Type**: New Discussion Topic
- **Context & Resources**: The requirements specify the extension must authenticate to ServiceNow and handle `HTTP 401` (authentication failure) and `HTTP 403` (authorization failure) responses distinctly as `AUTHENTICATION_ERROR` and `AUTHORIZATION_ERROR`. ServiceNow supports multiple authentication mechanisms. The choice determines the credential field structure and how the extension builds request headers.

  **Option comparison:**

  | Feature | O1 — Basic Auth | O2 — OAuth 2.0 Client Credentials |
  |---|---|---|
  | UAC Credential fields needed | 1 (username + password) | 1 (client_id + client_secret) + 1 Text field (token URL) |
  | ServiceNow setup required | None — works out of the box | Must create OAuth Application in ServiceNow |
  | Token lifecycle | No tokens — credentials sent per request | Access token obtained and refreshed |
  | Security | Password in header (HTTPS mitigates) | Tokens expire; no password in requests |
  | Implementation complexity | Low | Moderate (token fetch, refresh, caching) |
  | Most common for on-prem | Yes | Less common for on-prem automation |

  ServiceNow Basic Authentication documentation: https://developer.servicenow.com/dev.do#!/guides/tokyo/application-development/api-reference/rest-api-authentication

  UAC Credential field mapping:
  - Basic Auth → `user` attribute (ServiceNow username) + `password` attribute (ServiceNow password) → single Credential field
  - OAuth Client Credentials → `user` attribute (client_id) + `password` attribute (client_secret) → single Credential field + Text field for OAuth token URL

- **Question Dependencies**: None — foundational design decision
- **Recommended Answer**: O1 — Basic Authentication (single Credential field with `user` = ServiceNow username, `password` = ServiceNow password)
- **Rationale**: Basic Auth is universally supported on all ServiceNow instances without additional configuration, requires a single credential field, and eliminates token refresh complexity. The connection is always HTTPS (required by ServiceNow), which protects credentials in transit. This matches the most common pattern for on-premise ServiceNow automation integrations.
- **Trade-offs**: Basic Auth sends credentials on every request (mitigated by HTTPS and ServiceNow's enforcement of TLS). OAuth provides short-lived tokens that reduce exposure window but require ServiceNow OAuth app setup, token fetch logic, and expiry handling — significantly more complex for the same functional result.
- **Requirement Impact**: None — the requirements do not specify an auth method; Basic Auth satisfies all HTTP 401/403 test cases.
- **User's Answer**: O1 — Basic Authentication

---

**Question 3**: Which Python HTTP library should handle all ServiceNow API calls?

- **Question Type**: New Discussion Topic
- **Context & Resources**: The extension makes multiple types of HTTP calls to ServiceNow: `POST` to IRE endpoint, `GET` to Table API for CI queries and class metadata, and optionally `POST`/`PUT` for Incident/RITM. Two widely-used pure-Python HTTP libraries are viable on Linux:

  | Feature | `requests==2.34.2` | `httpx` (latest) |
  |---|---|---|
  | Type | Pure Python | Pure Python |
  | Platform compatibility | All platforms | All platforms |
  | SSL/CA bundle env var | `REQUESTS_CA_BUNDLE` | `SSL_CERT_FILE` |
  | Timeout granularity | Connect + read | Per-phase (connect, read, write, pool) |
  | Async support | No (sync only) | Yes (sync + async) |
  | UAC architect recommendation | Preferred | Not preferred |
  | Ecosystem adoption in UAC | Very common | Less common |

  Requests library documentation: https://requests.readthedocs.io/en/latest/
  UAC architect notes state: *"Prefer requests over httpx (broader wheel availability)"*

- **Question Dependencies**: None
- **Recommended Answer**: O1 — `requests==2.34.2`
- **Rationale**: Explicitly recommended by UAC architect notes. All ServiceNow API calls in this integration are synchronous — no async benefit from httpx. The simpler requests API reduces implementation surface. Consistent with the broader UAC extension ecosystem.
- **Trade-offs**: `requests` has basic connect + read timeout; `httpx` offers finer control. For ServiceNow REST API calls (which complete in seconds), basic timeout is sufficient. `httpx` also uses a different CA bundle environment variable (`SSL_CERT_FILE` vs `REQUESTS_CA_BUNDLE`), which can confuse operators configuring SSL in enterprise environments.
- **Requirement Impact**: Add `requests==2.34.2` to `requirements.txt`.
- **User's Answer**: O1 — `requests==2.34.2`

---

## Essential Input/Output Questions

**Question 4**: How should the CI Attributes field collect key-value attribute mappings for Create/Update CI?

- **Question Type**: Clarification on existing requirement
- **Context & Resources**: The "Create/Update CI" action requires users to map ServiceNow CI attribute names to values — including Stonebranch workflow variables. The requirements describe this as "Key/Value style input" and give this example:
  ```
  name       = ${ops_var_vm_name}
  ip_address = ${ops_var_vm_ip}
  cpu_count  = ${ops_var_vm_cpu}
  ```
  UAC supports two field types for this pattern:

  **Array Field** (`"Array Field 1-4"`): A UI table with two configurable column titles (e.g., "Attribute Name" and "Attribute Value"). Users click `+` to add rows. Each row is one key-value pair. UAC substitutes variable references in the value column (`${ops_var_vm_name}`) at launch time before the extension runs. Returned to extension code as `[{"name": "ip_address", "value": "10.10.20.15"}]`. No parsing needed — the data arrives structured.

  **Large Text Field**: A multi-line text area where users type `key=value` per line. Flexible and familiar if users are accustomed to properties-file syntax. Requires the extension to split lines, strip whitespace, and handle edge cases (empty lines, lines without `=`, duplicate keys).

  UAC Array Field reference in architect notes: *"Use for variable-length lists of name-value pairs. From User Interface perspective it is a table with two columns (name, value) of configurable title."*

- **Question Dependencies**: None
- **Recommended Answer**: O1 — Array Field with column titles "Attribute Name" and "Attribute Value"
- **Rationale**: The UAC Array Field is the native, purpose-built solution for key-value pairs. It eliminates format parsing errors, provides clear UI guidance (separate columns prevent ambiguity about the `=` separator), and handles Stonebranch variable substitution automatically. The IRE payload construction simply iterates the list of `{name, value}` pairs — no custom parsing logic required.
- **Trade-offs**: Array Field requires one `+` click per attribute row vs. pasting a block of text. For users who prefer bulk-paste, Large Text is more convenient but introduces parsing edge cases and potential errors in variable substitution detection.
- **Requirement Impact**: The example format in requirements (`name = ${vm_name}`) maps directly to Array Field rows where column 1 = `name` and column 2 = `${ops_var_vm_name}`. No change to the business logic specification.
- **User's Answer**: O1 — Array Field with columns "Attribute Name" / "Attribute Value"

---

**Question 5**: Should the "Data Source / Discovery Source" field for Create/Update CI use a free-text input or predefined choices?

- **Question Type**: Clarification on existing requirement
- **Context & Resources**: The ServiceNow IRE endpoint uses a Discovery Source (also called `source` in IRE payloads in some ServiceNow versions) to identify which system created or updated a CI. ServiceNow uses this value in CMDB reconciliation rules to determine which source is authoritative for each CI attribute. Each customer's ServiceNow instance may have its own set of configured discovery sources depending on their CMDB design. Common values include: `Stonebranch`, `ServiceNow Discovery`, `SCCM`, `Puppet`, `Chef`, `Manual`.

  ServiceNow IRE API reference: https://developer.servicenow.com/dev.do#!/reference/api/tokyo/rest/c_IdentifyReconcileAPI

  The requirements mark this field as **Optional** and provide `Stonebranch` as the primary example value.

  Options:
  - **O1 — Text Field** with default value `Stonebranch`: Open input, any valid source name accepted. Accommodates customer-specific reconciliation source names without requiring template changes.
  - **O2 — Choice Field** with predefined options (e.g., `Stonebranch`, `ServiceNow Discovery`, `SCCM`, `Puppet`, `Manual`): Prevents typos but may not cover all valid source names in a customer's ServiceNow instance.

- **Question Dependencies**: None
- **Recommended Answer**: O1 — Text Field with default value `Stonebranch`
- **Rationale**: ServiceNow CMDB reconciliation source names are customer-specific — different instances configure different sources. A text field with the `Stonebranch` default satisfies the primary use case while remaining flexible for customers with custom reconciliation configurations. A choice field would need customer-specific customization to be useful.
- **Trade-offs**: Text field allows any value including ones not configured in ServiceNow (IRE may reject unknown sources in strict reconciliation configurations). Choice field prevents invalid values but restricts flexibility.
- **Requirement Impact**: Field is Optional with `Stonebranch` as the default value in template.json. No change to business logic — the value is passed as-is in the IRE payload `source` or `discoverySource` field.
- **User's Answer**: O1 — Text Field with default value `Stonebranch`

---

**Question 6**: When "Get CI" finds no matching Configuration Items, should the task succeed or fail?

- **Question Type**: Clarification on existing requirement
- **Context & Resources**: The "Get CI" action queries ServiceNow CMDB by Name, Sys ID, or custom query. If no CI matches the search criteria, the behavior affects how downstream workflow tasks react. This is a workflow orchestration design decision.

  The requirements explicitly include test case 10: *"No result — Expected: clear NOT_FOUND behavior."* This language strongly implies failure rather than silent success.

  **Impact on workflow design:**

  | Behavior | Workflow effect | How user handles "not found" |
  |---|---|---|
  | **O1 — Fail (rc=1)** with `NOT_FOUND_ERROR` | Downstream tasks do NOT run (unless error handling configured) | Add UAC error handler or workflow branch for "not found" |
  | **O2 — Succeed (rc=0)** with empty output fields | Downstream tasks run unconditionally | Check `${ops_var_cmdb_sys_id}` value in downstream task condition |

  UAC architect notes on return codes: *"rc=1: Failed execution (covers all error scenarios apart from validation errors)."*

- **Question Dependencies**: None
- **Recommended Answer**: O1 — Task fails (rc=1) with `NOT_FOUND_ERROR` status description and empty result output fields
- **Rationale**: Test case 10 explicitly names this "clear NOT_FOUND behavior" — which aligns with a failure response. For workflow automation, a failure provides a clear, unambiguous signal that the CI lookup produced no result, triggering UAC's built-in error handling rather than requiring conditional field-value checks in downstream tasks. This is the safer default for production workflows.
- **Trade-offs**: O1 requires users to add explicit error handling (UAC "On Failure" task or workflow branch) when "not found" is acceptable (e.g., "create CI if not found" pattern). O2 is more lenient but puts the burden of detecting "no result" on downstream conditional logic.
- **Requirement Impact**: `NOT_FOUND_ERROR` is already listed in the error handling section; this confirms it maps to `rc=1`. STDOUT should include a clear message: `"No CI found matching search criteria."` Status description: `"Not Found: No CI found for [search criteria]"`.
- **User's Answer**: O1 — Task fails (rc=1) with NOT_FOUND_ERROR

---

**Question 7**: When Get CI returns multiple Configuration Items, how should individual output fields be populated?

- **Question Type**: New Discussion Topic
- **Context & Resources**: The requirements define two scenarios for Get CI output:
  - **Single result**: Individual output fields (`cmdb_sys_id`, `cmdb_name`, `cmdb_ip_address`, `cmdb_operational_status`, `cmdb_cpu_count`, `cmdb_ram`) are populated, plus `cmdb_result_json` with the complete CI object.
  - **Multiple results**: `cmdb_results_json` is populated with the array of all matching CIs.

  What happens to the individual output fields when multiple results are returned is not specified. Individual output fields are accessible as UAC variables in downstream tasks (e.g., `${ops_var_cmdb_sys_id}`). This is valuable for single-CI workflows.

  Options:
  - **O1 — Populate individual fields from the first result + `cmdb_results_json` for all results**: The first CI's attributes fill individual output fields. `cmdb_results_json` contains the complete array. A STDOUT note indicates "Showing first of N results."
  - **O2 — Leave individual fields empty for multiple results; populate only `cmdb_results_json`**: Clean separation — individual fields are meaningful only for single-result queries. Multi-result callers must parse `cmdb_results_json`.

- **Question Dependencies**: None
- **Recommended Answer**: O1 — Populate individual fields from the first result + `cmdb_results_json` for all results
- **Rationale**: Downstream workflow tasks typically need direct variable access to CI attributes (e.g., use `${ops_var_cmdb_sys_id}` in a subsequent update task). Populating from the first result enables this without requiring JSON parsing in downstream tasks. The Limit field defaults to 1 for most use cases; when users set Limit > 1, `cmdb_results_json` provides the full dataset. A STDOUT note ("1 of N results shown in output fields") makes the behavior transparent.
- **Trade-offs**: O1 may cause confusion if users don't notice that individual fields only reflect the first result when multiple are returned. O2 is unambiguous but forces all multi-result callers to implement JSON extraction logic.
- **Requirement Impact**: Add a STDOUT note when result count > 1: `"Returning N results. Individual output fields reflect the first result. Full results in cmdb_results_json."` Both `cmdb_result_json` (first result) and `cmdb_results_json` (all results) are populated when count > 1.
- **User's Answer**: O1 — Individual fields from first result + cmdb_results_json for all results

---

**Question 8**: When "Return Fields" is left empty in Get CI, what fields should be returned from ServiceNow?

- **Question Type**: New Discussion Topic
- **Context & Resources**: The Get CI action passes the "Return Fields" value as ServiceNow's `sysparm_fields` query parameter. This controls which CI attributes are included in the response. If the user leaves Return Fields empty and `sysparm_fields` is omitted from the request, ServiceNow returns ALL available fields for the CI record — which can be 100+ fields across CMDB base and extension tables, including many system and audit fields rarely useful to operators.

  ServiceNow Table API documentation on `sysparm_fields`: https://developer.servicenow.com/dev.do#!/reference/api/tokyo/rest/c_TableAPI#table-GET

  Options:
  - **O1 — Return ALL fields when Return Fields is empty**: Maximum completeness; response will include 100+ fields (system, audit, custom). `cmdb_result_json` becomes very large.
  - **O2 — Return a standard default set when Return Fields is empty**: For example `sys_id, name, ip_address, operational_status, cpu_count, ram, os, short_description`. Covers the most common CMDB use case (VM details) without noise. Users override by specifying Return Fields.
  - **O3 — Require Return Fields (validation error if empty)**: Forces explicit field selection. Prevents accidental large responses but adds friction for quick lookups.

- **Question Dependencies**: None
- **Recommended Answer**: O2 — Return a standard default set: `sys_id, name, ip_address, operational_status, cpu_count, ram, os, short_description`
- **Rationale**: Returning all fields produces large, noisy responses that bloat the UAC database and make `cmdb_result_json` difficult to use in downstream tasks. A sensible default covers the primary use case (VM CI details matching the requirements example) while remaining easy to override. This follows the UAC architect pattern for "Large Output Safety Net" — keeping inline output manageable by default.
- **Trade-offs**: O2 may omit CI attributes the user expects to see by default (e.g., environment, location, asset_tag). Users must specify Return Fields to access non-default attributes. O1 returns everything but creates large, hard-to-navigate JSON. O3 is most explicit but adds friction for common quick lookups.
- **Requirement Impact**: Document the default field set in the "Return Fields" field hint: `"Comma-separated CI fields to return. Default: sys_id, name, ip_address, operational_status, cpu_count, ram, os, short_description"`. STDOUT should indicate when defaults are applied.
- **User's Answer**: O2 — Return standard default set: `sys_id, name, ip_address, operational_status, cpu_count, ram, os, short_description`

---

## Operational Configuration Questions

**Question 9**: What format should STDOUT output use for Create/Update CI and Get CI results?

- **Question Type**: New Discussion Topic
- **Context & Resources**: The UAC architect notes state: *"ASCII Table format is preferable when information can be printed nicely in rows or in columns using well known python libraries. Use tablefmt='rounded_outline'."*

  CI attribute results (key-value pairs) and operation summaries are well-suited to tabular display. The `tabulate` library (version 0.10.0, pure Python, no platform constraint) is the standard choice for this in the UAC extension ecosystem.

  **Example STDOUT with tabulate (O1 — `rounded_outline` format):**
  ```
  Create/Update CI — Success

  ╭──────────────────┬────────────────────────────────────╮
  │ Field            │ Value                              │
  ├──────────────────┼────────────────────────────────────┤
  │ Action           │ CREATED                            │
  │ CI Class         │ cmdb_ci_vm_instance                │
  │ CI Name          │ APP-PROD-01                        │
  │ Sys ID           │ abc123...                          │
  │ Status           │ Success                            │
  ╰──────────────────┴────────────────────────────────────╯
  ```

  **Example STDOUT with simple text (O2):**
  ```
  Create/Update CI — Success
  Action  : CREATED
  CI Class: cmdb_ci_vm_instance
  CI Name : APP-PROD-01
  Sys ID  : abc123...
  Status  : Success
  ```

  Options:
  - **O1 — ASCII table using `tabulate==0.10.0`**: Pure Python, explicitly recommended by UAC architect notes, significantly better readability for operators monitoring task execution. Adds one pure-Python dependency.
  - **O2 — Simple formatted key-value text**: No additional dependency. Slightly less readable but avoids any library dependency.

- **Question Dependencies**: None
- **Recommended Answer**: O1 — ASCII table using `tabulate==0.10.0` with `tablefmt="rounded_outline"`
- **Rationale**: UAC architect notes explicitly recommend tabulate with `rounded_outline` format for tabular data. The library is pure Python and platform-agnostic, so it introduces no compatibility risk. It significantly improves readability for operators reviewing task output in the UAC UI. The dependency is minimal (a single small pure-Python package).
- **Trade-offs**: O1 adds one dependency to `requirements.txt`. O2 avoids any dependency but produces less readable output, especially for Get CI where many CI attributes are displayed.
- **Requirement Impact**: Add `tabulate==0.10.0` to `requirements.txt`.
- **User's Answer**: O1 — ASCII table using tabulate==0.10.0

---

**Question 10**: How should the HTTP request timeout to ServiceNow be configured?

- **Question Type**: New Discussion Topic
- **Context & Resources**: Network calls to ServiceNow can be slow during peak usage, maintenance windows, or from geographically distant UAC agents. Without a timeout, the extension can hang indefinitely. There are two approaches aligned with UAC architecture:

  **`UE_HTTP_TIMEOUT` environment variable** (O1): Set at the UAC Agent level, Business Services level, or individual Task Definition environment variable. All tasks using this extension on the same agent share the same timeout. Code defaults to 30 seconds if the variable is not set. Operators tune without modifying the task template. UAC architect notes state: *"Be in favor of environment variables for input parameters that are not commonly tuned and/or have some sensible defaults like HTTP Client Timeouts (UE_HTTP_TIMEOUT)."*

  **Integer template field** "HTTP Timeout (seconds)" (O2): Visible in the task definition UI. Each task definition can have its own timeout. Most useful when different task definitions legitimately need different timeouts (e.g., a quick health check vs. a large query).

  Options:
  - **O1 — `UE_HTTP_TIMEOUT` environment variable** (agent or task-level, not visible in template UI, code default: 30 seconds)
  - **O2 — Integer template field** "HTTP Timeout (seconds)" with default value 30, visible in the task form

- **Question Dependencies**: None
- **Recommended Answer**: O1 — `UE_HTTP_TIMEOUT` environment variable with a 30-second code default
- **Rationale**: UAC architect notes explicitly recommend the environment variable approach for timeout parameters. HTTP timeout is an operational tuning knob that rarely needs per-task customization — a 30-second default covers the vast majority of ServiceNow API calls. Keeping it out of the template UI reduces clutter and follows the principle of sensible defaults.
- **Trade-offs**: O1 requires operators to know the environment variable name to change it; cannot be set per-task without creating task-level environment variable overrides. O2 makes it visible and per-task configurable but adds a field most users will never change from the default, adding noise to the template form.
- **Requirement Impact**: Document `UE_HTTP_TIMEOUT` in the template description or field hints. Code: `timeout = int(os.environ.get("UE_HTTP_TIMEOUT", 30))`.
- **User's Answer**: O1 — UE_HTTP_TIMEOUT environment variable (default 30 seconds)
