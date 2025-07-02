"""
Test suite for the tacacs server datamodels.
"""

import re
from ipaddress import IPv4Address

import pytest

from py_net_conf_cisco.tacacs_server_datamodel import (
    TacacsServerConfig,
    TacacsServerGroupConfig,
)

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
        """Test failing creations"""
        with pytest.raises(TypeError, match=warning):
            interface = TacacsServerConfig(**kwargs)  # pyright: ignore
            return interface

    def test_working_createion(self):
        tacas_server = TacacsServerConfig(
            ip_address=server1, encrpyted_string=encrpyted_string
        )
        assert tacas_server.ip_address == server1
        assert tacas_server.encrpyted_string == encrpyted_string


class TestTacacsServerGroupConfig:
    failing_cases = [
        (
            {},
            re.escape(
                "TacacsServerGroupConfig.__init__() missing 2 required positional arguments: 'group_name' and 'servers'"
            ),
        ),
        (
            {
                "group_name": "tacas_group",
            },
            re.escape(
                "TacacsServerGroupConfig.__init__() missing 1 required positional argument: 'servers'"
            ),
        ),
        (
            {
                "servers": [],
            },
            re.escape(
                "TacacsServerGroupConfig.__init__() missing 1 required positional argument: 'group_name'"
            ),
        ),
        (
            {
                "group_name": "tacas_group",
                "servers": [],
            },
            re.escape("servers must be a non-empty list"),
        ),
        (
            {
                "group_name": "tacas_group",
                "servers": ["1.1.1.1"],
            },
            re.escape(
                "server at 0 of servers is not a TacacsServerGroupConfig"
            ),
        ),
        (
            {
                "group_name": "tacas_group",
                "servers": [
                    TacacsServerConfig(server1, encrpyted_string),
                    "1.1.1.1",
                ],
            },
            re.escape(
                "server at 1 of servers is not a TacacsServerGroupConfig"
            ),
        ),
        (
            {
                "group_name": "tacas_group",
                "servers": [
                    TacacsServerConfig(server1, encrpyted_string),
                    TacacsServerConfig(server1, encrpyted_string),
                ],
            },
            re.escape("duplicate servers in servers list: 1.1.1.1"),
        ),
        (
            {
                "group_name": "tacas_group",
                "servers": [
                    TacacsServerConfig(server1, encrpyted_string),
                    TacacsServerConfig(server1, encrpyted_string),
                    TacacsServerConfig(server2, encrpyted_string),
                    TacacsServerConfig(server2, encrpyted_string),
                ],
            },
            re.escape("duplicate servers in servers list: 1.1.1.1, 2.2.2.2"),
        ),
    ]

    @pytest.mark.parametrize("kwargs, warning", failing_cases)
    def test_failing_creations(self, kwargs, warning):
        """Test failing creations"""
        with pytest.raises(TypeError, match=warning):
            interface = TacacsServerGroupConfig(**kwargs)  # pyright: ignore
            return interface

    working_cases = [
        (  # Minimum requirements
            {
                "group_name": "tacas_group",
                "servers": [
                    TacacsServerConfig(server1, encrpyted_string),
                ],
            },
            [],
        ),
        (  # Multiple servers
            {
                "group_name": "tacas_group",
                "servers": [
                    TacacsServerConfig(server1, encrpyted_string),
                    TacacsServerConfig(server2, encrpyted_string),
                ],
            },
            [],
        ),
        (  # Multiple servers with vrf
            {
                "group_name": "tacas_group",
                "servers": [
                    TacacsServerConfig(server1, encrpyted_string),
                    TacacsServerConfig(server2, encrpyted_string),
                ],
                "vrf": "mgmt",
            },
            [],
        ),
        (  # Multiple servers with interface
            {
                "group_name": "tacas_group",
                "servers": [
                    TacacsServerConfig(server1, encrpyted_string),
                    TacacsServerConfig(server2, encrpyted_string),
                ],
                "interface": "GigabitEthernet1",
            },
            [],
        ),
        (  # Multiple servers with vrf and interface
            {
                "group_name": "tacas_group",
                "servers": [
                    TacacsServerConfig(server1, encrpyted_string),
                    TacacsServerConfig(server2, encrpyted_string),
                ],
                "vrf": "mgmt",
                "interface": "GigabitEthernet1",
            },
            [],
        ),
    ]

    @pytest.mark.parametrize("kwargs, expected_lines", working_cases)
    def test_working_creations(self, kwargs, expected_lines):
        pass
