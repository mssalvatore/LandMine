from datetime import datetime
from landmine import landmine
from landmine.configuration.email_recipient import EmailRecipient
import pytest

@pytest.fixture(scope="module")
def friday_datetime():
    return datetime(2019, 8, 9, hour=18, minute=24) # Friday (4)

def test_is_within_time_window_star_star(friday_datetime):
    recipient = EmailRecipient("test@test.test", "*", "*")
    assert landmine.is_within_time_window(friday_datetime, recipient)

def test_is_within_time_window_day_within_range(friday_datetime):
    recipient = EmailRecipient("test@test.test", "0-4", "*")
    assert landmine.is_within_time_window(friday_datetime, recipient)

def test_is_within_time_window_day_over(friday_datetime):
    recipient = EmailRecipient("test@test.test", "0-3", "*")
    assert not landmine.is_within_time_window(friday_datetime, recipient)

def test_is_within_time_window_day_under(friday_datetime):
    recipient = EmailRecipient("test@test.test", "5-6", "*")
    assert not landmine.is_within_time_window(friday_datetime, recipient)

def test_is_within_time_window_day_within_cyclical(friday_datetime):
    recipient = EmailRecipient("test@test.test", "3-1", "*")
    assert landmine.is_within_time_window(friday_datetime, recipient)

def test_is_within_time_window_day_outside_cyclical(friday_datetime):
    recipient = EmailRecipient("test@test.test", "5-2", "*")
    assert not landmine.is_within_time_window(friday_datetime, recipient)

def test_is_within_time_window_hour_within_range(friday_datetime):
    recipient = EmailRecipient("test@test.test", "*", "12-20")
    assert landmine.is_within_time_window(friday_datetime, recipient)

def test_is_within_time_window_hour_over(friday_datetime):
    recipient = EmailRecipient("test@test.test", "*", "12-18")
    assert not landmine.is_within_time_window(friday_datetime, recipient)

def test_is_within_time_window_hour_under(friday_datetime):
    recipient = EmailRecipient("test@test.test", "*", "19-23")
    assert not landmine.is_within_time_window(friday_datetime, recipient)

def test_is_within_time_window_hour_within_cyclical(friday_datetime):
    recipient = EmailRecipient("test@test.test", "*", "16-04")
    assert landmine.is_within_time_window(friday_datetime, recipient)

def test_is_within_time_window_hour_outside_cyclical(friday_datetime):
    recipient = EmailRecipient("test@test.test", "*", "19-17")
    assert not landmine.is_within_time_window(friday_datetime, recipient)
