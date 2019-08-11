from datetime import datetime
from landmine import landmine
from landmine.configuration.email_recipient import EmailRecipient
import pytest

class TestLandmine:
    def test_is_within_time_window_star_star(self):
        dtime = datetime(2019, 8, 9, hour=22, minute=24) # Friday (4)
        recipient = EmailRecipient("test@test.test", "*", "*")

        assert landmine.is_within_time_window(dtime, recipient)

    def test_is_within_time_window_day_within_range(self):
        dtime = datetime(2019, 8, 9, hour=22, minute=24) # Friday (4)
        recipient = EmailRecipient("test@test.test", "0-4", "*")

        assert landmine.is_within_time_window(dtime, recipient)

    def test_is_within_time_window_day_over(self):
        dtime = datetime(2019, 8, 9, hour=22, minute=24) # Friday (4)
        recipient = EmailRecipient("test@test.test", "0-3", "*")

        assert not landmine.is_within_time_window(dtime, recipient)

    def test_is_within_time_window_day_under(self):
        dtime = datetime(2019, 8, 9, hour=22, minute=24) # Friday (4)
        recipient = EmailRecipient("test@test.test", "5-6", "*")

        assert not landmine.is_within_time_window(dtime, recipient)

    def test_is_within_time_window_day_within_cyclical(self):
        dtime = datetime(2019, 8, 9, hour=22, minute=24) # Friday (4)
        recipient = EmailRecipient("test@test.test", "3-1", "*")

        assert landmine.is_within_time_window(dtime, recipient)

    def test_is_within_time_window_day_outside_cyclical(self):
        dtime = datetime(2019, 8, 9, hour=22, minute=24) # Friday (4)
        recipient = EmailRecipient("test@test.test", "5-2", "*")

        assert not landmine.is_within_time_window(dtime, recipient)
