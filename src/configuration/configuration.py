import configobj
from configobj import ConfigObj
from validate import Validator
import os

class ConfigurationError(Exception):
    pass

# TODO: Call validator functions from set_*() methods
class Configuration:
    def __init__(self, config_file_path="./config.ini"):
        self.config_file = config_file_path
        #self.config = ConfigObj(configspec="./configspec.ini", list_values=True, raise_errors=True)
        self.config = ConfigObj(self.config_file, configspec="./configspec.ini", list_values=True, raise_errors=True)
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

    def set_landmine_log_path(self, log_path):
        self.config['Logging']['landmine_log'] = log_path

    def set_smtp_server(self, server):
        self.config['Alerting']['smtp_server'] = server

    def set_smtp_port(self, port):
        self.config['Alerting']['smtp_port'] = port

    def set_smtp_username(self, username):
        self.config['Alerting']['smtp_username'] = username

    def set_smtp_password(self, password):
        self.config['Alerting']['smtp_password'] = password

    def set_alert_recipients(self, recipients):
        self.config['Alerting']['Recipients'] = recipients
 
    def save_config(self):
        try:
            self.config.write()
        except Exception as ex:
            msg = "Error writing to config file \"%s\": %s" % (self.config_file, str(ex))
            raise ConfigurationError(msg)
