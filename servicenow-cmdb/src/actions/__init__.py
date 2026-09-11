"""Actions module — business logic implementations for the ServiceNow CMDB extension."""

from actions.output import ActionOutput
from actions.create_incident import create_incident
from actions.update_incident import update_incident
from actions.update_ritm import update_ritm
from actions.create_update_ci import create_update_ci
from actions.get_ci import get_ci

# Maps the value of the action choice field to its implementation function.
# Keys must match exactly the choice values defined in template.json.
ACTION_MAPPER = {
    "Create Incident": create_incident,
    "Update Incident": update_incident,
    "Update RITM": update_ritm,
    "Create/Update CI": create_update_ci,
    "Get CI": get_ci,
}
