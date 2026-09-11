"""
Exceptions module for the ServiceNow CMDB Universal Extension.

This module provides:
- Base ExecutionError class
- Standard exception types (DataValidationError, UnexpectedSystemError)
- ServiceNow-specific exception types for HTTP and API errors
- CMDB IRE-specific exception types
- Exit code conventions:
    0 — Successful execution
    1 — All runtime errors (authentication, authorization, connection,
        ServiceNow API errors, CMDB errors, not found)
    2 — Input validation error (missing required field, malformed user-provided JSON)
"""
from typing import Optional


class ExecutionError(Exception):
    """
    The default error raised by an extension.

    All extension errors must inherit from it.

    Attrs:
        exit_code: The exit code of the extension (for UAC)
        message: The error message for status description
    """

    exit_code: int = 1
    message: str = "Execution Failed"

    def __init__(self, message: Optional[str] = None):
        """
        Initialize exception.

        Args:
            message: Optional message that will be appended to the default message.

        Note:
            To return result data with errors, use error_manager.set_result()
            before raising the exception.
        """
        if message:
            self.message = f"{self.message}: {message}"

        super().__init__(self.message)


class DataValidationError(ExecutionError):
    """Raised when an input field is invalid."""
    exit_code = 20
    message = "Data Validation Error"


class UnexpectedSystemError(ExecutionError):
    """Raised for unexpected system errors."""
    exit_code = 1
    message = "System Error"


class InputValidationError(ExecutionError):
    """
    Raised when a required input field is missing or contains malformed data.

    Use this exception for:
    - A required field is empty or not provided
    - A user-provided JSON string (e.g. incident_fields_to_update,
      ritm_fields_to_update) fails to parse as valid JSON
    - A dynamic choice field value cannot be resolved to a table name

    Exit code 2 signals a non-transient, user-correctable input error.
    """
    exit_code = 2
    message = "Input Validation Error"


class AuthenticationError(ExecutionError):
    """
    Raised when ServiceNow rejects the provided credentials (HTTP 401).

    Use this exception when the API responds with HTTP 401 Unauthorized,
    indicating that the supplied username or password is invalid.

    This is a non-transient error — the user must correct the credential.
    """
    exit_code = 1
    message = "Authentication Error"


class AuthorizationError(ExecutionError):
    """
    Raised when the authenticated user lacks permission to perform the operation (HTTP 403).

    Use this exception when the API responds with HTTP 403 Forbidden,
    indicating that the credential is valid but the user does not have
    the required ServiceNow role or ACL rights.

    This is a non-transient error — the user must correct their ServiceNow permissions.
    """
    exit_code = 1
    message = "Authorization Error"


class ConnectionError(ExecutionError):
    """
    Raised when a network-level failure prevents reaching the ServiceNow instance.

    Use this exception for:
    - TCP connection failures (requests.exceptions.ConnectionError)
    - SSL/TLS handshake errors (requests.exceptions.SSLError)
    - DNS resolution failures
    - Request timeouts (requests.exceptions.Timeout)

    This is a potentially transient error — retrying after a delay may succeed.
    """
    exit_code = 1
    message = "Connection Error"


class ServiceNowValidationError(ExecutionError):
    """
    Raised when ServiceNow rejects a request due to a field, table, or query issue.

    Use this exception for:
    - HTTP 400 or 422 responses where the error does not indicate a business rule
    - HTTP 404 responses (requested record or table not found)
    - Invalid sysparm_query strings rejected by the Table API
    - Invalid table names in CI class operations

    The original ServiceNow error message should be preserved in the exception message.
    """
    exit_code = 1
    message = "ServiceNow Validation Error"


class ServiceNowBusinessRuleError(ExecutionError):
    """
    Raised when a ServiceNow business rule blocks or rejects the requested operation.

    Use this exception for HTTP 400 or 422 responses where the error message
    contains keywords indicating that a business rule or workflow constraint
    prevented the operation (e.g. mandatory field check, approval requirement).

    The original ServiceNow error message should be preserved in the exception message.
    """
    exit_code = 1
    message = "ServiceNow Business Rule Error"


class CmdbIdentificationError(ExecutionError):
    """
    Raised when the ServiceNow IRE cannot identify the Configuration Item.

    Use this exception when the identifyreconcile API response contains
    identification errors in identificationResults[0].errors, or when
    the identificationResults list is empty.

    Common causes:
    - CI class does not have identification rules configured in ServiceNow
    - Required identification attributes are missing from the submitted values
    - The ci_class table name is invalid or not recognized by IRE

    The original ServiceNow IRE error message should be preserved.
    """
    exit_code = 1
    message = "CMDB Identification Error"


class CmdbReconciliationError(ExecutionError):
    """
    Raised when the ServiceNow IRE fails during the reconciliation phase.

    Use this exception when the identifyreconcile API response contains
    reconciliation errors in identificationResults[0].errors — specifically
    when the error message contains the keyword "reconciliation".

    Common causes:
    - Conflicting discovery source authority rules
    - CI attribute write permissions denied by reconciliation rules

    The original ServiceNow IRE error message should be preserved.
    """
    exit_code = 1
    message = "CMDB Reconciliation Error"


class NotFoundError(ExecutionError):
    """
    Raised when a Get CI query returns zero records from the ServiceNow Table API.

    Use this exception when the Table API responds with HTTP 200 but the
    result array is empty, meaning no CI matched the provided search criteria.

    Include the search mode and value in the exception message to aid debugging:
        raise NotFoundError("No CI found for [Name: APP-PROD-01]")
    """
    exit_code = 1
    message = "Not Found Error"
