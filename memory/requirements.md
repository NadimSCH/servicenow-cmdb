Enhance the existing Stonebranch ServiceNow Universal Integration with CMDB functionality.

The integration already supports Incident/RITM functionality.
Do NOT break or rewrite the existing Incident/RITM actions.

Add two new CMDB actions:

1. Create/Update CI
2. Get CI

The main use case is:

After a VM is created by Stonebranch, the VM details should be written into the ServiceNow CMDB.
If the CI already exists, it should be updated instead of creating a duplicate.

The integration should also be able to retrieve CI information from the CMDB and expose the returned values as Stonebranch task output fields.

============================================================
ACTION 1: CREATE/UPDATE CI
============================================================

Action name shown in the Universal Template:

Create/Update CI

Purpose:

Create a new Configuration Item in ServiceNow CMDB or update an existing CI using ServiceNow Identification and Reconciliation Engine (IRE).

Do NOT implement this as a simple direct POST to a cmdb_ci_* table unless there is a documented reason.

Preferred API:

POST /api/now/identifyreconcile

Use ServiceNow IRE so ServiceNow can identify whether the CI already exists and either:

- INSERT a new CI
- UPDATE the existing CI

This helps avoid duplicate CIs and respects ServiceNow CMDB identification/reconciliation rules.

============================================================
CREATE/UPDATE CI INPUT FIELDS
============================================================

Add these fields to the Universal Template:

Action:
- Create/Update CI

CI Class:
- Dynamic Choice
- Example values:
  - cmdb_ci_vm_instance
  - cmdb_ci_server
  - cmdb_ci_computer
  - other available cmdb_ci_* classes

CI Name:
- Text
- Required

Data Source / Discovery Source:
- Text or Choice
- Optional
- Example:
  Stonebranch

Attributes:
- Key/Value style input
- Must allow the user to map arbitrary ServiceNow CI attributes to Stonebranch variables

Example:

name            = ${vm_name}
ip_address      = ${vm_ip}
cpu_count       = ${vm_cpu}
ram             = ${vm_ram}
os              = ${vm_os}
environment     = ${environment}

The integration must support Stonebranch variables as values.

Example:

${ops_var_vm_name}
${ops_var_vm_ip}

or outputs from previous tasks.

============================================================
IRE PAYLOAD
============================================================

Build the ServiceNow IRE payload dynamically.

Example:

{
  "items": [
    {
      "className": "cmdb_ci_vm_instance",
      "values": {
        "name": "APP-PROD-01",
        "ip_address": "10.10.20.15",
        "cpu_count": "4",
        "ram": "8192"
      }
    }
  ]
}

Do not hardcode VM-specific attributes.

The className must come from the selected CI Class field.

The values object must be created dynamically from the provided Attributes mapping.

Remove empty values from the payload.

Do not send:

null
""
[]
{}

unless explicitly required.

============================================================
IRE RESULT HANDLING
============================================================

Parse the ServiceNow IRE response.

Return useful information as task output.

At minimum expose:

cmdb_action
cmdb_sys_id
cmdb_class
cmdb_name
cmdb_status

cmdb_action should indicate something like:

CREATED
UPDATED
MATCHED

depending on what the ServiceNow response provides.

If ServiceNow returns identification/reconciliation errors, expose the real ServiceNow error message.

Do not reduce every error to a generic authorization error.

============================================================
ACTION 2: GET CI
============================================================

Action name:

Get CI

Purpose:

Retrieve one or more Configuration Items from ServiceNow CMDB.

Support querying by:

CI Class
CI Name
sys_id
custom filter/query

============================================================
GET CI INPUT FIELDS
============================================================

CI Class:
- Dynamic Choice
- Required

Search By:
- Choice
- Name
- Sys ID
- Custom Query

Search Value:
- Text

Return Fields:
- Text or multi-value field
- Example:
  sys_id,name,ip_address,operational_status,cpu_count,ram

Limit:
- Integer
- Default: 1
- Optional

============================================================
GET CI API
============================================================

Prefer ServiceNow CMDB Instance API where appropriate.

If the existing integration architecture already uses the Table API and the CMDB Instance API adds unnecessary complexity, it is acceptable to use a read-only GET against the selected cmdb_ci_* table.

Example:

GET /api/now/table/cmdb_ci_vm_instance

with:

sysparm_query=name=APP-PROD-01
sysparm_fields=sys_id,name,ip_address,operational_status
sysparm_limit=1

Do not use direct Table API writes for Create/Update CI if IRE is available.

============================================================
GET CI OUTPUT
============================================================

For a single result, expose the requested fields as Stonebranch outputs.

Example:

cmdb_sys_id
cmdb_name
cmdb_ip_address
cmdb_operational_status
cmdb_cpu_count
cmdb_ram

Also expose the complete sanitized result as:

cmdb_result_json

For multiple results, return:

cmdb_results_json

Never expose ServiceNow authentication information.

============================================================
DYNAMIC CI CLASS FIELD
============================================================

Implement CI Class as a dynamic choice.

Query ServiceNow metadata/table information and return valid CMDB classes.

At minimum filter to tables beginning with:

cmdb_ci

Do not hardcode only VM classes.

The display value should be understandable.

Example:

VM Instance (cmdb_ci_vm_instance)
Server (cmdb_ci_server)
Computer (cmdb_ci_computer)

The internal value sent to ServiceNow should be the actual table/class name:

cmdb_ci_vm_instance

============================================================
OPTIONAL DYNAMIC ATTRIBUTE SUPPORT
============================================================

If practical within the existing Universal Integration framework, add a dynamic mechanism that can retrieve available fields for the selected CI Class.

For example:

CI Class:
cmdb_ci_vm_instance

Available fields:
name
ip_address
cpu_count
ram
os
environment
operational_status
...

However:

Do NOT make this a blocker for version 1.

Version 1 can use a generic Attributes key/value input.

============================================================
USE CASE EXAMPLE
============================================================

Workflow:

Task 1:
Create VM

Outputs:

vm_name = APP-PROD-01
vm_ip   = 10.10.20.15
vm_cpu  = 4
vm_ram  = 8192
vm_os   = Windows Server 2022

Task 2:
ServiceNow
Action = Create/Update CI

CI Class:
cmdb_ci_vm_instance

CI Name:
${vm_name}

Attributes:

name       = ${vm_name}
ip_address = ${vm_ip}
cpu_count  = ${vm_cpu}
ram        = ${vm_ram}
os         = ${vm_os}

Expected result:

If CI does not exist:
CREATE

If CI already exists:
UPDATE

No duplicate CI should be created if ServiceNow IRE identifies the existing CI.

============================================================
ARCHITECTURE
============================================================

Keep the current integration architecture.

Add clean methods/classes for CMDB functionality.

Suggested methods:

servicenow_api.py

create_update_ci(...)
get_ci(...)
get_cmdb_classes(...)

actions.py

create_update_ci_action(...)
get_ci_action(...)
get_cmdb_classes_dynamic_choice_action(...)

serializers:

CreateUpdateCIInputData
GetCIInputData

Do not put all logic directly into extension.py.

============================================================
ERROR HANDLING
============================================================

Reuse and improve the existing ServiceNow error-handling model.

Distinguish at minimum:

AUTHENTICATION_ERROR
AUTHORIZATION_ERROR
SERVICENOW_BUSINESS_RULE_ERROR
SERVICENOW_VALIDATION_ERROR
NOT_FOUND_ERROR
CONNECTION_ERROR
CMDB_IDENTIFICATION_ERROR
CMDB_RECONCILIATION_ERROR

Preserve the original safe ServiceNow error detail.

Do not expose:

passwords
OAuth tokens
Authorization headers
client secrets

============================================================
TESTS
============================================================

Add tests for:

1. Create/Update CI with valid VM attributes

2. IRE response for new CI
Expected:
cmdb_action = CREATED or equivalent

3. IRE response for existing CI
Expected:
cmdb_action = UPDATED or equivalent

4. Empty attribute values are excluded

5. Dynamic CI class lookup

6. Get CI by name

7. Get CI by sys_id

8. Get CI with custom query

9. Get CI with selected return fields

10. No result
Expected:
clear NOT_FOUND behavior

11. Multiple results

12. ServiceNow IRE identification failure

13. ServiceNow reconciliation failure

14. HTTP 401

15. HTTP 403

16. HTTP 400

17. Existing Incident functionality still passes

18. Existing RITM functionality still passes

Do not break existing actions.

============================================================
UI REQUIREMENTS
============================================================

Add these actions to the existing Action selector:

Create Incident
Update Incident
Update RITM
Create/Update CI
Get CI

Only show fields relevant to the selected action.

For Create/Update CI show:

CI Class
CI Name
Attributes
Data Source / Discovery Source

For Get CI show:

CI Class
Search By
Search Value
Return Fields
Limit

============================================================
IMPORTANT IMPLEMENTATION RULES
============================================================

Do NOT:

- hardcode one VM class
- hardcode one set of CI attributes
- create duplicate CIs manually
- use direct Table API write if IRE can be used
- delete existing Incident/RITM functionality
- expose credentials in logs
- silently ignore ServiceNow CMDB errors

============================================================
VERSIONING
============================================================

Bump the Universal Integration version to the next beta version.

Update:

extension.yml
template metadata
package metadata
README/changelog if present

============================================================
DELIVERABLE
============================================================

Before implementation, inspect the current integration and explain:

1. Current architecture
2. Which files need to change
3. How existing Incident/RITM functionality will remain untouched
4. How ServiceNow IRE will be integrated

Then implement:

- Create/Update CI
- Get CI
- Dynamic CI Class
- Generic attributes mapping
- Output fields
- Error handling
- Tests

Return:

1. Root cause/architecture analysis
2. Files changed
3. Code changes
4. Test results
5. Example Create/Update CI payload
6. Example Get CI request
7. Example task outputs
8. Packaged updated Universal Integration ZIP

Do not claim completion until all existing and new tests pass.