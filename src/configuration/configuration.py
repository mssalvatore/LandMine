import configobj
from configobj import ConfigObj
from validate import Validator
import os
import re
from socket import AddressFamily

class ConfigurationError(Exception):
    pass

def objects_from_comma_separated_list(config_csv, callback):
    objects = list()
    for value in config_csv.split(','):
        objects.append(callback(value))

    return objects

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

        print(hours)
        if hours is None or hours == '*':
            self.hours_min = '*'
            self.hours_max = '*'
        else:
            self.hours_min = int(hours.split('-')[0].strip())
            self.hours_max = int(hours.split('-')[1].strip())

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


class NetworkInterface:
    def __init__(self, interface, address_family):
        self.interface = interface
        self.address_family = address_family

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
        self.config['Monitoring']['snort_log'] = log_path

    def get_snort_log_path(self):
        return self.config['Monitoring']['snort_logfile']

    def set_landmine_log_path(self, log_path):
        self.config['Logging']['landmine_log'] = log_path

    def get_landmine_log_path(self):
        return self.config['Logging']['landmine_log']

    def set_smtp_server(self, server):
        self.config['Alerting']['smtp_server'] = server

    def get_smtp_server(self):
        return self.config['Alerting']['smtp_server']

    def set_smtp_port(self, port):
        self.config['Alerting']['smtp_port'] = port

    def get_smtp_port(self):
        return self.config['Alerting']['smtp_port']

    def set_smtp_username(self, username):
        self.config['Alerting']['smtp_username'] = username

    def get_smtp_username(self):
        return self.config['Alerting']['smtp_username']

    def set_smtp_password(self, password):
        self.config['Alerting']['smtp_password'] = password

    def get_smtp_password(self):
        return self.config['Alerting']['smtp_password']

    def set_alert_recipients(self, recipients):
        self.config['Alerting']['Recipients'] = recipients

    def get_alert_recipients(self):
        return email_recipients_from_config_list(self.config['Alerting']['recipients'])

    def set_email_subject(self, subject):
        self.config['Alerting']['email_subject'] = subject

    def get_email_subject(self):
        return self.config['Alerting']['email_subject']

    def set_alert_threshold(self, threshold):
        self.config['Alerting']['alert_threshold'] = threshold

    def get_alert_threshold(self):
        return self.config['Alerting']['alert_threshold']

    def set_alert_threshold_window_min(self, threshold_window_min):
        self.config['Alerting']['alert_threshold_window'] = threshold_window_min

    def get_alert_threshold_window_min(self):
        return self.config['Alerting']['alert_threshold_window']

    def get_alert_threshold_window_sec(self):
        return self.config['Alerting']['alert_threshold_window'] * 60

    def set_network_interfaces(self, interfaces):
        self.config['Monitoring']['network_interfaces'] = interfaces

    def get_network_interfaces(self):
        return network_interfaces_from_config_list(self.config['Monitoring']['network_interfaces'])
 
    def save_config(self):
        try:
            self.config.write()
        except Exception as ex:
            msg = "Error writing to config file \"%s\": %s" % (self.config_file, str(ex))
            raise ConfigurationError(msg)
