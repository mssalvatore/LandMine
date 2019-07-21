import configparser

class ConfigurationError(Exception):
    pass

# TODO: Call validator functions from set_*() methods
class Configuration:
    def __init__(self):
        self.config_file = "./config.ini"
        self.config = configparser.ConfigParser()
        self._set_config_defaults()

    def _set_config_defaults(self):
        self.config['Logging'] = dict()
        self.set_landmine_log_path("/var/snap/current/common/landmine.log")
        self.set_snort_log_path("DUMMY_VALUE")

    def set_landmine_log_path(self, log_path):
        self.config['Logging']['landmine_log'] = log_path

    def set_snort_log_path(self, log_path):
        self.config['Logging']['snort_log'] = log_path
 
    def save_config(self):
        try:
            with open(self.config_file, "w") as cf:
                self.config.write(cf)
        except Exception as ex:
            msg = "Error writing to config file \"%s\": %s" % (self.config_file, str(ex))
            raise ConfigurationError(msg)
