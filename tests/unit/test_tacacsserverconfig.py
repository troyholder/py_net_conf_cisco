"""
Test suite for the tacacs server datamodels.
"""

import re
from ipaddress import IPv4Address

import pytest
import vars

from py_net_conf_cisco.tacacsserverconfig import (
    TacacsServerConfig,
)

server1 = IPv4Address("1.1.1.1")
server2 = IPv4Address("2.2.2.2")
encrpyted_string = "encrpyted_string"


class TestTacacsServerConfig:
    """Test class for the TacacsServerConfig dataclass."""

    failing_cases = [
        (
            {},
            TypeError,
            re.escape(
                "TacacsServerConfig.__init__() missing 2 required positional arguments: 'ip_address' and 'encrpyted_string'"
            ),
        ),
        (
            {
                "ip_address": server1,
            },
            TypeError,
            re.escape(
                "TacacsServerConfig.__init__() missing 1 required positional argument: 'encrpyted_string'"
            ),
        ),
        (
            {
                "encrpyted_string": encrpyted_string,
            },
            TypeError,
            re.escape(
                "TacacsServerConfig.__init__() missing 1 required positional argument: 'ip_address'"
            ),
        ),
        (
            {
                "ip_address": "1.1.1.1",
                "encrpyted_string": encrpyted_string,
            },
            TypeError,
            re.escape(
                "ip_address must be an IPv4Address or IPv6Address instance"
            ),
        ),
        (
            {
                "ip_address": server1,
                "encrpyted_string": 1234,
            },
            TypeError,
            re.escape("encrpyted_string must be a string"),
        ),
    ]

    @pytest.mark.parametrize("kwargs, exception_class, warning", failing_cases)
    def test_failing_creation(self, kwargs, exception_class, warning):
        """Test failing creations"""
        with pytest.raises(exception_class, match=warning):
            tacacs_server = TacacsServerConfig(**kwargs)  # ty: ignore[missing-argument]
            return tacacs_server

    working_cases = [
        (
            {
                "ip_address": vars.server_1_ipv4_address,
                "encrpyted_string": vars.encrpyted_string_1,
            },
            [
                f"tacacs-server host {vars.server_1_ipv4_address} key {vars.encrpyted_string_1}",
            ],
        ),
    ]

    @pytest.mark.parametrize("kwargs, expected_lines", working_cases)
    def test_working_creation(self, kwargs, expected_lines):
        assert TacacsServerConfig(**kwargs)

    @pytest.mark.parametrize("kwargs, expected_lines", working_cases)
    def test_working_creations_to_config_lines(self, kwargs, expected_lines):
        tacas_server = TacacsServerConfig(**kwargs)
        assert tacas_server.to_config_lines() == expected_lines
