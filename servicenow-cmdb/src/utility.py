"""
Utility module for the ServiceNow CMDB Universal Extension.

Provides:
- ServiceNowClient: HTTP session management and response validation
- parse_ci_class: Extracts raw table name from dynamic choice display format
- parse_ire_response: Parses identifyreconcile API response into structured result
- print_table: Renders and prints ASCII tables via tabulate
- sanitize_json: Serializes dicts/lists to JSON strings, redacting credential values
"""

import json
import logging
import os
import re

import requests
from requests import Session
from requests.auth import HTTPBasicAuth
from tabulate import tabulate

from exceptions import (
    AuthenticationError,
    AuthorizationError,
    CmdbIdentificationError,
    CmdbReconciliationError,
    ConnectionError,
    ServiceNowBusinessRuleError,
    ServiceNowValidationError,
)

logger = logging.getLogger("UNV")

# Keywords that indicate a business rule blocked the request
_BUSINESS_RULE_KEYWORDS: tuple[str, ...] = (
    "business rule",
    "workflow",
    "mandatory",
    "approval",
    "script",
)

# Default HTTP timeout in seconds
_DEFAULT_TIMEOUT: int = 30


def _get_timeout() -> int:
    """Read UE_HTTP_TIMEOUT environment variable; fall back to default."""
    raw: str = os.environ.get("UE_HTTP_TIMEOUT", "")
    try:
        return int(raw)
    except ValueError:
        return _DEFAULT_TIMEOUT


def _extract_error_detail(response: requests.Response) -> str:
    """
    Extract the most descriptive error text from a ServiceNow error response body.

    Args:
        response: The HTTP response object with an error status code.

    Returns:
        A plain-text error description extracted from the response body.
    """
    try:
        body: dict = response.json()
        error: dict = body.get("error", {})
        detail: str = error.get("detail", "") or ""
        message: str = error.get("message", "") or ""
        return detail or message or response.text
    except Exception:
        return response.text


def _categorize_400_error(
    error_text: str, status_code: int, path: str
) -> None:
    """
    Raise the appropriate exception for HTTP 400 or 422 responses.

    Inspects the ServiceNow error message for business-rule keywords and routes
    to ServiceNowBusinessRuleError or ServiceNowValidationError accordingly.

    Args:
        error_text: The extracted error detail from the response body.
        status_code: The HTTP status code (400 or 422).
        path: The request URL path, used for context in the error message.

    Raises:
        ServiceNowBusinessRuleError: When the error text contains a business-rule keyword.
        ServiceNowValidationError: For all other 400/422 errors.
    """
    lower: str = error_text.lower()
    for keyword in _BUSINESS_RULE_KEYWORDS:
        if keyword in lower:
            logger.error(
                "ServiceNow business rule error (HTTP %d) at %s: %s",
                status_code,
                path,
                error_text,
            )
            raise ServiceNowBusinessRuleError(error_text)
    logger.error(
        "ServiceNow validation error (HTTP %d) at %s: %s",
        status_code,
        path,
        error_text,
    )
    raise ServiceNowValidationError(error_text)


class ServiceNowClient:
    """
    HTTP client for the ServiceNow REST API.

    Manages a requests.Session with Basic Auth, default JSON headers, and a
    consistent timeout. Validates all responses and raises typed exceptions.

    Usage:
        client = ServiceNowClient(instance_url, username, password)
        try:
            data = client.get("/api/now/table/incident", params={"sysparm_limit": "1"})
        finally:
            client.close()
    """

    def __init__(self, instance_url: str, username: str, password: str) -> None:
        """
        Initialize the session with Basic Auth and JSON headers.

        Args:
            instance_url: Base URL of the ServiceNow instance (e.g. https://dev.service-now.com).
            username: ServiceNow username for Basic Auth.
            password: ServiceNow password for Basic Auth.
        """
        self._instance_url: str = instance_url.rstrip("/")
        self._timeout: int = _get_timeout()
        self._session: Session = Session()
        self._session.auth = HTTPBasicAuth(username, password)
        self._session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )
        logger.debug(
            "ServiceNowClient initialized for %s (timeout=%ds)",
            self._instance_url,
            self._timeout,
        )

    def _url(self, path: str) -> str:
        """Build the full URL from a relative API path."""
        return self._instance_url + path

    def _validate_response(self, response: requests.Response) -> dict:
        """
        Inspect the HTTP response and return the parsed JSON body or raise a typed exception.

        Args:
            response: The completed HTTP response.

        Returns:
            Parsed JSON response body as a dict.

        Raises:
            AuthenticationError: HTTP 401.
            AuthorizationError: HTTP 403.
            ServiceNowValidationError: HTTP 404 or non-business-rule 400/422.
            ServiceNowBusinessRuleError: HTTP 400/422 caused by a business rule.
            ConnectionError: Any requests transport exception (propagated by callers).
        """
        status: int = response.status_code
        path: str = response.url

        logger.debug("Response status: %d from %s", status, path)

        if status in (200, 201):
            return response.json()

        if status == 401:
            logger.error("Authentication failed (HTTP 401) at %s", path)
            raise AuthenticationError(
                "Invalid ServiceNow credentials"
            )

        if status == 403:
            logger.error("Authorization denied (HTTP 403) at %s", path)
            raise AuthorizationError(
                "Insufficient permissions for this operation"
            )

        if status == 404:
            logger.error("Resource not found (HTTP 404) at %s", path)
            raise ServiceNowValidationError(
                "Record or table not found at path: %s" % path
            )

        if status in (400, 422):
            error_text: str = _extract_error_detail(response)
            _categorize_400_error(error_text, status, path)

        # Catch-all for unexpected status codes
        logger.error("Unexpected HTTP %d from %s", status, path)
        raise ServiceNowValidationError(
            "Unexpected HTTP %d from ServiceNow" % status
        )

    def get(self, path: str, params: dict | None = None) -> dict:
        """
        Execute a GET request.

        Args:
            path: API path relative to instance_url (e.g. "/api/now/table/incident").
            params: Optional query parameters dict.

        Returns:
            Parsed JSON response body.

        Raises:
            ConnectionError: On transport-level failures.
            AuthenticationError, AuthorizationError, ServiceNowValidationError,
            ServiceNowBusinessRuleError: On HTTP error responses.
        """
        url: str = self._url(path)
        logger.info("GET %s", url)
        logger.debug("Query params: %s", params)
        try:
            response: requests.Response = self._session.get(
                url, params=params, timeout=self._timeout
            )
        except requests.exceptions.Timeout:
            logger.error("Request timed out after %ds: GET %s", self._timeout, url)
            raise ConnectionError(
                "Request timed out after %d seconds" % self._timeout
            )
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.SSLError,
        ) as exc:
            logger.error("Connection failed: GET %s: %s", url, str(exc))
            raise ConnectionError(
                "Unable to reach ServiceNow instance at %s" % self._instance_url
            )
        return self._validate_response(response)

    def post(self, path: str, payload: dict) -> dict:
        """
        Execute a POST request with a JSON body.

        Args:
            path: API path relative to instance_url.
            payload: Dict to serialize as the JSON request body.

        Returns:
            Parsed JSON response body.

        Raises:
            ConnectionError: On transport-level failures.
            AuthenticationError, AuthorizationError, ServiceNowValidationError,
            ServiceNowBusinessRuleError: On HTTP error responses.
        """
        url: str = self._url(path)
        logger.info("POST %s", url)
        logger.debug("Request payload: %s", payload)
        try:
            response: requests.Response = self._session.post(
                url, json=payload, timeout=self._timeout
            )
        except requests.exceptions.Timeout:
            logger.error("Request timed out after %ds: POST %s", self._timeout, url)
            raise ConnectionError(
                "Request timed out after %d seconds" % self._timeout
            )
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.SSLError,
        ) as exc:
            logger.error("Connection failed: POST %s: %s", url, str(exc))
            raise ConnectionError(
                "Unable to reach ServiceNow instance at %s" % self._instance_url
            )
        return self._validate_response(response)

    def put(self, path: str, payload: dict) -> dict:
        """
        Execute a PUT request with a JSON body.

        Args:
            path: API path relative to instance_url.
            payload: Dict to serialize as the JSON request body.

        Returns:
            Parsed JSON response body.

        Raises:
            ConnectionError: On transport-level failures.
            AuthenticationError, AuthorizationError, ServiceNowValidationError,
            ServiceNowBusinessRuleError: On HTTP error responses.
        """
        url: str = self._url(path)
        logger.info("PUT %s", url)
        logger.debug("Request payload: %s", payload)
        try:
            response: requests.Response = self._session.put(
                url, json=payload, timeout=self._timeout
            )
        except requests.exceptions.Timeout:
            logger.error("Request timed out after %ds: PUT %s", self._timeout, url)
            raise ConnectionError(
                "Request timed out after %d seconds" % self._timeout
            )
        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.SSLError,
        ) as exc:
            logger.error("Connection failed: PUT %s: %s", url, str(exc))
            raise ConnectionError(
                "Unable to reach ServiceNow instance at %s" % self._instance_url
            )
        return self._validate_response(response)

    def close(self) -> None:
        """Close the underlying HTTP session and release connection pool resources."""
        self._session.close()
        logger.debug("ServiceNowClient session closed")


# ---------------------------------------------------------------------------
# CI Class Name Parser
# ---------------------------------------------------------------------------

_CI_CLASS_PATTERN: re.Pattern[str] = re.compile(r"\(([^)]+)\)\s*$")


def parse_ci_class(display_value: str) -> str:
    """
    Extract the raw ServiceNow table name from a dynamic choice display string.

    The dynamic choice field for ci_class renders entries as:
        "<Label> (<table_name>)"
    This function returns the table name portion.

    Args:
        display_value: The selected display string, e.g. "Server (cmdb_ci_server)".

    Returns:
        The raw table name string (e.g. "cmdb_ci_server"), or the entire input
        string if no parenthesised suffix is found, or an empty string if the
        input is empty.

    Examples:
        >>> parse_ci_class("Server (cmdb_ci_server)")
        'cmdb_ci_server'
        >>> parse_ci_class("cmdb_ci_server")
        'cmdb_ci_server'
        >>> parse_ci_class("")
        ''
    """
    if not display_value:
        return ""
    match: re.Match[str] | None = _CI_CLASS_PATTERN.search(display_value)
    if match:
        return match.group(1).strip()
    return display_value.strip()


# ---------------------------------------------------------------------------
# IRE Response Parser
# ---------------------------------------------------------------------------

_OPERATION_MAP: dict[str, str] = {
    "insert": "CREATED",
    "update": "UPDATED",
    "match": "MATCHED",
}


class IREResult:
    """
    Structured result from a parsed identifyreconcile API response.

    Attrs:
        cmdb_action: Human-readable operation outcome ("CREATED", "UPDATED", "MATCHED", "UNKNOWN").
        cmdb_sys_id: The sys_id of the affected Configuration Item.
        cmdb_class: The CMDB table/class name of the CI.
        cmdb_status: Overall status string ("SUCCESS" or "PARTIAL_SUCCESS").
    """

    def __init__(
        self,
        cmdb_action: str,
        cmdb_sys_id: str,
        cmdb_class: str,
        cmdb_status: str,
    ) -> None:
        self.cmdb_action: str = cmdb_action
        self.cmdb_sys_id: str = cmdb_sys_id
        self.cmdb_class: str = cmdb_class
        self.cmdb_status: str = cmdb_status


def parse_ire_response(response_body: dict) -> IREResult:
    """
    Parse the JSON body returned by the ServiceNow identifyreconcile endpoint.

    Validates the response structure, detects identification and reconciliation
    errors in the results list, and maps the operation code to a human-readable
    action name.

    Args:
        response_body: The parsed JSON dict returned by the identifyreconcile API.

    Returns:
        IREResult containing cmdb_action, cmdb_sys_id, cmdb_class, and cmdb_status.

    Raises:
        CmdbIdentificationError: When identificationResults is empty, or when an
            error message contains the keyword "identification".
        CmdbReconciliationError: When an error message contains "reconciliation".
        ServiceNowValidationError: For other IRE error messages.
    """
    result: dict = response_body.get("result", response_body)
    identification_results: list = result.get("identificationResults", [])

    if not identification_results:
        logger.error("IRE returned no identification results")
        raise CmdbIdentificationError("IRE returned no identification results")

    primary: dict = identification_results[0]
    errors: list = primary.get("errors", []) or []

    if errors:
        error_message: str = ""
        for err in errors:
            if isinstance(err, dict):
                error_message = err.get("message", "") or str(err)
            else:
                error_message = str(err)
            break

        lower_msg: str = error_message.lower()
        if "reconciliation" in lower_msg:
            logger.error("IRE reconciliation error: %s", error_message)
            raise CmdbReconciliationError(error_message)
        if "identification" in lower_msg:
            logger.error("IRE identification error: %s", error_message)
            raise CmdbIdentificationError(error_message)
        logger.error("IRE validation error: %s", error_message)
        raise ServiceNowValidationError(error_message)

    raw_operation: str = str(primary.get("operation", "")).lower()
    cmdb_action: str = _OPERATION_MAP.get(raw_operation, "UNKNOWN")

    cmdb_sys_id: str = str(primary.get("sysId", "") or "")
    cmdb_class: str = str(primary.get("className", "") or "")

    warnings: list = primary.get("warnings", []) or []
    cmdb_status: str = "PARTIAL_SUCCESS" if warnings else "SUCCESS"

    logger.debug(
        "IRE result: action=%s, sys_id=%s, class=%s, status=%s",
        cmdb_action,
        cmdb_sys_id,
        cmdb_class,
        cmdb_status,
    )

    return IREResult(
        cmdb_action=cmdb_action,
        cmdb_sys_id=cmdb_sys_id,
        cmdb_class=cmdb_class,
        cmdb_status=cmdb_status,
    )


# ---------------------------------------------------------------------------
# Output Table Formatter
# ---------------------------------------------------------------------------

def print_table(headers: list[str], rows: list[list]) -> None:
    """
    Render a multi-row ASCII table and print it to STDOUT.

    Args:
        headers: Column header labels.
        rows: List of row value lists; each inner list must match the length of headers.
    """
    table: str = tabulate(rows, headers=headers, tablefmt="rounded_outline")
    print(table)


def print_record_table(record: dict[str, str]) -> None:
    """
    Render a two-column ASCII table for a single record and print it to STDOUT.

    Column headers are "Field" and "Value".

    Args:
        record: Ordered dict of field name to display value.
    """
    rows: list[list] = [[k, v] for k, v in record.items()]
    table: str = tabulate(rows, headers=["Field", "Value"], tablefmt="rounded_outline")
    print(table)


def print_multi_result_note(count: int) -> None:
    """
    Print the standard multi-result note to STDOUT before a CI table.

    Args:
        count: Total number of CI records returned by the query.
    """
    print(
        "Returning %d results. Individual output fields reflect the first result."
        " Full results in cmdb_results_json." % count
    )


# ---------------------------------------------------------------------------
# JSON Sanitizer
# ---------------------------------------------------------------------------

def sanitize_json(
    data: dict | list,
    redact_values: set[str] | None = None,
    indent: int | None = None,
) -> str:
    """
    Serialize a dict or list to a JSON string, redacting any specified values.

    Any dict value (at any depth) that matches an entry in redact_values is
    replaced with the string "[REDACTED]" before serialization. This prevents
    credential values from appearing in output fields or STDOUT.

    Args:
        data: The dict or list to serialize.
        redact_values: Set of string values to replace with "[REDACTED]".
            Typically contains the ServiceNow password. Pass None or an
            empty set to disable redaction.
        indent: Optional indentation level for pretty-printing. Pass None
            for compact output (used in output fields).

    Returns:
        JSON-encoded string representation of the sanitized data.
    """
    if redact_values:
        data = _redact(data, redact_values)
    return json.dumps(data, indent=indent, ensure_ascii=False)


def _redact(obj: dict | list | str | None, redact_values: set[str]) -> dict | list | str | None:
    """
    Recursively replace dict values matching redact_values with "[REDACTED]".

    Args:
        obj: The object to traverse (dict, list, or scalar).
        redact_values: Values to replace.

    Returns:
        A new object with matching values replaced.
    """
    if isinstance(obj, dict):
        return {
            k: "[REDACTED]" if (isinstance(v, str) and v in redact_values) else _redact(v, redact_values)
            for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [
            "[REDACTED]" if (isinstance(item, str) and item in redact_values) else _redact(item, redact_values)
            for item in obj
        ]
    return obj
