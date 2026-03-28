import pytest

from plate_validator import (
    AuditManager,
    PatternRegistry,
    PlateValidatorApp,
    SecurityValidator,
    ValidatorEngine,
)


def test_california_format():
    engine = ValidatorEngine()
    ca_data = {"pattern": "^[0-9][A-Z]{3}[0-9]{3}$"}
    assert engine.validate("7GHT429", ca_data)[0] is True
    assert engine.validate("ABC1234", ca_data)[0] is False


def test_leetspeak_filter():
    security = SecurityValidator()
    assert security.is_appropriate("B4D-PLT")[0] is False
    assert security.is_appropriate("CLEAN")[0] is True


def test_hell_substring_not_false_positive():
    security = SecurityValidator()
    assert security.is_appropriate("HELLO")[0] is True


def test_bumble_allowed_for_bum():
    security = SecurityValidator()
    assert security.is_appropriate("BUMBLE")[0] is True
    assert security.is_appropriate("BUM")[0] is False


def test_failure_reason_uses_clean_example_length():
    engine = ValidatorEngine()
    mo = {"pattern": "^[A-Z0-9]{2}[A-Z][0-9][A-Z]$", "example": "AA1 B2C", "desc": "MO style"}
    msg = engine.get_failure_reason("AA1B2", mo)
    assert "Expected 6 chars" in msg


def test_failure_reason_first_position_kind():
    engine = ValidatorEngine()
    ca = {"pattern": "^[0-9][A-Z]{3}[0-9]{3}$", "example": "1ABC234"}
    msg = engine.get_failure_reason("AABC234", ca)
    assert "Position 1" in msg
    assert "digit" in msg


def test_failure_reason_first_position_char():
    engine = ValidatorEngine()
    ca = {"pattern": "^[0-9][A-Z]{3}[0-9]{3}$", "example": "1ABC234"}
    msg = engine.get_failure_reason("1ABZ234", ca)
    assert "Position 4" in msg
    assert "'C'" in msg
    assert "'Z'" in msg


def test_failure_reason_pattern_only_when_example_chars_match_but_regex_fails():
    engine = ValidatorEngine()
    weird = {"pattern": "^X$", "example": "Y"}
    msg = engine.get_failure_reason("Y", weird)
    assert "same length as example" in msg


def test_fullmatch_not_partial():
    engine = ValidatorEngine()
    ca = {"pattern": "^[0-9][A-Z]{3}[0-9]{3}$"}
    assert engine.validate("17GHT429", ca)[0] is False


def test_pattern_registry_skips_underscore_keys(tmp_path):
    p = tmp_path / "patterns.json"
    p.write_text(
        '{"_meta": {"note": "x"}, "ZZ": {"name": "Test", "pattern": "^A$", "example": "A"}}',
        encoding="utf-8",
    )
    reg = PatternRegistry(str(p))
    assert "ZZ" in reg.patterns
    assert "_meta" not in reg.patterns


def test_audit_log_roundtrip(tmp_path):
    log = tmp_path / "audit.json"
    mgr = AuditManager(str(log))
    mgr.log_attempt({"region": "CA", "plate": "1ABC234", "valid": True, "safe": True})
    logs = mgr.get_all_logs()
    assert len(logs) == 1
    assert logs[0]["region"] == "CA"


def test_bulk_validate_csv(tmp_path):
    csv_in = tmp_path / "in.csv"
    csv_out = tmp_path / "out.csv"
    csv_in.write_text("region,plate\nCA,7GHT429\nXX,1\n", encoding="utf-8")
    app = PlateValidatorApp()
    results, warnings = app.bulk_validate_csv(str(csv_in), str(csv_out))
    assert warnings == []
    assert len(results) == 2
    assert results[0]["Status"] == "PASS"
    assert results[1]["Status"] == "FAIL"
    text = csv_out.read_text(encoding="utf-8")
    assert "7GHT429" in text


def test_bulk_validate_csv_case_insensitive_headers(tmp_path):
    csv_in = tmp_path / "in.csv"
    csv_out = tmp_path / "out.csv"
    csv_in.write_text("Region,Plate\nCA,7GHT429\n", encoding="utf-8")
    app = PlateValidatorApp()
    results, warnings = app.bulk_validate_csv(str(csv_in), str(csv_out))
    assert warnings == []
    assert len(results) == 1
    assert results[0]["Status"] == "PASS"


def test_bulk_validate_csv_missing_column_warns(tmp_path):
    csv_in = tmp_path / "in.csv"
    csv_out = tmp_path / "out.csv"
    csv_in.write_text("region,nope\nCA,7GHT429\n", encoding="utf-8")
    app = PlateValidatorApp()
    results, warnings = app.bulk_validate_csv(str(csv_in), str(csv_out))
    assert any("plate" in w.lower() for w in warnings)
    assert results == []


def test_bulk_validate_csv_no_data_rows_warns(tmp_path):
    csv_in = tmp_path / "in.csv"
    csv_out = tmp_path / "out.csv"
    csv_in.write_text("region,plate\n", encoding="utf-8")
    app = PlateValidatorApp()
    results, warnings = app.bulk_validate_csv(str(csv_in), str(csv_out))
    assert any("No data rows" in w for w in warnings)
    assert results == []


def test_bulk_validate_csv_no_header_warns(tmp_path):
    csv_in = tmp_path / "in.csv"
    csv_out = tmp_path / "out.csv"
    csv_in.write_text("", encoding="utf-8")
    app = PlateValidatorApp()
    results, warnings = app.bulk_validate_csv(str(csv_in), str(csv_out))
    assert any("header" in w.lower() for w in warnings)
