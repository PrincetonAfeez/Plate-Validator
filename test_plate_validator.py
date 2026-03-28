import pytest
from plate_validator import ValidatorEngine, SecurityValidator

def test_california_format():
    engine = ValidatorEngine()
    ca_data = {"pattern": "^[0-9][A-Z]{3}[0-9]{3}$"}
    assert engine.validate("7GHT429", ca_data)[0] == True
    assert engine.validate("ABC1234", ca_data)[0] == False  # Wrong format

def test_leetspeak_filter():
    security = SecurityValidator()
    assert security.is_appropriate("B4D-PLT")[0] == False # Should catch B4D as BAD
    assert security.is_appropriate("CLEAN")[0] == True