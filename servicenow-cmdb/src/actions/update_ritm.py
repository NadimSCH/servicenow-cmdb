"""
Update RITM action for the ServiceNow CMDB Universal Extension.

Updates an existing Request Item (RITM) record in ServiceNow by sys_id
using the Table API.
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


def update_ritm(input_data: InputFields) -> ActionOutput:
    """
    Update an existing Request Item record in ServiceNow.

    Args:
        input_data: Validated input fields.

    Returns:
        ActionOutput with ritm_sys_id, ritm_number, and ritm_result.

    Raises:
        InputValidationError: When ritm_sys_id is empty or ritm_fields_to_update
            is not valid JSON.
        AuthenticationError: HTTP 401 from ServiceNow.
        AuthorizationError: HTTP 403 from ServiceNow.
        ServiceNowValidationError: HTTP 400/404/422 validation failures.
        ServiceNowBusinessRuleError: HTTP 400/422 business rule blocks.
        ConnectionError: Network or timeout failures.
    """
    logger.info("Starting update_ritm action")

    # --- Step 1: Input validation ---
    sys_id_input: str = (
        input_data.ritm_sys_id.value if input_data.ritm_sys_id else ""
    )
    if not sys_id_input:
        raise InputValidationError("ritm_sys_id is required for Update RITM")

    fields_raw: str = (
        input_data.ritm_fields_to_update.value
        if input_data.ritm_fields_to_update
        else ""
    )

    payload: dict
    if fields_raw:
        try:
            payload = json.loads(fields_raw)
        except (ValueError, TypeError) as exc:
            raise InputValidationError(
                "ritm_fields_to_update must be a valid JSON object"
            ) from exc
    else:
        payload = {}

    logger.debug(
        "Input: ritm_sys_id=%s, payload_keys=%s",
        sys_id_input,
        list(payload.keys()),
    )

    # --- Step 2: Initialize output tracking ---
    output_fields = OutputFields()
    output_fields.update(ritm_number="Updating...")

    # --- Step 3: Execute API call ---
    instance_url: str = input_data.instance_url.value
    username: str = input_data.credential.user
    password: str = input_data.credential.password

    client = ServiceNowClient(instance_url, username, password)
    try:
        path: str = "/api/now/table/sc_req_item/%s" % sys_id_input
        logger.info("Updating RITM via PUT %s", path)
        response_body: dict = client.put(path, payload)
    finally:
        client.close()

    # --- Step 4: Parse response ---
    result: dict = response_body.get("result", {})
    returned_sys_id: str = str(result.get("sys_id", "") or "")
    number: str = str(result.get("number", "") or "")
    state: str = str(result.get("state", "") or "")
    updated_on: str = str(result.get("sys_updated_on", "") or "")

    logger.info("RITM updated: number=%s, sys_id=%s", number, returned_sys_id)

    # --- Step 5: Update UI output fields ---
    output_fields.update(ritm_number=number)

    # --- Step 6: Write STDOUT ---
    headers = ["Sys ID", "Number", "State", "Updated On"]
    rows = [[returned_sys_id, number, state, updated_on]]
    print_table(headers, rows)

    logger.info("update_ritm action completed: %s", number)

    # --- Step 7: Return ---
    ritm_result: dict = {
        "sys_id": returned_sys_id,
        "number": number,
        "state": state,
        "sys_updated_on": updated_on,
    }

    return ActionOutput(
        ritm_sys_id=returned_sys_id,
        ritm_number=number,
        ritm_result=ritm_result,
    )
