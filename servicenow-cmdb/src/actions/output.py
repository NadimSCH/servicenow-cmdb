"""
ActionOutput dataclass for the ServiceNow CMDB Universal Extension.

Returned by every action function. Carries the data that extension.py uses
to populate the extension output (unv_output) and the OutputFields UI update.

There are no stdout_options / output_options control fields in this extension:
STDOUT printing is performed inside each action using the utility print_table
helpers before the ActionOutput is returned.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class ActionOutput:
    """
    Output from an action function.

    Fields cover all five actions; unused fields remain None and are excluded
    from to_dict(). print_output() is a no-op for this extension because each
    action prints its own ASCII table directly via utility helpers.
    """

    # --- Create Incident / Update Incident outputs ---
    incident_sys_id: Optional[str] = None
    incident_number: Optional[str] = None

    # --- Incident result snapshot (written to extension output) ---
    incident_result: Optional[Dict[str, Any]] = None

    # --- Update RITM outputs ---
    ritm_sys_id: Optional[str] = None
    ritm_number: Optional[str] = None

    # --- RITM result snapshot ---
    ritm_result: Optional[Dict[str, Any]] = None

    # --- Create/Update CI outputs ---
    cmdb_action: Optional[str] = None
    cmdb_sys_id: Optional[str] = None
    cmdb_class: Optional[str] = None
    cmdb_name: Optional[str] = None
    cmdb_status: Optional[str] = None

    # --- Get CI outputs ---
    cmdb_ip_address: Optional[str] = None
    cmdb_operational_status: Optional[str] = None
    cmdb_cpu_count: Optional[str] = None
    cmdb_ram: Optional[str] = None
    cmdb_os: Optional[str] = None
    cmdb_short_description: Optional[str] = None
    cmdb_result_json: Optional[str] = None
    cmdb_results_json: Optional[str] = None
    result_count: Optional[int] = None

    def print_output(self) -> None:
        """
        No-op: each action prints its own STDOUT via utility helpers.

        STDOUT output (ASCII tables) is rendered and printed inside each action
        function using print_table() and print_record_table() from utility.py
        before this ActionOutput is returned. This method exists to satisfy the
        interface contract expected by extension.py.
        """

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize non-None fields to a plain dict for the extension output.

        Returns:
            Dict containing only fields with non-None values, suitable for
            use as the ``result`` payload in the extension's unv_output.
        """
        output: Dict[str, Any] = {}

        # --- Incident fields ---
        if self.incident_sys_id is not None:
            output["sys_id"] = self.incident_sys_id
        if self.incident_number is not None:
            output["number"] = self.incident_number
        if self.incident_result is not None:
            output["result"] = self.incident_result

        # --- RITM fields ---
        if self.ritm_sys_id is not None:
            output["sys_id"] = self.ritm_sys_id
        if self.ritm_number is not None:
            output["number"] = self.ritm_number
        if self.ritm_result is not None:
            output["result"] = self.ritm_result

        # --- Create/Update CI fields ---
        if self.cmdb_action is not None:
            output["cmdb_action"] = self.cmdb_action
        if self.cmdb_sys_id is not None:
            output["cmdb_sys_id"] = self.cmdb_sys_id
        if self.cmdb_class is not None:
            output["cmdb_class"] = self.cmdb_class
        if self.cmdb_name is not None:
            output["cmdb_name"] = self.cmdb_name
        if self.cmdb_status is not None:
            output["cmdb_status"] = self.cmdb_status

        # --- Get CI fields ---
        if self.cmdb_ip_address is not None:
            output["cmdb_ip_address"] = self.cmdb_ip_address
        if self.cmdb_operational_status is not None:
            output["cmdb_operational_status"] = self.cmdb_operational_status
        if self.cmdb_cpu_count is not None:
            output["cmdb_cpu_count"] = self.cmdb_cpu_count
        if self.cmdb_ram is not None:
            output["cmdb_ram"] = self.cmdb_ram
        if self.cmdb_os is not None:
            output["cmdb_os"] = self.cmdb_os
        if self.cmdb_short_description is not None:
            output["cmdb_short_description"] = self.cmdb_short_description
        if self.cmdb_result_json is not None:
            output["cmdb_result_json"] = self.cmdb_result_json
        if self.cmdb_results_json is not None:
            output["cmdb_results_json"] = self.cmdb_results_json
        if self.result_count is not None:
            output["result_count"] = self.result_count

        return output
