import re
from validate import VdtValueError

EMAIL_ADDRESS_REGEX = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
DAYS_REGEX = r"([0-6]-[0-6])|\*"
HOURS_REGEX = r"(\d{1,2}-\d{1,2})|\*"
EMAIL_RECIPIENT_REGEX = r"^(%s)(:(%s))(:(%s))" % (EMAIL_ADDRESS_REGEX,
                                                   DAYS_REGEX,
                                                   HOURS_REGEX)

class EmailRecipient:
    def __init__(self, email_address, days, hours):
        EmailRecipient._validate(email_address, days, hours)

        self.email_address = email_address

        if days == '*':
            self.days_min = '*'
            self.days_max = '*'
        else:
            self.days_min = int(days.split('-')[0].strip())
            self.days_max = int(days.split('-')[1].strip())

        if hours == '*':
            self.hours_min = '*'
            self.hours_max = '*'
        else:
            self.hours_min = int(hours.split('-')[0].strip())
            self.hours_max = int(hours.split('-')[1].strip())

    def validate(self):
        EmailRecipient._validate(self.email_address, self._days_str(), self._hours_str())

    def __str__(self):
        days = self._days_str()
        hours = self._hours_str()

        return ":".join((self.email_address, days, hours))

    def __eq__(self, other):
        if self.__class__ != other.__class__:
            return False

        return self.__dict__ == other.__dict__

    def _days_str(self):
        return EmailRecipient._range_str(str(self.days_min), str(self.days_max))

    def _hours_str(self):
        return EmailRecipient._range_str(str(self.hours_min), str(self.hours_max))

    @staticmethod
    def _range_str(min_val, max_val):
        val_str = ""
        if min_val == '*':
            val_str = '*'
        else:
            val_str = "-".join((min_val, max_val))

        return val_str

    @classmethod
    def from_config_str(cls, config_str):
        email_address, days, hours = cls._parse(config_str)
        return EmailRecipient(email_address, days, hours)

    @staticmethod
    def _parse(config_str):
        match = re.match(EMAIL_RECIPIENT_REGEX, config_str)
        if not match:
            # TODO: Consider subclassing VdtValueError in order to provide more
            #       meaningful feedback
            raise VdtValueError(config_str)

        email_address = match.group(1)
        days = match.group(3)
        hours = match.group(6)

        return email_address, days, hours

    @staticmethod
    def _split_range_str(range_str):
        try:
            range_list = list(map(int, range_str.split("-")))
        except ValueError as ve:
            raise VdtValueError(range_str)

        return range_list

    @classmethod
    def _range_is_valid(cls, range_min, range_max, value_str):
        if value_str is "*":
            return True

        values = cls._split_range_str(value_str)

        if len(values) != 2:
            return False

        for value in values:
            if range_min > value or value > range_max:
                return False

        return True

    @classmethod
    def _validate(cls, email_address, days, hours):
        if not re.match(EMAIL_ADDRESS_REGEX, email_address):
            raise VdtValueError(email_address)

        if not cls._range_is_valid(0, 6, days):
            raise VdtValueError(":".join((email_address, days, hours)))

        if not cls._range_is_valid(0, 23, hours):
            raise VdtValueError(":".join((email_address, days, hours)))
