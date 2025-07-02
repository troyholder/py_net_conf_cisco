"""
Test suite for the tacacs server datamodels.
"""

import re
from ipaddress import IPv4Address

import pytest

from py_net_conf_cisco.tacacs_server_datamodel import TacacsServerConfig

server1 = IPv4Address("1.1.1.1")
server2 = IPv4Address("2.2.2.2")
encrpyted_string = "encrpyted_string"


class TestTacacsServerConfig:
    """Test class for the TacacsServerConfig dataclass."""

    failing_cases = [
        (
            {},
            re.escape(
                "TacacsServerConfig.__init__() missing 2 required positional arguments: 'ip_address' and 'encrpyted_string'"
            ),
        ),
        (
            {
                "ip_address": server1,
            },
            re.escape(
                "TacacsServerConfig.__init__() missing 1 required positional argument: 'encrpyted_string'"
            ),
        ),
        (
            {
                "encrpyted_string": encrpyted_string,
            },
            re.escape(
                "TacacsServerConfig.__init__() missing 1 required positional argument: 'ip_address'"
            ),
        ),
        (
            {
                "ip_address": "1.1.1.1",
                "encrpyted_string": encrpyted_string,
            },
            re.escape(
                "ip_address must be an IPv4Address or IPv6Address instance"
            ),
        ),
        (
            {
                "ip_address": server1,
                "encrpyted_string": 1234,
            },
            re.escape("encrpyted_string must be a string"),
        ),
    ]

    @pytest.mark.parametrize("kwargs, warning", failing_cases)
    def test_failing_creation(self, kwargs, warning):
        """Test a failing creation"""
        with pytest.raises(TypeError, match=warning):
            interface = TacacsServerConfig(**kwargs)  # pyright: ignore
            return interface

    def test_working_createion(self):
        tacas_server = TacacsServerConfig(
            ip_address=server1, encrpyted_string=encrpyted_string
        )
        assert tacas_server.ip_address == server1
        assert tacas_server.encrpyted_string == encrpyted_string
