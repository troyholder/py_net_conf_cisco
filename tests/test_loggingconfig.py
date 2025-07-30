import re
from ipaddress import IPv4Address, IPv6Address

import pytest

from py_net_conf_cisco.loggingconfig import LoggingConfig

server_1_ipv4_address = IPv4Address("192.168.1.1")
server_1_ipv6_address = IPv6Address("2001:db8::1")
server_2_ipv4_address = IPv4Address("192.168.2.1")
server_2_ipv6_address = IPv6Address("2001:db8::2")


class TestLoggingConfig:
    """Test class for the LoggingConfig dataclass."""

    failing_cases = [
        (
            {},
            TypeError,
            re.escape(
                "At least one of syslog_ip_address or syslog_fqdn must be set."
            ),
        ),
        (
            {
                "syslog_ip_address": 1,
            },
            TypeError,
            re.escape(
                "syslog_ip_address must be an IPv4Address or IPv6Address."
            ),
        ),
        (
            {
                "syslog_fqdn": 1,
            },
            TypeError,
            re.escape("syslog_fqdn must be a string."),
        ),
        (
            {
                "syslog_ip_address": server_1_ipv4_address,
                "syslog_fqdn": "foo.bar",
            },
            ValueError,
            re.escape(
                "Only one of syslog_ip_address or syslog_fqdn can be set."
            ),
        ),
        (
            {
                "syslog_ip_address": server_1_ipv4_address,
                "vrf": 9,
            },
            TypeError,
            re.escape("vrf must be a string."),
        ),
    ]

    @pytest.mark.parametrize("kwargs, exception_class, warning", failing_cases)
    def test_failing_creation(self, kwargs, exception_class, warning):
        """Test failing creations"""
        with pytest.raises(exception_class, match=warning):
            logging_server = LoggingConfig(**kwargs)  # pyright: ignore
            return logging_server

    working_cases = [
        (
            {
                "syslog_ip_address": server_1_ipv4_address,
            },
            [f"logging host {server_1_ipv4_address}"],
        ),
        (
            {
                "syslog_fqdn": "foobar",
            },
            ["logging host fqdn foobar"],
        ),
        (
            {
                "syslog_ip_address": server_1_ipv4_address,
                "vrf": "blue",
            },
            [f"logging host {server_1_ipv4_address} vrf blue"],
        ),
    ]

    @pytest.mark.parametrize("kwargs, expected_lines", working_cases)
    def test_working_creations(self, kwargs, expected_lines):
        assert LoggingConfig(**kwargs)

    @pytest.mark.parametrize("kwargs, expected_lines", working_cases)
    def test_working_creations_to_config_lines(self, kwargs, expected_lines):
        logging_server = LoggingConfig(**kwargs)
        assert logging_server.to_config_lines() == expected_lines
