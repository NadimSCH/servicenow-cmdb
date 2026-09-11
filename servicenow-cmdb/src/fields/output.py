"""
OutputFields dataclass for the ServiceNow CMDB Universal Extension.

Provides real-time UI field updates during extension execution and carries
previous-run data when a task is re-run. Field names match the output-only
fields defined in template.json.
"""
from dataclasses import dataclass, asdict
from typing import Optional

from fields.types import Integer, Text
from universal_extension import ui


@dataclass
class OutputFields:
    """
    Real-time output fields for UAC UI updates.

    All fields correspond to output-only entries in template.json.
    String-valued fields use the Text wrapper; numeric fields use Integer.
    """

    # --- Incident outputs (Create Incident / Update Incident) ---
    incident_number: Optional[Text] = None

    # --- RITM outputs (Update RITM) ---
    ritm_number: Optional[Text] = None

    # --- CI Create/Update outputs ---
    cmdb_action: Optional[Text] = None
    cmdb_sys_id: Optional[Text] = None
    cmdb_class: Optional[Text] = None
    cmdb_name: Optional[Text] = None
    cmdb_status: Optional[Text] = None

    # --- Get CI outputs ---
    cmdb_operational_status: Optional[Integer] = None
    cmdb_cpu_count: Optional[Integer] = None
    cmdb_ram: Optional[Integer] = None
    cmdb_result_count: Optional[Integer] = None
    cmdb_result_json: Optional[Text] = None
    cmdb_results_json: Optional[Text] = None

    def update(self, **fields: object) -> None:
        """
        Update output fields and sync with the UAC UI in real-time.

        String values are automatically wrapped in Text. Integer-typed fields
        accept int values directly.

        Args:
            **fields: Field names and values to update.
        """
        for field_name, field_value in fields.items():
            if hasattr(self, field_name):
                if isinstance(field_value, str):
                    field_value = Text(field_value)
                setattr(self, field_name, field_value)
        ui.update_output_fields(fields)

    def to_dict(self) -> dict:
        """
        Return current field values as a plain dictionary.

        Text wrapper values are unwrapped to strings; Integer wrapper values
        are unwrapped to ints. None fields are omitted.

        Returns:
            Dict of non-None field values with raw Python types.
        """
        result = {}
        for k, v in asdict(self).items():
            if v is None:
                continue
            if isinstance(v, dict) and "value" in v:
                result[k] = v["value"]
            else:
                result[k] = v
        return result

    def clear(self) -> None:
        """Reset all output fields to None."""
        self.incident_number = None
        self.ritm_number = None
        self.cmdb_action = None
        self.cmdb_sys_id = None
        self.cmdb_class = None
        self.cmdb_name = None
        self.cmdb_status = None
        self.cmdb_operational_status = None
        self.cmdb_cpu_count = None
        self.cmdb_ram = None
        self.cmdb_result_count = None
        self.cmdb_result_json = None
        self.cmdb_results_json = None
