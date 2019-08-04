import re
from validate import VdtValueError

EMAIL_ADDRESS_REGEX = "[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
DAYS_REGEX = "([0-6]-[0-6])|\*"
HOURS_REGEX = "(\d{1,2}-\d{1,2})|\*"
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

    def __str__(self):
        days = ""
        if self.days_min == '*':
            days = '*'
        else:
            days = "-".join((str(self.days_min), str(self.days_max)))

        hours = ""
        if self.hours_min == '*':
            hours = '*'
        else:
            hours = "-".join((str(self.hours_min), str(self.hours_max)))

        return ":".join((self.email_address, days, hours))

    @staticmethod
    def from_config_str(config_str):
        email_address, days, hours = EmailRecipient._parse(config_str)
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
    def _validate(email_address, days, hours):
        if not re.match(EMAIL_ADDRESS_REGEX, email_address):
            raise VdtValueError(email_address)

        if days is not "*":
            days_list = days.split("-")
            if len(days_list) != 2 or days_list[0] > days_list[1]:
                raise VdtValueError(":".join((email_address, days, hours)))

        if hours is not "*":
            hours_list = hours.split("-")
            if len(hours_list) != 2 or hours_list[0] > hours_list[1]:
                raise VdtValueError(":".join((email_address, days, hours)))

