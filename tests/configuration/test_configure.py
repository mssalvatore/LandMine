from landmine.configuration import configtool
from psutil import _common
import psutil
import pytest
from socket import AddressFamily

def net_if_addrs():
#    return { "eth0": [
    return {"eth0": [
                _common.snicaddr(
                    family=AddressFamily.AF_INET,
                    address="192.168.1.10",
                    netmask="255.255.255.0",
                    broadcast="192.168.1.255",
                    ptp=None),
                _common.snicaddr(
                    family=AddressFamily.AF_INET6,
                    address="2001:0db8:ac10:fe01::%eth0",
                    netmask="ffff:ffff:ffff:ffff::",
                    broadcast="ff:ff:ff:ff:ff:ff",
                    ptp=None)],
            "lo": [
                _common.snicaddr(
                    family=AddressFamily.AF_INET,
                    address="127.0.0.1",
                    netmask="255.0.0.0",
                    broadcast=None,
                    ptp=None),
                _common.snicaddr(
                    family=AddressFamily.AF_INET6,
                    address="::1",
                    netmask="ffff:ffff:ffff:ffff::",
                    broadcast=None,
                    ptp=None)]}

@pytest.fixture
def network_if_data(monkeypatch):
    monkeypatch.setattr(psutil, "net_if_addrs", net_if_addrs)
    return configtool.get_network_if_data()


def test_get_network_if_data_default_false(network_if_data):
    for choice in network_if_data:
        assert not choice[2]

def test_get_network_if_data_strip_interface_ipv6(network_if_data):
    for choice in network_if_data:
        assert choice[0] not in choice[1]

def test_get_network_if_data(network_if_data):
    assert network_if_data[0][0] == "eth0"
    assert network_if_data[0][1] == "192.168.1.10"
    assert network_if_data[1][0] == "eth0"
    assert network_if_data[1][1] == "2001:0db8:ac10:fe01::"
    assert network_if_data[2][0] == "lo"
    assert network_if_data[2][1] == "127.0.0.1"
    assert network_if_data[3][0] == "lo"
    assert network_if_data[3][1] == "::1"
