class EmailRecipient:
    def __init__(self, email_address, days, hours):
        # TODO: Validate
        self.email_address = email_address

        if days is None or days == '*':
            self.days_min = '*'
            self.days_max = '*'
        else:
            self.days_min = int(days.split('-')[0].strip())
            self.days_max = int(days.split('-')[1].strip())

        if hours is None or hours == '*':
            self.hours_min = '*'
            self.hours_max = '*'
        else:
            self.hours_min = int(hours.split('-')[0].strip())
            self.hours_max = int(hours.split('-')[1].strip())
