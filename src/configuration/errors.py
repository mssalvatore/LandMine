class ConfigError(Exception):
    pass

class ConfigValidationError(ConfigError):
    def __init__(self, section, key, validation_error_msg):
        self.section = section
        self.key = key
        self.validation_error_msg = validation_error_msg

    def __str__(self):
        return 'An error occurred while validation the configuration key ' \
                '"%s" in the section "%s": %s' \
                % (self.key, self.section, self.validation_error_msg)
