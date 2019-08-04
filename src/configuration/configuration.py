import configobj
from configobj import ConfigObj
import copy
from email_recipient import EmailRecipient
from errors import *
from network_interface import NetworkInterface
from validate import Validator
from validate import VdtValueError
from validate import VdtTypeError
from validate import VdtMissingValue
import os
import re
from socket import AddressFamily

ALERT_THRESHOLD = 'alert_threshold'
ALERT_THRESHOLD_WINDOW = 'alert_thershold_window'
ALERTING = 'Alerting'
EMAIL_SUBJECT = 'email_subject'
LANDMINE_LOG = 'landmine_log'
LOGGING = 'Logging'
MONITORING = 'Monitoring'
NETWORK_INTERFACES = 'network_interfaces'
RECIPIENTS = 'recipients'
SMTP_PASSWORD = 'smtp_password'
SMTP_PORT = 'smtp_port'
SMTP_SERVER = 'smtp_server'
SMTP_USERNAME = 'smtp_username'
SNORT_LOG = 'snort_log'

EMAIL_ADDRESS_REGEX = "[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
DAYS_REGEX = "([0-6]-[0-6])|\*"
HOURS_REGEX = "(\d{1,2}-\d{1,2})|\*"
EMAIL_RECIPIENT_REGEX = r"^(%s)(:(%s))(:(%s))" % (EMAIL_ADDRESS_REGEX,
                                                   DAYS_REGEX,
                                                   HOURS_REGEX)

CONFIGSPEC_PATH = os.path.join(os.path.dirname(__file__), "./configspec.ini")

class Configuration:
    def __init__(self, config_file_path="./config.ini"):
        self.config_file = config_file_path
        self.config = ConfigObj(self.config_file, configspec=CONFIGSPEC_PATH,
                                list_values=True, raise_errors=True,
                                write_empty_values=True)
        self.validator = Validator()
        self._register_custom_validators()

        if os.path.isfile(self.config_file):
            self.print_errors(self.config.validate(self.validator, copy=True, preserve_errors=True))

    def _register_custom_validators(self):
        self.validator.functions['alert_recipient_list'] = Configuration._alert_recipient_list

    def print_errors(self, results):
        if results is not True:
            print(results)
            for (section_list, key, _) in configobj.flatten_errors(self.config, results):
                if key is not None:
                    print('The "%s" key in the section "%s" failed validation' % (key, ', '.join(section_list)))
                else:
                    print('The following section was missing:%s ' % ', '.join(section_list))

    def validate(self):
        return self.config.validate(self.validator, copy=True, preserve_errors=True)

    @staticmethod
    def _objects_from_comma_separated_list(config_csv, callback):
        objects = list()
        for value in config_csv.split(','):
            objects.append(callback(value))

        return objects

    @staticmethod
    def _email_recipients_from_config_list(config_csv):
        return Configuration._objects_from_comma_separated_list(config_csv,
                                Configuration._email_recipient_from_config_str)

    @staticmethod
    def _email_recipient_from_config_str(config_str):
        email_address, days, hours = Configuration._parse_and_validate_email_recipient(config_str)
        return EmailRecipient(email_address, days, hours)

    @staticmethod
    def _alert_recipient_list(recipient_list):
        # TODO: Consider subclassing Vdt Errors in order to provide more
        #       meaningful feedback
        if not isinstance(recipient_list, list):
            raise VdtTypeError(recipient_list)

        if len(recipient_list) == 0:
            raise VdtMissingValue("Recipient list must have at least one recipient")

        for recipient in recipient_list:
            Configuration._parse_and_validate_email_recipient(recipient)


    @staticmethod
    def _parse_and_validate_email_recipient(email_recipient):
        match = re.match(EMAIL_RECIPIENT_REGEX, email_recipient)
        if not match:
            # TODO: Consider subclassing VdtValueError in order to provide more
            #       meaningful feedback
            raise VdtValueError(email_recipient)

        email_address = match.group(1)
        days = match.group(3)
        hours = match.group(6)

        if days is not "*":
            days_list = days.split("-")
            if len(days_list) != 2 or days_list[0] > days_list[1]:
                raise VdtValueError(email_recipient)

        if hours is not "*":
            hours_list = hours.split("-")
            if len(hours_list) != 2 or hours_list[0] > hours_list[1]:
                raise VdtValueError(email_recipient)

        return (email_address, days, hours)

    @staticmethod
    def _network_interfaces_from_config_list(config_csv):
        return Configuration._objects_from_comma_separated_list(config_csv,
                               Configuration._network_interface_from_config_str)

    @staticmethod
    def _network_interface_from_config_str(config_str):
        match = re.match(r"(.+):(IPv4|IPv6)", config_str)
        if match:
            interface = match.group(1)
            if match.group(2) == "IPv4":
                address_family = AddressFamily.AF_INET
            elif match.group(2) == "IPv6":
                address_family = AddressFamily.AF_INET6
            else:
                pass
                # TODO: raise exception

            return NetworkInterface(interface, address_family)
        else:
            pass
            # TODO: raise exception

    def _validating_set(self, value, section, key):
        try:
            config_copy = copy.deepcopy(self.config)
            self.config[section][key] = value
            self._throw_on_invalid_config_option(section, key)
        except:
            self.config = copy.deepcopy(config_copy)
            raise

    def _throw_on_invalid_config_option(self, section, key):
        results = self.validate()

        if results is True or results[section][key] is True:
            return

        msg = results[section][key]
        raise ConfigValidationError(section, key, msg)

    @property
    def snort_log_path(self):
        return self.config[MONITORING][SNORT_LOG]

    @snort_log_path.setter
    def snort_log_path(self, log_path):
        self._validating_set(log_path, MONITORING, SNORT_LOG)

    @property
    def landmine_log_path(self):
        return self.config[LOGGING][LANDMINE_LOG]

    @landmine_log_path.setter
    def landmine_log_path(self, log_path):
        self._validating_set(log_path, LOGGING, LANDMINE_LOG)

    @property
    def smtp_server(self):
        return self.config[ALERTING][SMTP_SERVER]

    @smtp_server.setter
    def smtp_server(self, server):
        self._validating_set(server, ALERTING, SMTP_SERVER)

    @property
    def smtp_port(self):
        return self.config[ALERTING][SMTP_PORT]

    @smtp_port.setter
    def smtp_port(self, port):
        self._validating_set(port, ALERTING, SMTP_PORT)

    @property
    def smtp_username(self):
        return self.config[ALERTING][SMTP_USERNAME]

    @smtp_username.setter
    def smtp_username(self, username):
        self._validating_set(username, ALERTING, SMTP_USERNAME)

    @property
    def smtp_password(self):
        return self.config[ALERTING][SMTP_PASSWORD]

    @smtp_password.setter
    def smtp_password(self, password):
        self._validating_set(password, ALERTING, SMTP_PASSWORD)

    @property
    def alert_recipients(self):
        return Configuration._email_recipients_from_config_list(self.config[ALERTING][RECIPIENTS])

    @alert_recipients.setter
    def alert_recipients(self, recipients):
        self._validating_set(recipients, ALERTING, RECIPIENTS)

    @property
    def email_subject(self):
        return self.config[ALERTING][EMAIL_SUBJECT]

    @email_subject.setter
    def email_subject(self, subject):
        self._validating_set(subject, ALERTING, EMAIL_SUBJECT)

    @property
    def alert_threshold(self):
        return self.config[ALERTING][ALERT_THRESHOLD]

    @alert_threshold.setter
    def alert_threshold(self, threshold):
        self._validating_set(threshold, ALERTING, ALERT_THRESHOLD)

    @property
    def alert_threshold_window_min(self):
        return self.config[ALERTING][ALERT_THRESHOLD_WINDOW]

    @alert_threshold_window_min.setter
    def alert_threshold_window_min(self, threshold_window_min):
        self._validating_set(threshold_window_min, ALERTING, ALERT_THRESHOLD_WINDOW)

    def get_alert_threshold_window_sec(self):
        return self.config[ALERTING][ALERT_THRESHOLD_WINDOW] * 60

    @property
    def network_interfaces(self):
        return Configuration._network_interfaces_from_config_list(self.config[MONITORING][NETWORK_INTERFACES])

    @network_interfaces.setter
    def network_interfaces(self, interfaces):
        self._validating_set(interfaces, MONITORING, NETWORK_INTERFACES)

    def save_config(self):
        try:
            self.config.write()
        except Exception as ex:
            msg = "Error writing to config file \"%s\": %s" % (self.config_file, str(ex))
            raise ConfigError(msg)
