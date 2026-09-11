"""
Update Incident action for the ServiceNow CMDB Universal Extension.

Updates an existing Incident record in ServiceNow by sys_id using the Table API.
"""

import json
import logging

from actions.output import ActionOutput
from exceptions import InputValidationError
from fields.input import InputFields
from fields.output import OutputFields
from manager import ExtensionManager
from utility import ServiceNowClient, print_table

logger = logging.getLogger("UNV")
extension_manager = ExtensionManager()


def update_incident(input_data: InputFields) -> ActionOutput:
    """
    Update an existing Incident record in ServiceNow.

    Args:
        input_data: Validated input fields.

    Returns:
        ActionOutput with incident_sys_id, incident_number, and incident_result.

    Raises:
        InputValidationError: When incident_sys_id is empty or fields_to_update
            is not valid JSON.
        AuthenticationError: HTTP 401 from ServiceNow.
        AuthorizationError: HTTP 403 from ServiceNow.
        ServiceNowValidationError: HTTP 400/404/422 validation failures.
        ServiceNowBusinessRuleError: HTTP 400/422 business rule blocks.
        ConnectionError: Network or timeout failures.
    """
    logger.info("Starting update_incident action")

    # --- Step 1: Input validation ---
    sys_id_input: str = (
        input_data.incident_sys_id.value if input_data.incident_sys_id else ""
    )
    if not sys_id_input:
        raise InputValidationError("incident_sys_id is required for Update Incident")

    fields_raw: str = (
        input_data.incident_fields_to_update.value
        if input_data.incident_fields_to_update
        else ""
    )

    payload: dict
    if fields_raw:
        try:
            payload = json.loads(fields_raw)
        except (ValueError, TypeError) as exc:
            raise InputValidationError(
                "incident_fields_to_update must be a valid JSON object"
            ) from exc
    else:
        payload = {}

    logger.debug(
        "Input: incident_sys_id=%s, payload_keys=%s",
        sys_id_input,
        list(payload.keys()),
    )

    # --- Step 2: Initialize output tracking ---
    output_fields = OutputFields()
    output_fields.update(incident_number="Updating...")

    # --- Step 3: Execute API call ---
    instance_url: str = input_data.instance_url.value
    username: str = input_data.credential.user
    password: str = input_data.credential.password

    client = ServiceNowClient(instance_url, username, password)
    try:
        path: str = "/api/now/table/incident/%s" % sys_id_input
        logger.info("Updating Incident via PUT %s", path)
        response_body: dict = client.put(path, payload)
    finally:
        client.close()

    # --- Step 4: Parse response ---
    result: dict = response_body.get("result", {})
    returned_sys_id: str = str(result.get("sys_id", "") or "")
    number: str = str(result.get("number", "") or "")
    state: str = str(result.get("state", "") or "")
    updated_on: str = str(result.get("sys_updated_on", "") or "")

    logger.info("Incident updated: number=%s, sys_id=%s", number, returned_sys_id)

    # --- Step 5: Update UI output fields ---
    output_fields.update(incident_number=number)

    # --- Step 6: Write STDOUT ---
    headers = ["Sys ID", "Number", "State", "Updated On"]
    rows = [[returned_sys_id, number, state, updated_on]]
    print_table(headers, rows)

    logger.info("update_incident action completed: %s", number)

    # --- Step 7: Return ---
    incident_result: dict = {
        "sys_id": returned_sys_id,
        "number": number,
        "state": state,
        "sys_updated_on": updated_on,
    }

    return ActionOutput(
        incident_sys_id=returned_sys_id,
        incident_number=number,
        incident_result=incident_result,
    )
