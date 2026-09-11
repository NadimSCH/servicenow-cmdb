"""
Extension module template for UAC Universal Extensions.

This module provides the Extension class with extension_start() method that is called
by UAC when the extension task executes. It orchestrates all components:
- Input validation (InputFields)
- Action dispatch (ACTION_MAPPER)
- Output formatting (ActionOutput)
- Extension state management (ExtensionManager)
"""

import json

from universal_extension import UniversalExtension, ExtensionResult, logger
from universal_extension.deco.choice import dynamic_choice_command
from fields.input import InputFields
from actions.output import ActionOutput
from actions import ACTION_MAPPER
from exceptions import ExecutionError, UnexpectedSystemError
from manager import ExtensionManager
from utility import ServiceNowClient

# Extension metadata - UPDATE THESE FROM YOUR ANALYSIS
EXTENSION_NAME = "servicenow-cmdb"
EXTENSION_VERSION = "1.0.0"

extension_manager = ExtensionManager()

# ============================================================================
# Extension Class
# ============================================================================

class Extension(UniversalExtension):
    """
    Universal Extension entry point.

    This class inherits from UniversalExtension as required by the UAC framework.
    """

    def extension_start(self, fields: dict) -> ExtensionResult:
        """
        Main entry point called by UAC when extension task executes.

        Flow:
        1. Preprocess fields via InputFields.preprocess_fields()
        2. Parse and validate input (InputFields)
        3. Dispatch to action (ACTION_MAPPER)
        4. Action executes, prints to STDOUT, returns ActionOutput
        5. Build ExtensionResult via build_result()
        6. Return ExtensionResult

        Args:
            fields: Dictionary containing all input field values from UAC

        Returns:
            ExtensionResult with rc, message, and optional unv_output
        """
        # Initialize extension manager at start
        extension_manager.clear()

        input_data = None
        processed_fields = {}

        try:
            logger.info("%s v%s started", EXTENSION_NAME, EXTENSION_VERSION)

            # Preprocess fields via InputFields static method
            processed_fields = InputFields.preprocess_fields(fields)

            # Parse and validate input (triggers validation in __post_init__)
            input_data = InputFields(**processed_fields)
            logger.info("Action requested: %s", input_data.action.value)

            # Get action function from mapper
            action_func = ACTION_MAPPER.get(input_data.action.value)

            # Execute action - action prints to STDOUT and returns ActionOutput
            logger.info("Executing action: %s", input_data.action.value)
            action_output: ActionOutput = action_func(input_data)

            # Print action output to STDOUT
            action_output.print_output()

            # Build success result
            logger.info("%s completed successfully", EXTENSION_NAME)
            return self.build_result(
                input_fields=input_data,
                result=action_output.to_dict()
            )
        except ExecutionError as e:
            # Custom extension exception (validation, auth, service errors, etc.)
            logger.error("Execution error: %s", e.message)

            # Add error to manager if not already collected
            if not e in extension_manager.errors:
                extension_manager.add_error(e)

            # Create InputFields without validation for error reporting
            if processed_fields:
                input_data = InputFields(**processed_fields, _skip_validation=True)

            return self.build_result(
                input_fields=input_data,
                result=extension_manager.result,
                errors=extension_manager.to_array(),
                exit_code=e.exit_code,
                status_description=e.message
            )
        except Exception as e:
            # Capture exception details for debugging
            error_msg = str(e) if str(e) else f"{type(e).__name__}"
            exc = UnexpectedSystemError(error_msg)
            extension_manager.add_error(exc)

            if processed_fields:
                input_data = InputFields(**processed_fields, _skip_validation=True)

            return self.build_result(
                input_fields=input_data,
                result=extension_manager.result,
                errors=extension_manager.to_array(),
                exit_code=exc.exit_code,
                status_description=exc.message
            )


    def build_result(
        self,
        input_fields: InputFields = None,
        result: dict = None,
        errors: list = None,
        exit_code: int = 0,
        status_description: str = "Successful Execution"
    ) -> ExtensionResult:
        """
        Build ExtensionResult with structured unv_output.

        Args:
            input_fields: Input fields (InputFields instance, optional)
            result: Result dictionary from action or ErrorManager
            errors: Errors array (empty list for success, error list for failures)
            exit_code: Exit code (0 for success, 1+ for errors)
            status_description: Human-readable status message

        Returns:
            ExtensionResult with structured unv_output

        Example (success):
            return self.build_result(
                input_fields=input_data,
                result=action_output.to_dict(),
                errors=[],
                exit_code=0,
                status_description=action_output.message
            )

        Example (error):
            return self.build_result(
                input_fields=input_data,
                result=extension_manager.result,
                errors=extension_manager.to_array(),
                exit_code=1,
                status_description="Execution failed"
            )
        """
        # Set defaults
        if result is None:
            result = {}
        if errors is None:
            errors = []

        # Convert input_fields to dict (if provided)
        # Uses to_dict() to exclude internal fields and empty previous_output
        input_dict = input_fields.to_dict() if input_fields else {}

        # Build unv_output structure
        unv_output = {
            "exit_code": exit_code,
            "status_description": status_description,
            "metadata": {
                "version": EXTENSION_VERSION,
                "extension": EXTENSION_NAME
            },
            "input_fields": input_dict,
            "result": result,
            "errors": errors
        }

        return ExtensionResult(
            rc=exit_code,
            message=status_description,
            unv_output=json.dumps(unv_output, indent=2, default=str)
        )

    def extension_cancel(self):
        """
        Called when extension is cancelled.

        Sets extension_manager.cancelled = True which can be checked in actions:
            if extension_manager.is_cancelled():
                raise OperationCancelledError("User cancelled")

        Override to add custom cleanup:
            def extension_cancel(self):
                super().extension_cancel()  # Set the cancelled flag
                logger.info("Cleaning up resources")
                # Close connections, cleanup files, etc.
        """
        extension_manager.set_cancelled()


    # ============================================================================
    # Dynamic Choice Commands
    # ============================================================================

    @dynamic_choice_command("ci_class")
    def get_ci_classes(self, fields: dict) -> ExtensionResult:
        """
        Populate the CI Class dropdown with all available CMDB CI tables from ServiceNow.

        Called by UAC when the user clicks the refresh button on the ci_class dropdown.
        Queries sys_db_object for all tables whose name starts with cmdb_ci and returns
        them formatted as "<Label> (<table_name>)" for human-readable selection.

        Dependencies (declared in template.json choiceFields):
            - instance_url (Text Field 1): Base URL of the ServiceNow instance.
            - credential (Credential Field 1): Basic Auth credentials.

        Args:
            fields: Raw field values from the UAC task form for the declared dependencies.

        Returns:
            ExtensionResult with values containing a sorted list of CI class strings,
            or an empty list on error.
        """
        client: ServiceNowClient | None = None
        try:
            processed = InputFields.preprocess_fields(fields)
            input_data = InputFields(**processed, _skip_validation=True)

            instance_url: str = (
                input_data.instance_url.value
                if input_data.instance_url and input_data.instance_url.value
                else ""
            )
            if not instance_url:
                logger.error("ci_class dynamic choice: instance_url is empty")
                return ExtensionResult(rc=1, message="instance_url is required", values=[])

            if not input_data.credential or not input_data.credential.user:
                logger.error("ci_class dynamic choice: credential is missing or incomplete")
                return ExtensionResult(rc=1, message="credential is required", values=[])

            username: str = input_data.credential.user
            password: str = input_data.credential.password or ""

            logger.info("Loading CI classes from %s", instance_url)

            client = ServiceNowClient(instance_url, username, password)
            response_body: dict = client.get(
                "/api/now/table/sys_db_object",
                params={
                    "sysparm_query": "name STARTSWITH cmdb_ci",
                    "sysparm_fields": "name,label",
                    "sysparm_limit": "1000",
                },
            )

            records: list = response_body.get("result", [])
            choices: list[str] = []
            for record in records:
                name: str = record.get("name", "") or ""
                label: str = record.get("label", "") or ""
                if not name:
                    continue
                display_label: str = label if label else name
                choices.append(f"{display_label} ({name})")

            choices.sort()
            logger.info("Loaded %d CI classes", len(choices))
            return ExtensionResult(rc=0, message="CI classes retrieved", values=choices)

        except Exception as e:
            logger.error("Failed to load CI classes: %s", str(e))
            return ExtensionResult(rc=1, message=f"Error: {str(e)}", values=[])
        finally:
            if client is not None:
                client.close()


    # ============================================================================
    # CUSTOMIZE: Add Extension Commands (MUST be methods inside Extension class)
    # ============================================================================

    # Example extension command:
    #
    # from universal_extension.deco.command import dynamic_command
    #
    # @dynamic_command(command_name="validate_configuration")
    # def validate_configuration(self, fields: dict) -> ExtensionResult:
    #     """
    #     Command to validate extension configuration.
    #
    #     Can be called independently from UAC without executing the extension.
    #     The command_name in decorator is used to invoke this command.
    #
    #     Args:
    #         fields: Current field values to validate
    #
    #     Returns:
    #         ExtensionResult indicating validation success/failure
    #     """
    #     try:
    #         logger.info("Validating configuration...")
    #
    #         # Extract and validate fields
    #         timeout = fields.get("timeout", 30)
    #         if timeout < 5:
    #             return ExtensionResult(
    #                 rc=1,
    #                 message="Timeout must be at least 5 seconds",
    #                 output=False,
    #                 output_data=None,
    #                 output_name=None
    #             )
    #
    #         logger.info("Configuration validated successfully")
    #         return ExtensionResult(
    #             rc=0,
    #             message="Configuration is valid",
    #             output=False,
    #             output_data=None,
    #             output_name=None
    #         )
    #
    #     except Exception as e:
    #         logger.error("Validation failed: %s", str(e))
    #         return ExtensionResult(
    #             rc=1,
    #             message=f"Validation error: {str(e)}",
    #             output=False,
    #             output_data=None,
    #             output_name=None
    #         )
    #
    # Example extension command with output data:
    #
    # @dynamic_command(command_name="get_system_info")
    # def get_system_info(self, _fields: dict) -> ExtensionResult:
    #     """Return extension and system information."""
    #     try:
    #         info = {
    #             "extension_name": EXTENSION_NAME,
    #             "extension_version": EXTENSION_VERSION,
    #             "python_version": "3.11"
    #         }
    #         return ExtensionResult(
    #             rc=0,
    #             message="System information retrieved",
    #             output=True,
    #             output_data=json.dumps(info, indent=2),
    #             output_name="system_info"
    #         )
    #     except Exception as e:
    #         return ExtensionResult(
    #             rc=1,
    #             message=f"Error: {str(e)}",
    #             output=False,
    #             output_data=None,
    #             output_name=None
    #         )
