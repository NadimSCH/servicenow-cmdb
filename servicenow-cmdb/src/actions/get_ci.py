"""
Get CI action for the ServiceNow CMDB Universal Extension.

Retrieves one or more Configuration Items from ServiceNow CMDB using the
Table API. Supports search by Name, Sys ID, or Custom Query. Returns CI
attributes as both individual output fields and sanitized JSON strings.
"""

import logging

from actions.output import ActionOutput
from exceptions import InputValidationError, NotFoundError
from fields.input import InputFields
from fields.output import OutputFields
from manager import ExtensionManager
from utility import (
    ServiceNowClient,
    parse_ci_class,
    print_multi_result_note,
    print_table,
    sanitize_json,
)

logger = logging.getLogger("UNV")
extension_manager = ExtensionManager()

# Default fields returned when return_fields is empty
_DEFAULT_RETURN_FIELDS: str = (
    "sys_id,name,ip_address,operational_status,cpu_count,ram,os,short_description"
)

# Mapping from ServiceNow field name to ActionOutput attribute name
_FIELD_TO_OUTPUT_ATTR: dict = {
    "sys_id": "cmdb_sys_id",
    "name": "cmdb_name",
    "ip_address": "cmdb_ip_address",
    "operational_status": "cmdb_operational_status",
    "cpu_count": "cmdb_cpu_count",
    "ram": "cmdb_ram",
    "os": "cmdb_os",
    "short_description": "cmdb_short_description",
}

# Human-readable column headers for STDOUT table, keyed by ServiceNow field name
_FIELD_HEADERS: dict = {
    "sys_id": "Sys ID",
    "name": "Name",
    "ip_address": "IP Address",
    "operational_status": "Operational Status",
    "cpu_count": "CPU Count",
    "ram": "RAM",
    "os": "OS",
    "short_description": "Short Description",
}


def get_ci(input_data: InputFields) -> ActionOutput:
    """
    Retrieve one or more CMDB Configuration Items from ServiceNow.

    Args:
        input_data: Validated input fields.

    Returns:
        ActionOutput with cmdb_sys_id, cmdb_name, and any standard CI attribute
        fields present in the response. Also includes cmdb_result_json and
        optionally cmdb_results_json when multiple records are returned.

    Raises:
        InputValidationError: When ci_class or search_value is empty.
        NotFoundError: When the query returns zero records.
        AuthenticationError: HTTP 401 from ServiceNow.
        AuthorizationError: HTTP 403 from ServiceNow.
        ServiceNowValidationError: HTTP 400 or invalid table/query.
        ConnectionError: Network or timeout failures.
    """
    logger.info("Starting get_ci action")

    # --- Step 1: Input validation ---
    ci_class_display: str = (
        input_data.ci_class.value if input_data.ci_class else ""
    )
    raw_table_name: str = parse_ci_class(ci_class_display)
    if not raw_table_name:
        raise InputValidationError(
            "ci_class is required and must resolve to a valid ServiceNow table name"
        )

    search_value: str = (
        input_data.search_value.value if input_data.search_value else ""
    )
    if not search_value:
        raise InputValidationError("search_value is required for Get CI")

    search_by: str = (
        input_data.search_by.value if input_data.search_by else "Name"
    )

    logger.debug(
        "Input: ci_class=%s, table=%s, search_by=%s, search_value=%s",
        ci_class_display,
        raw_table_name,
        search_by,
        search_value,
    )

    # --- Step 2: Build query parameters ---
    if search_by == "Name":
        sysparm_query: str = "name=" + search_value
    elif search_by == "Sys ID":
        sysparm_query = "sys_id=" + search_value
    else:
        # Custom Query — pass as-is
        sysparm_query = search_value

    return_fields_raw: str = (
        input_data.return_fields.value if input_data.return_fields else ""
    )
    if return_fields_raw:
        sysparm_fields: str = ",".join(
            f.strip() for f in return_fields_raw.split(",")
        )
    else:
        sysparm_fields = _DEFAULT_RETURN_FIELDS

    limit_value: int = int(input_data.limit) if input_data.limit else 1

    params: dict = {
        "sysparm_query": sysparm_query,
        "sysparm_fields": sysparm_fields,
        "sysparm_limit": str(limit_value),
    }

    logger.debug("Query params: %s", params)

    # --- Step 3: Initialize output tracking ---
    output_fields = OutputFields()
    output_fields.update(cmdb_name="Querying...")

    # --- Step 4: Execute API call ---
    instance_url: str = input_data.instance_url.value
    username: str = input_data.credential.user
    password: str = input_data.credential.password

    client = ServiceNowClient(instance_url, username, password)
    try:
        path: str = "/api/now/table/%s" % raw_table_name
        logger.info("GET %s with query: %s", path, sysparm_query)
        response_body: dict = client.get(path, params=params)
    finally:
        client.close()

    # --- Step 5: Process results ---
    results: list = response_body.get("result", [])
    result_count: int = len(results)

    logger.info("Query returned %d record(s)", result_count)

    if result_count == 0:
        print("No CI found matching search criteria.")
        raise NotFoundError(
            "No CI found for [%s: %s]" % (search_by, search_value)
        )

    first_result: dict = results[0]

    # Redact credential values from output
    redact_set: set = set()
    if password:
        redact_set.add(password)
    if username:
        redact_set.add(username)

    # Sanitize the first result for JSON output
    result_json_str: str = sanitize_json(first_result, redact_values=redact_set or None)

    # Build the ActionOutput kwargs from resolved fields
    output_kwargs: dict = {}
    resolved_fields: list = [f.strip() for f in sysparm_fields.split(",")]

    for snow_field in resolved_fields:
        attr_name = _FIELD_TO_OUTPUT_ATTR.get(snow_field)
        if attr_name and snow_field in first_result:
            field_val = first_result[snow_field]
            if field_val is not None:
                output_kwargs[attr_name] = str(field_val)

    cmdb_sys_id: str = str(first_result.get("sys_id", "") or "")
    cmdb_name: str = str(first_result.get("name", "") or "")

    # --- Step 6: Update UI output fields ---
    output_fields.update(
        cmdb_sys_id=cmdb_sys_id,
        cmdb_name=cmdb_name,
        cmdb_result_json=result_json_str,
    )

    # --- Step 7: Write STDOUT ---
    headers = [
        _FIELD_HEADERS.get(f, f) for f in resolved_fields
    ]
    row = [str(first_result.get(f, "")) for f in resolved_fields]

    results_json_str: str = ""
    if result_count > 1:
        print_multi_result_note(result_count)
        print()
        results_json_str = sanitize_json(results, redact_values=redact_set or None)
        output_fields.update(cmdb_results_json=results_json_str)

    print_table(headers, [row])

    logger.info(
        "get_ci action completed: %d record(s), first=%s (%s)",
        result_count,
        cmdb_name,
        raw_table_name,
    )

    # --- Step 8: Return ---
    action_output = ActionOutput(
        cmdb_sys_id=cmdb_sys_id,
        cmdb_name=cmdb_name,
        cmdb_result_json=result_json_str,
        result_count=result_count,
        **{k: v for k, v in output_kwargs.items() if k not in ("cmdb_sys_id", "cmdb_name")},
    )

    if results_json_str:
        action_output.cmdb_results_json = results_json_str

    return action_output
