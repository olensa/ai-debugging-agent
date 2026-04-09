import re


def classify_error(error_text: str) -> dict:
    text = error_text.lower()

    error_type = "unknown"
    severity = "medium"
    category = "unknown"

    if "nullpointerexception" in text or "none" in text or "null reference" in text:
        error_type = "NullPointerException"
        category = "null_reference"
        severity = "high"

    elif "timeout" in text or "timed out" in text:
        error_type = "Timeout"
        category = "timeout"
        severity = "high"

    elif "sql" in text or "database" in text or "jdbc" in text:
        error_type = "DatabaseError"
        category = "database"
        severity = "high"

    elif "unauthorized" in text or "forbidden" in text or "401" in text or "403" in text:
        error_type = "AuthError"
        category = "auth"
        severity = "medium"

    elif "validation" in text or "invalid" in text or "bad request" in text or "400" in text:
        error_type = "ValidationError"
        category = "validation"
        severity = "low"

    elif "connection refused" in text or "network" in text or "socket" in text:
        error_type = "NetworkError"
        category = "network"
        severity = "high"

    return {
        "error_type": error_type,
        "severity": severity,
        "category": category,
    }


def extract_signals(text: str) -> dict:
    stack_trace_lines = []
    filenames = []
    method_names = []
    exception_names = []
    keywords = []

    lines = text.splitlines()

    for line in lines:
        stripped = line.strip()

        if stripped.startswith("at "):
            stack_trace_lines.append(stripped)

        file_matches = re.findall(r'([A-Z][A-Za-z0-9_]+\.(?:java|py|js|ts))', stripped)
        filenames.extend(file_matches)

        method_matches = re.findall(r'at\s+([\w.$<>]+)\(', stripped)
        method_names.extend(method_matches)

        exception_matches = re.findall(r'([A-Z][A-Za-z0-9_]*Exception|[A-Z][A-Za-z0-9_]*Error)', stripped)
        exception_names.extend(exception_matches)

        keyword_candidates = [
            "null",
            "timeout",
            "timed out",
            "database",
            "sql",
            "jdbc",
            "network",
            "socket",
            "connection refused",
            "unauthorized",
            "forbidden",
            "invalid",
            "config",
            "payment",
            "user",
            "billing",
            "service",
        ]

    lowered_text = text.lower()
    for word in keyword_candidates:
        if word in lowered_text:
            keywords.append(word)

    return {
        "stack_trace_lines": list(dict.fromkeys(stack_trace_lines)),
        "filenames": list(dict.fromkeys(filenames)),
        "method_names": list(dict.fromkeys(method_names)),
        "exception_names": list(dict.fromkeys(exception_names)),
        "keywords": list(dict.fromkeys(keywords)),
    }


def investigation_checklist(category: str) -> dict:
    checklists = {
        "null_reference": [
            "Check which object is null before the failing line.",
            "Trace where the object is first assigned.",
            "Verify whether input data is missing or malformed.",
            "Add temporary logging before the failure point.",
        ],
        "timeout": [
            "Check which dependency is slow or unresponsive.",
            "Review timeout configuration values.",
            "Look for recent latency spikes in downstream services.",
            "Confirm whether retries are happening.",
        ],
        "database": [
            "Verify database connectivity.",
            "Check the exact query or ORM call being executed.",
            "Look for schema or data changes.",
            "Confirm whether the failing record exists.",
        ],
        "auth": [
            "Check whether credentials or tokens are missing.",
            "Verify user roles and permissions.",
            "Confirm token expiration or invalid session state.",
            "Review auth-related config changes.",
        ],
        "validation": [
            "Check which input field failed validation.",
            "Compare request payload against expected format.",
            "Review recent input or API contract changes.",
            "Confirm whether frontend and backend rules still match.",
        ],
        "network": [
            "Check service availability.",
            "Verify host, port, and DNS resolution.",
            "Look for firewall or connection issues.",
            "Review network-related config changes.",
        ],
        "unknown": [
            "Review the full stack trace.",
            "Check recent code or config changes.",
            "Identify whether the issue is reproducible.",
            "Add logging around the failure point.",
        ],
    }

    return {
        "category": category,
        "next_steps": checklists.get(category, checklists["unknown"])
    }