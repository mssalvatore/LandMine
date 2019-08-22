from landmine.configuration.email_recipient import EmailRecipient
import pytest
import validate

def test_email_recpient():
    er = EmailRecipient("mike@test.test", "02-6", "8-20")
    er.validate()

    assert er.email_address == "mike@test.test"
    assert er.days_min == 2
    assert er.days_max == 6
    assert er.hours_min == 8
    assert er.hours_max == 20

def test_email_recpient_1():
    er = EmailRecipient("mike@test.test", "*", "8-20")
    er.validate()

    assert er.email_address == "mike@test.test"
    assert er.days_min == '*'
    assert er.hours_min == 8
    assert er.hours_max == 20

def test_email_recpient_2():
    er = EmailRecipient("mike@test.test", "2-6", "*")
    er.validate()

    assert er.email_address == "mike@test.test"
    assert er.days_min == 2
    assert er.days_max == 6
    assert er.hours_min == '*'

def test_bogus_email():
    with pytest.raises(validate.VdtValueError):
        EmailRecipient("bogus", "0-4", "08-20")
    with pytest.raises(validate.VdtValueError):
        er = EmailRecipient("test@test.net", "0-4", "08-20")
        er.email_address = "bogus"
        er.validate()

def test_bogus_days():
    with pytest.raises(validate.VdtValueError):
        EmailRecipient("test@test.net", "bogus-4", "08-20")
    with pytest.raises(validate.VdtValueError):
        er = EmailRecipient("test@test.net", "0-4", "08-20")
        er.days_min = "bogus"
        er.validate()

    with pytest.raises(validate.VdtValueError):
        EmailRecipient("test@test.net", "4", "08-20")
    with pytest.raises(validate.VdtValueError):
        er = EmailRecipient("test@test.net", "0-4", "08-20")
        er.days_max = ""
        er.validate()

def test_invalid_day():
    with pytest.raises(validate.VdtValueError):
        EmailRecipient("test@test.net", "0-7", "08-20")

def test_invalid_hour():
    with pytest.raises(validate.VdtValueError):
        EmailRecipient("test@test.net", "0-6", "08-24")

def test_bogus_hours():
    with pytest.raises(validate.VdtValueError):
        EmailRecipient("test@test.net", "0-4", "bogus-20")
    with pytest.raises(validate.VdtValueError):
        er = EmailRecipient("test@test.net", "0-4", "08-20")
        er.hours_min = "bogus"
        er.validate()

    with pytest.raises(validate.VdtValueError):
        EmailRecipient("test@test.net", "4", "08-20")
    with pytest.raises(validate.VdtValueError):
        er = EmailRecipient("test@test.net", "0-4", "08-20")
        er.hours_max = ""
        er.validate()

def test_from_config_str_bogus_string():
    with pytest.raises(validate.VdtValueError):
        EmailRecipient.from_config_str("bogus_string:bogus")

def test_str():
    er = EmailRecipient("test@test.net", "0-4", "8-20")
    assert str(er) == "test@test.net:0-4:8-20"

def test_str_2():
    er = EmailRecipient("test@test.net", "0-4", "*")
    assert str(er) == "test@test.net:0-4:*"
