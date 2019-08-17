import re
from validate import VdtValueError

NETWORK_INTERFACE_REGEX = r"(.+):(IPv4|IPv6)"

class NetworkInterface:
    def __init__(self, interface, address_family):
        NetworkInterface._validate(interface, address_family)

        self.interface = interface
        self.address_family = address_family

    def validate(self):
        NetworkInterface._validate(self.interface, self.address_family)

    def __str__(self):
        return ":".join((self.interface, self.address_family))

    @staticmethod
    def from_config_str(config_str):
        interface, address_family = NetworkInterface._parse(config_str)
        return NetworkInterface(interface, address_family)

    @staticmethod
    def _parse(config_str):
        match = re.match(NETWORK_INTERFACE_REGEX, config_str)
        if not match:
            raise VdtValueError(config_str)

        interface = match.group(1)
        address_family = match.group(2)

        return interface, address_family

    @staticmethod
    def _validate(interface, address_family):
        for char in interface:
            if char.isspace() or char in "[]!/,":
                raise VdtValueError(":".join([interface, address_family]))
        if (address_family != "IPv4") and (address_family != "IPv6"): 
            raise VdtValueError(":".join([interface, address_family]))
