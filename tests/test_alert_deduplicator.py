from landmine.alert_deduplicator import AlertDeduplicator
from landmine.snort_alert import SnortAlert
import pytest

@pytest.fixture(scope="module")
def snort_alert():
    snort_alert_lines = \
    ['[**] [1:20000002:0] Unexpected packet [**]',
     '[Priority: 0] ',
     '08/11-20:24:41.343538 192.168.1.10:40784 -> 192.168.1.20:22',
     'TCP TTL:64 TOS:0x10 ID:63587 IpLen:20 DgmLen:52 DF',
     '***A**** Seq: 0x63344944  Ack: 0x6D8D376  Win: 0x6C3  TcpLen: 32',
     'TCP Options (3) => NOP NOP TS: 1335606453 3706709806"""']

    return SnortAlert(snort_alert_lines)

@pytest.fixture(scope="module")
def snort_alert_dup():
    snort_alert_lines = \
    ['[**] [1:20000002:0] Unexpected packet [**]',
     '[Priority: 0] ',
     '08/11-20:24:42.628128 192.168.1.10:40784 -> 192.168.1.20:22',
     'TCP TTL:64 TOS:0x10 ID:63587 IpLen:20 DgmLen:52 DF',
     '***A**** Seq: 0x63344944  Ack: 0x6D8D376  Win: 0x6C3  TcpLen: 32',
     'TCP Options (3) => NOP NOP TS: 1335606453 3706709806"""']

    return SnortAlert(snort_alert_lines)

@pytest.fixture(scope="module")
def snort_alert_2():
    snort_alert_lines = \
    ['[**] [1:20000001:0] Unexpected packet [**]',
     '[Priority: 0] ',
     '08/11-20:24:41.343538 192.168.1.20:22 -> 192.168.1.10:40784',
     'TCP TTL:64 TOS:0x10 ID:63587 IpLen:20 DgmLen:52 DF',
     '***A**** Seq: 0x63344944  Ack: 0x6D8D376  Win: 0x6C3  TcpLen: 32',
     'TCP Options (3) => NOP NOP TS: 1335606453 3706709806"""']

    return SnortAlert(snort_alert_lines)

def test_supress_past_threshold(snort_alert, snort_alert_dup):
    alert_dedup = AlertDeduplicator(1, 600, False)
    assert alert_dedup.should_send_new_alert(snort_alert)
    assert not alert_dedup.should_send_new_alert(snort_alert_dup)

def test_supress_duplicate(snort_alert, snort_alert_dup):
    alert_dedup = AlertDeduplicator(2, 600, True)
    assert alert_dedup.should_send_new_alert(snort_alert)
    assert not alert_dedup.should_send_new_alert(snort_alert_dup)

def test_send_duplicate(snort_alert, snort_alert_dup):
    alert_dedup = AlertDeduplicator(2, 600, False)
    assert alert_dedup.should_send_new_alert(snort_alert)
    assert alert_dedup.should_send_new_alert(snort_alert_dup)

def test_send_non_duplicates(snort_alert, snort_alert_2):
    alert_dedup = AlertDeduplicator(2, 600, True)
    assert alert_dedup.should_send_new_alert(snort_alert)
    assert alert_dedup.should_send_new_alert(snort_alert_2)

def test_threshold_window_elapsed(snort_alert, snort_alert_dup):
    threshold_window_sec = 600
    current_time = 1566347420

    alert_dedup = AlertDeduplicator(1, threshold_window_sec, True)
    assert alert_dedup.should_send_new_alert(snort_alert, current_time)
    assert alert_dedup.should_send_new_alert(snort_alert_2, current_time + threshold_window_sec + 1)

def test_threshold_window_elapsed_2(snort_alert):
    threshold_window_sec = 600
    alert_1_time = 1566347420
    alert_2_time = alert_1_time + 100

    alert_dedup = AlertDeduplicator(2, threshold_window_sec, False)
    assert alert_dedup.should_send_new_alert(snort_alert, alert_1_time)
    assert alert_dedup.should_send_new_alert(snort_alert, alert_2_time)
    assert alert_dedup.should_send_new_alert(snort_alert, alert_2_time + threshold_window_sec + 1)

def test_threshold_window_elapsed_duplicate(snort_alert, snort_alert_dup):
    threshold_window_sec = 600
    current_time = 1566347420

    alert_dedup = AlertDeduplicator(1, threshold_window_sec, True)
    assert alert_dedup.should_send_new_alert(snort_alert, current_time)
    assert alert_dedup.should_send_new_alert(snort_alert_dup, current_time + threshold_window_sec + 1)

def test_threshold_window_elapsed_duplicate_2(snort_alert, snort_alert_dup):
    threshold_window_sec = 600
    current_time = 1566347420

    alert_dedup = AlertDeduplicator(1, threshold_window_sec, True)
    assert alert_dedup.should_send_new_alert(snort_alert, current_time)
    assert not alert_dedup.should_send_new_alert(snort_alert_dup, current_time + 10)
    assert alert_dedup.should_send_new_alert(snort_alert_dup, current_time + threshold_window_sec + 1)
