"""
Create/Update CI action for the ServiceNow CMDB Universal Extension.

Creates or updates a Configuration Item in ServiceNow CMDB exclusively via the
Identification and Reconciliation Engine (IRE) endpoint. IRE determines whether
to INSERT a new CI or UPDATE an existing CI based on ServiceNow identification
rules.
"""

import logging

from actions.output import ActionOutput
from exceptions import InputValidationError
from fields.input import InputFields
from fields.output import OutputFields
from manager import ExtensionManager
from utility import IREResult, ServiceNowClient, parse_ci_class, parse_ire_response, print_table

logger = logging.getLogger("UNV")
extension_manager = ExtensionManager()


def create_update_ci(input_data: InputFields) -> ActionOutput:
    """
    Create or update a CMDB Configuration Item via the ServiceNow IRE.

    Args:
        input_data: Validated input fields.

    Returns:
        ActionOutput with cmdb_action, cmdb_sys_id, cmdb_class, cmdb_name,
        and cmdb_status.

    Raises:
        InputValidationError: When ci_class or ci_name is empty.
        AuthenticationError: HTTP 401 from ServiceNow.
        AuthorizationError: HTTP 403 from ServiceNow.
        CmdbIdentificationError: IRE identification failure.
        CmdbReconciliationError: IRE reconciliation failure.
        ServiceNowValidationError: HTTP 400 or other API errors.
        ConnectionError: Network or timeout failures.
    """
    logger.info("Starting create_update_ci action")

    # --- Step 1: Input validation ---
    ci_class_display: str = (
        input_data.ci_class.value if input_data.ci_class else ""
    )
    raw_table_name: str = parse_ci_class(ci_class_display)
    if not raw_table_name:
        raise InputValidationError(
            "ci_class is required and must resolve to a valid ServiceNow table name"
        )

    ci_name_value: str = (
        input_data.ci_name.value if input_data.ci_name else ""
    )
    if not ci_name_value:
        raise InputValidationError("ci_name is required for Create/Update CI")

    logger.debug(
        "Input: ci_class=%s, raw_table=%s, ci_name=%s",
        ci_class_display,
        raw_table_name,
        ci_name_value,
    )

    # --- Step 2: Build IRE payload ---
    values: dict = {"name": ci_name_value}

    attributes_field = input_data.attributes
    if attributes_field and attributes_field.pairs:
        for pair in attributes_field.pairs:
            attr_name: str = pair.get("name", "") if isinstance(pair, dict) else ""
            attr_value = pair.get("value", "") if isinstance(pair, dict) else ""
            if attr_name and attr_value not in (None, "", "[]", "{}"):
                values[attr_name] = attr_value

    logger.debug("IRE values dict keys: %s", list(values.keys()))

    ire_payload: dict = {
        "items": [
            {
                "className": raw_table_name,
                "values": values,
            }
        ]
    }

    data_source_value: str = (
        input_data.data_source.value if input_data.data_source else ""
    )
    if data_source_value:
        ire_payload["source"] = data_source_value

    logger.debug("IRE payload source: %s", data_source_value or "(omitted)")

    # --- Step 3: Initialize output tracking ---
    output_fields = OutputFields()
    output_fields.update(cmdb_status="Processing...")

    # --- Step 4: Execute API call ---
    instance_url: str = input_data.instance_url.value
    username: str = input_data.credential.user
    password: str = input_data.credential.password

    client = ServiceNowClient(instance_url, username, password)
    try:
        logger.info("Calling IRE POST /api/now/identifyreconcile for class %s", raw_table_name)
        response_body: dict = client.post("/api/now/identifyreconcile", ire_payload)
    finally:
        client.close()

    # --- Step 5: Parse IRE response ---
    ire_result: IREResult = parse_ire_response(response_body)

    cmdb_action: str = ire_result.cmdb_action
    cmdb_sys_id: str = ire_result.cmdb_sys_id
    cmdb_class: str = ire_result.cmdb_class
    cmdb_status: str = ire_result.cmdb_status
    cmdb_name: str = ci_name_value  # IRE response may not echo name; use submitted value

    logger.info(
        "IRE result: action=%s, sys_id=%s, class=%s, status=%s",
        cmdb_action,
        cmdb_sys_id,
        cmdb_class,
        cmdb_status,
    )

    # --- Step 6: Update UI output fields ---
    output_fields.update(
        cmdb_action=cmdb_action,
        cmdb_sys_id=cmdb_sys_id,
        cmdb_class=cmdb_class,
        cmdb_name=cmdb_name,
        cmdb_status=cmdb_status,
    )

    # --- Step 7: Write STDOUT ---
    headers = ["Operation", "Sys ID", "CI Class", "CI Name", "Status"]
    rows = [[cmdb_action, cmdb_sys_id, cmdb_class, cmdb_name, cmdb_status]]
    print_table(headers, rows)

    logger.info(
        "create_update_ci action completed: %s %s (%s)",
        cmdb_action,
        cmdb_name,
        cmdb_class,
    )

    # --- Step 8: Return ---
    return ActionOutput(
        cmdb_action=cmdb_action,
        cmdb_sys_id=cmdb_sys_id,
        cmdb_class=cmdb_class,
        cmdb_name=cmdb_name,
        cmdb_status=cmdb_status,
    )
