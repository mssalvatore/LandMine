import re

class SnortAlert:
    _rule_id_regex = re.compile(r"\[\d+:(\d+):\d+\]")
    _msg_regex = re.compile(r"\[\*\*\] \[.*\] (.*) \[\*\*\]")

    def __init__(self, alert_lines):
        #TODO: Add more validation to check that snort alert is valid
        self._timestamp = SnortAlert.parse_timestamp(alert_lines)
        self._rule_id = SnortAlert.parse_rule_id(alert_lines)
        self._alert_msg = SnortAlert.parse_alert_msg(alert_lines)
        self._protocol = SnortAlert.parse_protocol(alert_lines)
        self._packet_header_info = SnortAlert.parse_packet_ip_port_direction(alert_lines)

    @staticmethod
    def parse_rule_id(alert_lines):
        matches = SnortAlert._rule_id_regex.search(alert_lines[0]);
        if matches:
            return matches.group(1)

        raise Exception("Error parsing rule ID from snort alert")

    @staticmethod
    def parse_alert_msg(alert_lines):
        matches = SnortAlert._msg_regex.search(alert_lines[0]);
        if matches:
            return matches.group(1)

        raise Exception("Error parsing message from snort alert")

    @staticmethod
    def parse_timestamp(alert_lines):
        timestamp = alert_lines[2].split(' ')[0]

        if not timestamp:
            raise Exception("Error parsing procol from snort alert")

        return timestamp

    @staticmethod
    def parse_packet_ip_port_direction(alert_lines):
        split_line = alert_lines[2].split(' ');
        if len(split_line) != 4:
            raise Exception("Error parsing IP/Port from snort alert")

        src = split_line[1]
        direction = split_line[2]
        destination = split_line[3]
        return src + " " + direction + " " + destination;

    @staticmethod
    def parse_protocol(alert_lines):
        protocol = alert_lines[3].split(' ')[0];

        if not protocol:
            raise Exception("Error parsing procol from snort alert")

        return protocol

    @property
    def timestamp(self):
        return self._timestamp

    @property
    def rule_id(self):
        return self._rule_id

    @property
    def alert_msg(self):
        return self._alert_msg

    @property
    def protocol(self):
        return self._protocol

    @property
    def packet_header_info(self):
        return self._packet_header_info
