from landmine.configuration.configuration import Configuration
from landmine.configuration.email_recipient import EmailRecipient
from landmine.configuration.network_interface import NetworkInterface
from landmine.configuration.errors import ConfigValidationError
from landmine.configuration.errors import ConfigError
import hashlib
import os
import pytest
import tempfile
import validate

TEST_CONFIG_PATH = "tests/assets/test_config.ini"
@pytest.fixture
def config():
    cwd = os.getcwd()
    return Configuration(os.path.join(cwd, TEST_CONFIG_PATH))

@pytest.fixture
def recipients():
    recipients = list()
    recipients.append(EmailRecipient("test@test.net", "0-6", "*"));
    recipients.append(EmailRecipient("test2@test.com", "*", "*"));
    recipients.append(EmailRecipient("test3@example.edu", "1-5", "9-17"));

    return recipients

@pytest.fixture
def network_interfaces():
    network_interfaces = list()
    network_interfaces.append(NetworkInterface("eth0", "IPv4"));
    network_interfaces.append(NetworkInterface("ethA", "IPv4"));
    network_interfaces.append(NetworkInterface("ethB", "IPv6"));

    return network_interfaces

def test_construct_from_file(config, recipients, network_interfaces):
    assert config.snort_log_path == '/var/log/snort/alert'
    assert config.alert_recipients == recipients
    assert config.network_interfaces == network_interfaces
    assert config.smtp_server == 'smtp.example.com'
    assert config.smtp_port == 587
    assert config.smtp_username == 'testuser'
    assert config.smtp_password == 'testpassword'
    assert config.email_subject == 'LandMine Alert!'
    assert config.alert_threshold == 10
    assert config.alert_threshold_window_min == 5
    assert config.suppress_duplicate_alerts == True
    assert config.landmine_log_path == '/var/snap/current/common/landmine.log'

def test_set_snort_log_path(config):
    config.snort_log_path = "/tmp/bogus"
    assert config.snort_log_path == "/tmp/bogus"

def test_set_snort_log_path_invalid_type(config):
    with pytest.raises(ConfigValidationError):
        config.snort_log_path = 1

def test_set_landmine_log_path(config):
    config.landmine_log_path = "/tmp/bogus"
    assert config.landmine_log_path == "/tmp/bogus"

def test_set_landmine_log_path_invalid_type(config):
    with pytest.raises(ConfigValidationError):
        config.landmine_log_path = 1

def test_set_smtp_server(config):
    config.smtp_server = "test.smtp.net"
    assert config.smtp_server == "test.smtp.net"

def test_set_smtp_server_invalid_type(config):
    with pytest.raises(ConfigValidationError):
        config.smtp_server = 1

def test_set_smtp_port(config):
    config.smtp_port = 1919
    assert config.smtp_port == 1919

def test_set_smtp_port_low(config):
    with pytest.raises(ConfigValidationError):
        config.smtp_port=0
    with pytest.raises(ConfigValidationError):
        config.smtp_port=-1

def test_set_smtp_port_high(config):
    with pytest.raises(ConfigValidationError):
        config.smtp_port=65536

def test_set_smtp_username(config):
    config.smtp_username = "user1"
    assert config.smtp_username == "user1"

def test_set_smtp_username_invalid_type(config):
    with pytest.raises(ConfigValidationError):
        config.smtp_username = ["hello"]

def test_set_smtp_password(config):
    config.smtp_password = "mypasswd"
    assert config.smtp_password == "mypasswd"

def test_set_smtp_password_invalid_type(config):
    with pytest.raises(ConfigValidationError):
        config.smtp_password = False

def test_set_alert_recipients(recipients):
    config = Configuration()
    config.alert_recipients = recipients

def test_set_alert_recipients_empty_list():
    config = Configuration()
    with pytest.raises(ConfigValidationError):
        config.alert_recipients = list()

def test_set_alert_recipients_not_list():
    config = Configuration()
    with pytest.raises(ConfigValidationError):
        config.alert_recipients = "hello"

def test_set_alert_recipients_wrong_type_in_list():
    config = Configuration()
    a_list = [1,2]
    with pytest.raises(ConfigValidationError):
        config.alert_recipients = a_list

def test_set_network_interfaces(network_interfaces):
    config = Configuration()
    config.network_interfaces = network_interfaces

def test_set_network_interfaces_empty_list():
    config = Configuration()
    with pytest.raises(ConfigValidationError):
        config.network_interfaces = list()

def test_set_network_interfaces_not_list():
    config = Configuration()
    with pytest.raises(ConfigValidationError):
        config.network_interfaces = "hello"

def test_set_network_interfaces_wrong_type_in_list():
    config = Configuration()
    a_list = [1,2]
    with pytest.raises(ConfigValidationError):
        config.network_interfaces = a_list

def test_set_email_subject(config):
    config.email_subject = "AN EMAIL SUBJECT"
    assert config.email_subject == "AN EMAIL SUBJECT"

def test_set_email_subject_invalid_type(config):
    with pytest.raises(ConfigValidationError):
        config.email_subject = dict()

def test_set_alert_threshold(config):
    config.alert_threshold = 10
    assert config.alert_threshold == 10

def test_set_alert_threshold_invalid_type(config):
    with pytest.raises(ConfigValidationError):
        config.alert_threshold = "hello"

def test_set_alert_threshold_low(config):
    with pytest.raises(ConfigValidationError):
        config.alert_threshold = -1

def test_set_alert_threshold_window(config):
    config.alert_threshold_window_min = 10
    assert config.alert_threshold_window_min == 10

def test_set_alert_threshold_window_invalid_type(config):
    with pytest.raises(ConfigValidationError):
        config.alert_threshold_window_min = "hello"

def test_set_alert_threshold_window_low(config):
    with pytest.raises(ConfigValidationError):
        config.alert_threshold_window_min = -1

def test_alert_threshold_window_sec(config):
    assert config.get_alert_threshold_window_sec() == 300

def test_set_suppress_duplicate_alerts(config):
    config.suppress_duplicate_alerts = False
    assert config.suppress_duplicate_alerts is False

def test_set_suppress_duplicate_alerts_invalid_type(config):
    with pytest.raises(ConfigValidationError):
        config.suppress_duplicate_alerts = "hello"

def calc_sha256sum_of_file(file_name, block_size=65536):
    sha256 = hashlib.sha256()
    with open(file_name, 'rb') as f:
        for block in iter(lambda: f.read(block_size), b''):
            sha256.update(block)
    return sha256.hexdigest()

def test_save_config(config):
    tmp_config = tempfile.NamedTemporaryFile()
    config.config.filename = tmp_config.name
    config.save_config()

    orig_config_hash = calc_sha256sum_of_file(TEST_CONFIG_PATH)
    new_config_hash = calc_sha256sum_of_file(tmp_config.name)

    assert  new_config_hash == orig_config_hash

def test_save_config(config):
    with pytest.raises(ConfigError):
        config.config.filename = "/long/bogus/filepath/that/shouldnt/exist/1337"
        config.save_config()
