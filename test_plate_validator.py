import pytest
from plate_validator import ValidatorEngine, SecurityValidator

def test_california_format():
    engine = ValidatorEngine()
    ca_data = {"pattern": "^[0-9][A-Z]{3}[0-9]{3}$"}
    assert engine.validate("7GHT429", ca_data)[0] == True
    assert engine.validate("ABC1234", ca_data)[0] == False  # Wrong format

def test_leetspeak_filter():
    security = SecurityValidator()
    assert security.is_appropriate("B4D-PLT")[0] == False  # Should catch B4D as BAD
    assert security.is_appropriate("CLEAN")[0] == True


def test_hell_substring_not_false_positive():
    security = SecurityValidator()
    assert security.is_appropriate("HELLO")[0] is True


def test_failure_reason_uses_clean_example_length():
    engine = ValidatorEngine()
    mo = {"pattern": "^[A-Z0-9]{2}[A-Z][0-9][A-Z]$", "example": "AA1 B2C", "desc": "MO style"}
    msg = engine.get_failure_reason("AA1B2", mo)
    assert "Expected 6 chars" in msg


def test_fullmatch_not_partial():
    engine = ValidatorEngine()
    ca = {"pattern": "^[0-9][A-Z]{3}[0-9]{3}$"}
    assert engine.validate("17GHT429", ca)[0] is False