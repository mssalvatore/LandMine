from landmine.configuration.network_interface import NetworkInterface
import pytest
import socket
import validate

def test_IPv4_address_family():
    ni = NetworkInterface("eth0", "IPv4")
    ni.validate()

def test_IPv6_address_family():
    ni = NetworkInterface("eth0", "IPv6")
    ni.validate()

def test_invalid_address_family():
    invalid_addr_family = "IPv5"
    with pytest.raises(validate.VdtValueError):
        NetworkInterface("eth0",invalid_addr_family)

    ni = NetworkInterface("eth0", "IPv4")
    ni.address_family = invalid_addr_family
    with pytest.raises(validate.VdtValueError):
        ni.validate()

def test_invalid_interface_newline():
    invalid_interface = "eth0\naaaa"
    with pytest.raises(validate.VdtValueError):
        NetworkInterface(invalid_interface, "IPv6")

    ni = NetworkInterface("eth0", "IPv6")
    ni.interface = invalid_interface
    with pytest.raises(validate.VdtValueError):
        ni.validate()

def test_invalid_interface_space():
    with pytest.raises(validate.VdtValueError):
        NetworkInterface("eth0 aaaa", "IPv6")

def test_invalid_interface_tab():
    with pytest.raises(validate.VdtValueError):
        NetworkInterface("eth0\taaaa", "IPv6")

def test_invalid_interface_unicode():
    with pytest.raises(validate.VdtValueError):
        NetworkInterface("eth0\u000Daaaa", "IPv6")
    with pytest.raises(validate.VdtValueError):
        NetworkInterface("eth0\u000Aaaaa", "IPv6")
    with pytest.raises(validate.VdtValueError):
        NetworkInterface("eth0\u00A0aaaa", "IPv6")

def test_invalid_interface_restricted_characters():
    with pytest.raises(validate.VdtValueError):
        NetworkInterface("eth0[", "IPv6")
    with pytest.raises(validate.VdtValueError):
        NetworkInterface("eth0]", "IPv6")
    with pytest.raises(validate.VdtValueError):
        NetworkInterface("eth0!", "IPv6")
    with pytest.raises(validate.VdtValueError):
        NetworkInterface("eth0/", "IPv6")
    with pytest.raises(validate.VdtValueError):
        NetworkInterface("eth0,", "IPv6")

def test_from_config_str_IPv4():
    ni = NetworkInterface.from_config_str("enp2s1:IPv4")
    assert ni.interface == "enp2s1"
    assert ni.address_family == "IPv4"

def test_from_config_str_IPv6():
    ni = NetworkInterface.from_config_str("enp2s1:IPv6")
    assert ni.interface == "enp2s1"
    assert ni.address_family == "IPv6"

def test_from_config_str_invalid_ip():
    with pytest.raises(validate.VdtValueError):
        NetworkInterface.from_config_str("enp2s1:invalid")

def test_str():
    ni = NetworkInterface("eth0", "IPv4")
    assert str(ni) == "eth0:IPv4"

