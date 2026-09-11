"""
Create Incident action for the ServiceNow CMDB Universal Extension.

Creates a new Incident record in ServiceNow via the Table API and returns
the resulting sys_id, number, and key incident fields.
"""

import logging

from actions.output import ActionOutput
from exceptions import InputValidationError
from fields.input import InputFields
from fields.output import OutputFields
from manager import ExtensionManager
from utility import ServiceNowClient, print_table

logger = logging.getLogger("UNV")
extension_manager = ExtensionManager()


def create_incident(input_data: InputFields) -> ActionOutput:
    """
    Create a new Incident record in ServiceNow.

    Args:
        input_data: Validated input fields.

    Returns:
        ActionOutput with incident_sys_id, incident_number, and incident_result.

    Raises:
        InputValidationError: When short_description is empty.
        AuthenticationError: HTTP 401 from ServiceNow.
        AuthorizationError: HTTP 403 from ServiceNow.
        ServiceNowValidationError: HTTP 400/404 validation failures.
        ServiceNowBusinessRuleError: HTTP 400/422 business rule blocks.
        ConnectionError: Network or timeout failures.
    """
    logger.info("Starting create_incident action")

    # --- Step 1: Input validation ---
    short_desc: str = (
        input_data.short_description.value
        if input_data.short_description
        else ""
    )
    if not short_desc:
        raise InputValidationError("short_description is required for Create Incident")

    logger.debug(
        "Input: instance_url=%s, short_description=%s",
        input_data.instance_url.value if input_data.instance_url else None,
        short_desc,
    )

    # --- Step 2: Build request payload ---
    payload: dict = {"short_description": short_desc}

    optional_field_map = {
        "description": "description",
        "category": "category",
        "priority": "priority",
        "urgency": "urgency",
        "impact": "impact",
        "caller": "caller_id",
        "assignment_group": "assignment_group",
        "assigned_to": "assigned_to",
    }

    for attr_name, snow_field in optional_field_map.items():
        field_obj = getattr(input_data, attr_name, None)
        if field_obj and field_obj.value:
            payload[snow_field] = field_obj.value

    logger.debug("Incident creation payload keys: %s", list(payload.keys()))

    # --- Step 3: Initialize output tracking ---
    output_fields = OutputFields()
    output_fields.update(incident_number="Creating...")

    # --- Step 4: Execute API call ---
    instance_url: str = input_data.instance_url.value
    username: str = input_data.credential.user
    password: str = input_data.credential.password

    client = ServiceNowClient(instance_url, username, password)
    try:
        logger.info("Creating Incident via POST /api/now/table/incident")
        response_body: dict = client.post("/api/now/table/incident", payload)
    finally:
        client.close()

    # --- Step 5: Parse response ---
    result: dict = response_body.get("result", {})
    sys_id: str = str(result.get("sys_id", "") or "")
    number: str = str(result.get("number", "") or "")
    state: str = str(result.get("state", "") or "")
    priority: str = str(result.get("priority", "") or "")

    logger.info("Incident created: number=%s, sys_id=%s", number, sys_id)

    # --- Step 6: Update UI output fields ---
    output_fields.update(incident_number=number)

    # --- Step 7: Write STDOUT ---
    headers = ["Sys ID", "Number", "Short Description", "State", "Priority"]
    rows = [[sys_id, number, short_desc, state, priority]]
    print_table(headers, rows)

    logger.info("create_incident action completed: %s", number)

    # --- Step 8: Return ---
    incident_result: dict = {
        "sys_id": sys_id,
        "number": number,
        "short_description": short_desc,
        "state": state,
        "priority": priority,
    }

    return ActionOutput(
        incident_sys_id=sys_id,
        incident_number=number,
        incident_result=incident_result,
    )
