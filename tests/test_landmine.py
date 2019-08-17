from datetime import datetime
from landmine import landmine
from landmine.configuration.email_recipient import EmailRecipient
import pytest

@pytest.fixture(scope="module")
def friday_datetime():
    return datetime(2019, 8, 9, hour=18, minute=24) # Friday (4)

def test_is_within_time_window_star_star(friday_datetime):
    recipient = EmailRecipient("test@test.test", "*", "*")
    assert landmine.is_within_time_window(friday_datetime, recipient)

def test_is_within_time_window_day_within_range(friday_datetime):
    recipient = EmailRecipient("test@test.test", "0-4", "*")
    assert landmine.is_within_time_window(friday_datetime, recipient)

def test_is_within_time_window_day_over(friday_datetime):
    recipient = EmailRecipient("test@test.test", "0-3", "*")
    assert not landmine.is_within_time_window(friday_datetime, recipient)

def test_is_within_time_window_day_under(friday_datetime):
    recipient = EmailRecipient("test@test.test", "5-6", "*")
    assert not landmine.is_within_time_window(friday_datetime, recipient)

def test_is_within_time_window_day_within_cyclical(friday_datetime):
    recipient = EmailRecipient("test@test.test", "3-1", "*")
    assert landmine.is_within_time_window(friday_datetime, recipient)

def test_is_within_time_window_day_outside_cyclical(friday_datetime):
    recipient = EmailRecipient("test@test.test", "5-2", "*")
    assert not landmine.is_within_time_window(friday_datetime, recipient)

def test_is_within_time_window_hour_within_range(friday_datetime):
    recipient = EmailRecipient("test@test.test", "*", "12-20")
    assert landmine.is_within_time_window(friday_datetime, recipient)

def test_is_within_time_window_hour_over(friday_datetime):
    recipient = EmailRecipient("test@test.test", "*", "12-18")
    assert not landmine.is_within_time_window(friday_datetime, recipient)

def test_is_within_time_window_hour_under(friday_datetime):
    recipient = EmailRecipient("test@test.test", "*", "19-23")
    assert not landmine.is_within_time_window(friday_datetime, recipient)

def test_is_within_time_window_hour_within_cyclical(friday_datetime):
    recipient = EmailRecipient("test@test.test", "*", "16-04")
    assert landmine.is_within_time_window(friday_datetime, recipient)

def test_is_within_time_window_hour_outside_cyclical(friday_datetime):
    recipient = EmailRecipient("test@test.test", "*", "19-17")
    assert not landmine.is_within_time_window(friday_datetime, recipient)

@pytest.fixture(scope="function")
def snort_alert():
    return ['[**] [1:20000002:0] Unexpected packet [**]',
            '[Priority: 0] ',
            '08/11-20:24:41.343538 192.168.1.10:40784 -> 192.168.1.20:22',
            'TCP TTL:64 TOS:0x10 ID:63587 IpLen:20 DgmLen:52 DF',
            '***A**** Seq: 0x63344944  Ack: 0x6D8D376  Win: 0x6C3  TcpLen: 32',
            'TCP Options (3) => NOP NOP TS: 1335606453 3706709806"""']

@pytest.fixture(scope="module")
def malformed_snort_alert():
    return ['[**] 1:20000002:0',
            '[Priority: 0] ',
            '08/11-4:41343538 192.168.1.10:40784 ->192.168.1.20:22',
            '',
            '***A**** Seq: 0x63344944  Ack: 0x6D8D376  Win: 0x6C3  TcpLen: 32',
            'TCP Options (3) => NOP NOP TS: 1335606453 3706709806"""']

@pytest.fixture(scope="module")
def malformed_snort_alert_2():
    return ['[**] 1:20000002:0',
            '[Priority: 0] ',
            '08/11-4:41343538192.168.1.10:40784->192.168.1.20:22']

def test_parse_rule_id(snort_alert):
    expected = "20000002"
    assert landmine.parse_rule_id(snort_alert) == expected

def test_parse_alert_msg(snort_alert):
    expected = "Unexpected packet"
    assert landmine.parse_alert_msg(snort_alert) == expected

def test_parse_timestamp(snort_alert):
    expected = "08/11-20:24:41.343538"
    assert landmine.parse_timestamp(snort_alert) == expected

def test_parse_timestamp_empty(snort_alert):
    snort_alert[2] = ''
    with pytest.raises(Exception):
        landmine.parse_timestamp(snort_alert)

def test_parse_ip_port_direction(snort_alert):
    expected = "192.168.1.10:40784 -> 192.168.1.20:22"
    assert landmine.parse_packet_ip_port_direction(snort_alert) == expected

def test_protocol(snort_alert):
    expected = "TCP"
    assert landmine.parse_protocol(snort_alert) == expected

def test_malformed_parse_rule_id(malformed_snort_alert):
    with pytest.raises(Exception):
        landmine.parse_rule_id(malformed_snort_alert)

def test_malformed_parse_alert_msg(malformed_snort_alert):
    with pytest.raises(Exception):
        landmine.parse_alert_msg(malformed_snort_alert)

def test_malformed_parse_timestamp(malformed_snort_alert_2):
    with pytest.raises(Exception):
        landmine.parse_timestamp(malformed_snort_alert)

def test_malformed_parse_ip_port_direction(malformed_snort_alert):
    with pytest.raises(Exception):
        landmine.parse_packet_ip_port_direction(malformed_snort_alert)

def test_malformed_protocol(malformed_snort_alert):
    with pytest.raises(Exception):
        landmine.parse_protocol(malformed_snort_alert)
