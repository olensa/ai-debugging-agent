from app.tools import classify_error, extract_signals, investigation_checklist


def test_classify_error_null_pointer():
    text = "java.lang.NullPointerException at PaymentService.process(PaymentService.java:142)"
    result = classify_error(text)

    assert result["error_type"] == "NullPointerException"
    assert result["category"] == "null_reference"
    assert result["severity"] == "high"


def test_classify_error_timeout():
    text = "Request timed out after 30 seconds"
    result = classify_error(text)

    assert result["category"] == "timeout"
    assert result["severity"] == "high"


def test_extract_signals_finds_exception_and_file():
    text = """
    java.lang.NullPointerException
        at com.example.PaymentService.process(PaymentService.java:142)
    """
    result = extract_signals(text)

    assert "NullPointerException" in result["exception_names"]
    assert "PaymentService.java" in result["filenames"]
    assert "com.example.PaymentService.process" in result["method_names"]


def test_extract_signals_finds_keywords():
    text = "Database timeout in payment flow"
    result = extract_signals(text)

    assert "database" in result["keywords"]
    assert "timeout" in result["keywords"]
    assert "payment" in result["keywords"]


def test_investigation_checklist_database():
    result = investigation_checklist("database")

    assert result["category"] == "database"
    assert len(result["next_steps"]) > 0
    assert "Verify database connectivity." in result["next_steps"]


def test_investigation_checklist_unknown():
    result = investigation_checklist("something_weird")

    assert result["category"] == "something_weird"
    assert len(result["next_steps"]) > 0