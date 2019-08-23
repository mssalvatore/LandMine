import configobj
from configobj import ConfigObj
import copy
from .email_recipient import EmailRecipient
from .errors import *
from .network_interface import NetworkInterface
import os
import re
from socket import AddressFamily
from validate import Validator
from validate import VdtTypeError
from validate import VdtMissingValue

ALERT_THRESHOLD = 'alert_threshold'
ALERT_THRESHOLD_WINDOW = 'alert_threshold_window'
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
SNORT_LOG = 'snort_logfile'
SUPPRESS_DUPLICATES = 'suppress_duplicate_alerts'

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
        self.validator.functions['alert_recipient_list'] = Configuration._validate_alert_recipient_list
        self.validator.functions['network_interface_list'] = Configuration._validate_network_interface_list

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
    def _validate_list_items(config_list_items, cls):
        # TODO: Consider subclassing Vdt Errors in order to provide more
        #       meaningful feedback
        if not isinstance(config_list_items, list):
            raise VdtTypeError(config_list_items)

        if len(config_list_items) == 0:
            raise VdtMissingValue("Lists must contain at least one item")

        validated_results = list()
        for item in config_list_items:
            if type(item) is str:
                validated_results.append(cls.from_config_str(item))
            elif type(item) is cls:
                item.validate()
                validated_results.append(item)
            else:
                raise VdtTypeError(item)

        return validated_results

    @staticmethod
    def _validate_alert_recipient_list(recipient_list):
        return Configuration._validate_list_items(recipient_list, EmailRecipient)

    @staticmethod
    def _validate_network_interface_list(network_interface_list):
        return Configuration._validate_list_items(network_interface_list, NetworkInterface)

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
        return self.config[ALERTING][RECIPIENTS]

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
    def suppress_duplicate_alerts(self):
        return self.config[ALERTING][SUPPRESS_DUPLICATES]

    @suppress_duplicate_alerts.setter
    def suppress_duplicate_alerts(self, suppress_duplicate_alerts):
        self._validating_set(suppress_duplicate_alerts, ALERTING, SUPPRESS_DUPLICATES)

    @property
    def network_interfaces(self):
        return self.config[MONITORING][NETWORK_INTERFACES]

    @network_interfaces.setter
    def network_interfaces(self, interfaces):
        self._validating_set(interfaces, MONITORING, NETWORK_INTERFACES)

    def save_config(self):
        try:
            self.config.write()
        except Exception as ex:
            msg = "Error writing to config file \"%s\": %s" % (self.config_file, str(ex))
            raise ConfigError(msg)
