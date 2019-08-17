from landmine.snort_alert import SnortAlert
import pytest

@pytest.fixture(scope="function")
def snort_alert_lines():
    return ['[**] [1:20000002:0] Unexpected packet [**]',
            '[Priority: 0] ',
            '08/11-20:24:41.343538 192.168.1.10:40784 -> 192.168.1.20:22',
            'TCP TTL:64 TOS:0x10 ID:63587 IpLen:20 DgmLen:52 DF',
            '***A**** Seq: 0x63344944  Ack: 0x6D8D376  Win: 0x6C3  TcpLen: 32',
            'TCP Options (3) => NOP NOP TS: 1335606453 3706709806"""']

@pytest.fixture(scope="module")
def malformed_snort_alert_lines():
    return ['[**] 1:20000002:0',
            '[Priority: 0] ',
            '08/11-4:41343538 192.168.1.10:40784 ->192.168.1.20:22',
            '',
            '***A**** Seq: 0x63344944  Ack: 0x6D8D376  Win: 0x6C3  TcpLen: 32',
            'TCP Options (3) => NOP NOP TS: 1335606453 3706709806"""']

@pytest.fixture(scope="module")
def malformed_snort_alert_lines_2():
    return ['[**] 1:20000002:0',
            '[Priority: 0] ',
            '08/11-4:41343538192.168.1.10:40784->192.168.1.20:22']

def test_parse_rule_id(snort_alert_lines):
    expected = "20000002"
    snort_alert = SnortAlert(snort_alert_lines)
    assert snort_alert.rule_id == expected

def test_parse_alert_msg(snort_alert_lines):
    expected = "Unexpected packet"
    snort_alert = SnortAlert(snort_alert_lines)
    assert snort_alert.alert_msg == expected

def test_parse_timestamp(snort_alert_lines):
    expected = "08/11-20:24:41.343538"
    snort_alert = SnortAlert(snort_alert_lines)
    assert snort_alert.timestamp == expected

def test_parse_timestamp_empty(snort_alert_lines):
    snort_alert_lines[2] = ''
    with pytest.raises(Exception):
        snort_alert = SnortAlert(snort_alert_lines)

def test_parse_ip_port_direction(snort_alert_lines):
    expected = "192.168.1.10:40784 -> 192.168.1.20:22"
    snort_alert = SnortAlert(snort_alert_lines)
    assert snort_alert.packet_header_info == expected

def test_protocol(snort_alert_lines):
    expected = "TCP"
    snort_alert = SnortAlert(snort_alert_lines)
    assert snort_alert.protocol == expected

def test_malformed_parse_rule_id(malformed_snort_alert_lines):
    with pytest.raises(Exception):
        SnortAlert(malformed_snort_alert_lines)

def test_malformed_parse_alert_msg(snort_alert_lines):
    snort_alert_lines[0] = '** [1:20000002:0] Unexpected packet [**]'
    with pytest.raises(Exception):
        SnortAlert(snort_alert_lines)

def test_malformed_parse_timestamp(malformed_snort_alert_lines_2):
    with pytest.raises(Exception):
        SnortAlert(malformed_snort_alert_lines_2)

def test_malformed_parse_ip_port_direction(snort_alert_lines, malformed_snort_alert_lines):
    snort_alert_lines[2] = malformed_snort_alert_lines[2]
    with pytest.raises(Exception):
        SnortAlert(snort_alert_lines)

def test_malformed_protocol(snort_alert_lines, malformed_snort_alert_lines):
    snort_alert_lines[3] = malformed_snort_alert_lines[3]
    with pytest.raises(Exception):
        SnortAlert(snort_alert_lines)
