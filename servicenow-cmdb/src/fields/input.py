"""
InputFields dataclass for the ServiceNow CMDB Universal Extension.

Maps every field defined in template.json to a typed Python attribute.
Handles preprocessing of UAC field formats, validation, and re-run support.
"""
import json
from dataclasses import dataclass, fields as dataclass_fields, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, get_args, get_origin, get_type_hints

from exceptions import DataValidationError, InputValidationError
from fields.output import OutputFields
from fields.types import (
    Array,
    Boolean,
    Credential,
    Float,
    Integer,
    MultiChoice,
    Script,
    SingleChoice,
    Text,
)
from manager import ExtensionManager

extension_manager = ExtensionManager()


@dataclass
class InputFields:
    """
    Typed representation of all UAC task template input fields.

    All user-defined fields are Optional — UAC enforces required field
    validation at the controller level; hidden fields arrive as empty strings.
    """

    # --- Always-visible fields ---
    action: Optional[SingleChoice] = None
    instance_url: Optional[Text] = None
    credential: Optional[Credential] = None

    # --- Create Incident fields ---
    short_description: Optional[Text] = None
    description: Optional[Text] = None
    category: Optional[Text] = None
    priority: Optional[Text] = None
    urgency: Optional[Text] = None
    impact: Optional[Text] = None
    caller: Optional[Text] = None
    assignment_group: Optional[Text] = None
    assigned_to: Optional[Text] = None

    # --- Update Incident fields ---
    # Also used as output: preserveOutputOnRerun=true in template.json
    incident_sys_id: Optional[Text] = None
    incident_fields_to_update: Optional[Text] = None

    # --- Update RITM fields ---
    # Also used as output: preserveOutputOnRerun=true in template.json
    ritm_sys_id: Optional[Text] = None
    ritm_fields_to_update: Optional[Text] = None

    # --- Shared CI fields (Create/Update CI + Get CI) ---
    ci_class: Optional[SingleChoice] = None

    # --- Create/Update CI fields ---
    ci_name: Optional[Text] = None
    attributes: Optional[Array] = None
    data_source: Optional[Text] = None

    # --- Get CI fields ---
    search_by: Optional[SingleChoice] = None
    search_value: Optional[Text] = None
    return_fields: Optional[Text] = None
    limit: Optional[Integer] = None

    # --- Output-only fields (written by extension, readable on re-run) ---
    incident_number: Optional[Text] = None
    ritm_number: Optional[Text] = None
    cmdb_action: Optional[Text] = None
    cmdb_sys_id: Optional[Text] = None
    cmdb_class: Optional[Text] = None
    cmdb_name: Optional[Text] = None
    cmdb_status: Optional[Text] = None
    cmdb_operational_status: Optional[Integer] = None
    cmdb_cpu_count: Optional[Integer] = None
    cmdb_ram: Optional[Integer] = None
    cmdb_result_count: Optional[Integer] = None
    cmdb_result_json: Optional[Text] = None
    cmdb_results_json: Optional[Text] = None

    # --- Framework internals (must be last — default fields after non-default not allowed) ---
    previous_output: Optional[OutputFields] = None
    _skip_validation: bool = False

    def __post_init__(self) -> None:
        """Run validation after dataclass initialization."""
        if self._skip_validation:
            return

        self._validate_action()
        self._validate_instance_url()
        self._validate_credential()
        self._validate_short_description()
        self._validate_incident_sys_id()
        self._validate_incident_fields_to_update()
        self._validate_ritm_sys_id()
        self._validate_ritm_fields_to_update()
        self._validate_ci_class()
        self._validate_ci_name()
        self._validate_search_by()
        self._validate_search_value()
        self._validate_limit()

        if extension_manager.has_errors():
            raise DataValidationError(
                f"Validation failed with {extension_manager.error_count()} error(s)"
            )

    # ------------------------------------------------------------------
    # Validation methods
    # ------------------------------------------------------------------

    def _validate_action(self) -> None:
        """Validate action is one of the five defined choice values."""
        valid_actions = {
            "Create Incident",
            "Update Incident",
            "Update RITM",
            "Create/Update CI",
            "Get CI",
        }
        if self.action is not None and self.action.value not in valid_actions:
            exc = DataValidationError(
                f"Invalid action: '{self.action.value}'. "
                f"Must be one of: {sorted(valid_actions)}"
            )
            extension_manager.add_error(exc, field="action", value=self.action.value)

    def _validate_instance_url(self) -> None:
        """Validate instance_url starts with https:// and has no trailing slash."""
        if self.instance_url and self.instance_url.value:
            url = self.instance_url.value
            if not url.startswith("https://"):
                exc = DataValidationError(
                    "instance_url must begin with 'https://'"
                )
                extension_manager.add_error(exc, field="instance_url", value=url)
            elif url.endswith("/"):
                exc = DataValidationError(
                    "instance_url must not include a trailing slash"
                )
                extension_manager.add_error(exc, field="instance_url", value=url)

    def _validate_credential(self) -> None:
        """Validate credential provides both user and password."""
        if self.credential is not None:
            if not self.credential.user:
                exc = DataValidationError(
                    "Credential must provide a username (user attribute)"
                )
                extension_manager.add_error(exc, field="credential")
            if not self.credential.password:
                exc = DataValidationError(
                    "Credential must provide a password (password attribute)"
                )
                extension_manager.add_error(exc, field="credential")

    def _validate_short_description(self) -> None:
        """Validate short_description is non-empty when Create Incident is selected."""
        if self.action and self.action.value == "Create Incident":
            if not self.short_description or not self.short_description.value:
                exc = InputValidationError(
                    "short_description is required for action 'Create Incident'"
                )
                extension_manager.add_error(exc, field="short_description")

    def _validate_incident_sys_id(self) -> None:
        """Validate incident_sys_id is non-empty when Update Incident is selected."""
        if self.action and self.action.value == "Update Incident":
            if not self.incident_sys_id or not self.incident_sys_id.value:
                exc = InputValidationError(
                    "incident_sys_id is required for action 'Update Incident'"
                )
                extension_manager.add_error(exc, field="incident_sys_id")

    def _validate_incident_fields_to_update(self) -> None:
        """Validate incident_fields_to_update is valid JSON when provided."""
        if (
            self.action
            and self.action.value == "Update Incident"
            and self.incident_fields_to_update
            and self.incident_fields_to_update.value
        ):
            try:
                json.loads(self.incident_fields_to_update.value)
            except (ValueError, TypeError):
                exc = InputValidationError(
                    "incident_fields_to_update must be a valid JSON object"
                )
                extension_manager.add_error(exc, field="incident_fields_to_update")

    def _validate_ritm_sys_id(self) -> None:
        """Validate ritm_sys_id is non-empty when Update RITM is selected."""
        if self.action and self.action.value == "Update RITM":
            if not self.ritm_sys_id or not self.ritm_sys_id.value:
                exc = InputValidationError(
                    "ritm_sys_id is required for action 'Update RITM'"
                )
                extension_manager.add_error(exc, field="ritm_sys_id")

    def _validate_ritm_fields_to_update(self) -> None:
        """Validate ritm_fields_to_update is valid JSON when provided."""
        if (
            self.action
            and self.action.value == "Update RITM"
            and self.ritm_fields_to_update
            and self.ritm_fields_to_update.value
        ):
            try:
                json.loads(self.ritm_fields_to_update.value)
            except (ValueError, TypeError):
                exc = InputValidationError(
                    "ritm_fields_to_update must be a valid JSON object"
                )
                extension_manager.add_error(exc, field="ritm_fields_to_update")

    def _validate_ci_class(self) -> None:
        """Validate ci_class is non-empty when Create/Update CI or Get CI is selected."""
        ci_actions = {"Create/Update CI", "Get CI"}
        if self.action and self.action.value in ci_actions:
            if not self.ci_class or not self.ci_class.value:
                exc = InputValidationError(
                    f"ci_class is required for action '{self.action.value}'"
                )
                extension_manager.add_error(exc, field="ci_class")

    def _validate_ci_name(self) -> None:
        """Validate ci_name is non-empty when Create/Update CI is selected."""
        if self.action and self.action.value == "Create/Update CI":
            if not self.ci_name or not self.ci_name.value:
                exc = InputValidationError(
                    "ci_name is required for action 'Create/Update CI'"
                )
                extension_manager.add_error(exc, field="ci_name")

    def _validate_search_by(self) -> None:
        """Validate search_by is one of the defined options when Get CI is selected."""
        valid_options = {"Name", "Sys ID", "Custom Query"}
        if self.action and self.action.value == "Get CI":
            if self.search_by is not None and self.search_by.value not in valid_options:
                exc = DataValidationError(
                    f"Invalid search_by: '{self.search_by.value}'. "
                    f"Must be one of: {sorted(valid_options)}"
                )
                extension_manager.add_error(
                    exc, field="search_by", value=self.search_by.value
                )

    def _validate_search_value(self) -> None:
        """Validate search_value is non-empty when Get CI is selected."""
        if self.action and self.action.value == "Get CI":
            if not self.search_value or not self.search_value.value:
                exc = InputValidationError(
                    "search_value is required for action 'Get CI'"
                )
                extension_manager.add_error(exc, field="search_value")

    def _validate_limit(self) -> None:
        """Validate limit is between 1 and 10000 when Get CI is selected."""
        if self.action and self.action.value == "Get CI":
            if self.limit is not None and not (1 <= int(self.limit) <= 10000):
                exc = DataValidationError(
                    f"limit must be between 1 and 10000, got {int(self.limit)}"
                )
                extension_manager.add_error(
                    exc, field="limit", value=int(self.limit)
                )

    # ------------------------------------------------------------------
    # Framework methods — do not remove
    # ------------------------------------------------------------------

    @staticmethod
    def preprocess_fields(fields: dict) -> dict:
        """
        Normalize raw UAC field dict before passing to the dataclass constructor.

        Steps performed:
        1. Strip dot-notation credential sub-fields (e.g. credential.user).
        2. Unwrap single-item lists to scalar values.
        3. Convert raw values to typed wrapper instances based on field type hints.
        4. Separate OutputFields-named keys into a nested previous_output instance.

        Args:
            fields: Raw field dict received from UAC.

        Returns:
            Processed dict suitable for InputFields(**processed).
        """
        output_field_names = {f.name for f in dataclass_fields(OutputFields)}
        type_hints = get_type_hints(InputFields)

        # Build map of field name -> unwrapped (non-None) type
        field_wrapper_types: Dict[str, Any] = {}
        for field_name, field_type in type_hints.items():
            base_type = field_type
            if get_origin(field_type) is Union:
                args = get_args(field_type)
                non_none = [a for a in args if a is not type(None)]
                if non_none:
                    base_type = non_none[0]
            field_wrapper_types[field_name] = base_type

        processed: dict = {}
        previous_output_data: dict = {}

        for key, value in fields.items():
            # Drop dot-notation credential sub-fields (e.g. credential.token)
            if "." in key:
                continue

            # Unwrap single-element lists
            if isinstance(value, list) and len(value) == 1:
                value = value[0]

            # Route OutputFields keys to a separate dict for re-run support
            if key in output_field_names:
                previous_output_data[key] = value
                continue

            if value is None:
                processed[key] = value
                continue

            wrapper_type = field_wrapper_types.get(key)

            if wrapper_type is SingleChoice:
                if isinstance(value, list):
                    value = SingleChoice(_values=value)
                else:
                    value = SingleChoice(_values=[value])
            elif wrapper_type is MultiChoice:
                if isinstance(value, list):
                    value = MultiChoice(values=value)
                else:
                    value = MultiChoice(values=[value])
            elif wrapper_type is Script:
                if isinstance(value, str):
                    value = Script(path=Path(value))
            elif wrapper_type is Credential:
                if isinstance(value, dict):
                    value = Credential.from_dict(value)
            elif wrapper_type is Text:
                if isinstance(value, str):
                    value = Text(value=value)
            elif wrapper_type is Integer:
                if isinstance(value, (int, str)):
                    value = Integer(value=int(value))
            elif wrapper_type is Float:
                if isinstance(value, (int, float, str)):
                    value = Float(value=float(value))
            elif wrapper_type is Boolean:
                if isinstance(value, bool):
                    value = Boolean(value=value)
            elif wrapper_type is Array:
                if isinstance(value, list):
                    value = Array(pairs=value)

            processed[key] = value

        if previous_output_data:
            # Wrap string values in Text for previous OutputFields
            wrapped: dict = {}
            for k, v in previous_output_data.items():
                if isinstance(v, str):
                    wrapped[k] = Text(value=v)
                else:
                    wrapped[k] = v
            processed["previous_output"] = OutputFields(**wrapped)

        return processed

    def to_dict(self) -> dict:
        """
        Convert to dict, unwrapping wrapper types and excluding internal fields.

        Returns:
            Clean dict for use in build_result(), without _skip_validation or
            empty previous_output.
        """
        data = asdict(self)
        result: dict = {}

        for key, value in data.items():
            if key == "_skip_validation":
                continue
            if key == "previous_output" and value is None:
                continue

            if isinstance(value, dict):
                if "_values" in value:  # SingleChoice
                    result[key] = value["_values"]
                elif "values" in value and len(value) == 1:  # MultiChoice
                    result[key] = value["values"]
                elif "value" in value and len(value) == 1:  # Text, Integer, Float, Boolean
                    result[key] = value["value"]
                elif "path" in value:  # Script
                    result[key] = str(value["path"])
                elif "pairs" in value:  # Array
                    result[key] = value["pairs"]
                else:
                    result[key] = value
            else:
                result[key] = value

        return result

    def update(self, **kwargs: object) -> None:
        """Update one or more field values by name."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def clear(self) -> None:
        """Reset all user-defined fields to None (preserves framework internals)."""
        for f in dataclass_fields(self):
            if f.name in ("_skip_validation", "previous_output"):
                continue
            setattr(self, f.name, None)
