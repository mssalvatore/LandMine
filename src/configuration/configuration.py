import configobj
from configobj import ConfigObj
from email_recipient import EmailRecipient
from errors import *
from network_interface import NetworkInterface
from validate import Validator
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

def objects_from_comma_separated_list(config_csv, callback):
    objects = list()
    for value in config_csv.split(','):
        objects.append(callback(value))

    return objects

def email_recipients_from_config_list(config_csv):
    return objects_from_comma_separated_list(config_csv, email_recipient_from_config_str)

def email_recipient_from_config_str(config_str):
    # TODO: Validate
    match = re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)(:(([0-6]-[0-6])|\*))?(:((\d{1,2}-\d{1,2})|\*))?", config_str)
    if match:
        email_address = match.group(1)
        days = match.group(3)
        hours = match.group(6)
        return EmailRecipient(email_address, days, hours)
    else:
        pass
        # TODO: raise exception

def network_interfaces_from_config_list(config_csv):
    return objects_from_comma_separated_list(config_csv, network_interface_from_config_str)

def network_interface_from_config_str(config_str):
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


# TODO: Call validator functions from set_*() methods
CONFIGSPEC_PATH = os.path.join(os.path.dirname(__file__), "./configspec.ini")
class Configuration:
    def __init__(self, config_file_path="./config.ini"):
        self.config_file = config_file_path
        self.config = ConfigObj(self.config_file, configspec=CONFIGSPEC_PATH, list_values=True, raise_errors=True)
        self.validator = Validator()
        
        if os.path.isfile(self.config_file):
            self.print_errors(self.config.validate(self.validator, copy=True))

    def print_errors(self, results):
        if results != True:
            print(results)
            for (section_list, key, _) in configobj.flatten_errors(self.config, results):
                if key is not None:
                    print('The "%s" key in the section "%s" failed validation' % (key, ', '.join(section_list)))
                else:
                    print('The following section was missing:%s ' % ', '.join(section_list))

    def validate(self):
        return self.config.validate(self.validator, copy=True)

    def set_snort_log_path(self, log_path):
        self.config[MONITORING][SNORT_LOG] = log_path

    def get_snort_log_path(self):
        return self.config[MONITORING][SNORT_LOG]

    def set_landmine_log_path(self, log_path):
        self.config[LOGGING][LANDMINE_LOG] = log_path

    def get_landmine_log_path(self):
        return self.config[LOGGING][LANDMINE_LOG]

    def set_smtp_server(self, server):
        self.config[ALERTING][SMTP_SERVER] = server

    def get_smtp_server(self):
        return self.config[ALERTING][SMTP_SERVER]

    def set_smtp_port(self, port):
        self.config[ALERTING][SMTP_PORT] = port

    def get_smtp_port(self):
        return self.config[ALERTING][SMTP_PORT]

    def set_smtp_username(self, username):
        self.config[ALERTING][SMTP_USERNAME] = username

    def get_smtp_username(self):
        return self.config[ALERTING][SMTP_USERNAME]

    def set_smtp_password(self, password):
        self.config[ALERTING][SMTP_PASSWORD] = password

    def get_smtp_password(self):
        return self.config[ALERTING][SMTP_PASSWORD]

    def set_alert_recipients(self, recipients):
        self.config[ALERTING][RECIPIENTS] = recipients

    def get_alert_recipients(self):
        return email_recipients_from_config_list(self.config[ALERTING][RECIPIENTS])

    def set_email_subject(self, subject):
        self.config[ALERTING][EMAIL_SUBJECT] = subject

    def get_email_subject(self):
        return self.config[ALERTING][EMAIL_SUBJECT]

    def set_alert_threshold(self, threshold):
        self.config[ALERTING][ALERT_THRESHOLD] = threshold

    def get_alert_threshold(self):
        return self.config[ALERTING][ALERT_THRESHOLD]

    def set_alert_threshold_window_min(self, threshold_window_min):
        self.config[ALERTING][ALERT_THRESHOLD_WINDOW] = threshold_window_min

    def get_alert_threshold_window_min(self):
        return self.config[ALERTING][ALERT_THRESHOLD_WINDOW]

    def get_alert_threshold_window_sec(self):
        return self.config[ALERTING][ALERT_THRESHOLD_WINDOW] * 60

    def set_network_interfaces(self, interfaces):
        self.config[MONITORING][NETWORK_INTERFACES] = interfaces

    def get_network_interfaces(self):
        return network_interfaces_from_config_list(self.config[MONITORING][NETWORK_INTERFACES])
 
    def save_config(self):
        try:
            self.config.write()
        except Exception as ex:
            msg = "Error writing to config file \"%s\": %s" % (self.config_file, str(ex))
            raise ConfigurationError(msg)
