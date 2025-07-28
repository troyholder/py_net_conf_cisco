"""
Test suite for the tacacs server datamodels.
"""

import re
from ipaddress import IPv4Address

import pytest

from py_net_conf_cisco.interface_datamodel import Interface, InterfaceType
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
                "TacacsServerGroupConfig.__init__() missing 1 required positional argument: 'name'"
            ),
        ),
    ]

    @pytest.mark.parametrize("kwargs, warning", failing_cases)
    def test_failing_creations(self, kwargs, warning):
        """Test failing creations"""
        with pytest.raises(TypeError, match=warning):
            tacas_server_group_config = TacacsServerGroupConfig(**kwargs)  # pyright: ignore
            return tacas_server_group_config

    working_cases = [
        (  # Minimum requirements
            {
                "name": "tacas_group",
            },
            [
                "aaa group server tacacs+ tacas_group",
            ],
        ),
        (
            {
                "name": "tacas_group",
                "vrf": "Mgmt-vrf",
            },
            [
                "aaa group server tacacs+ tacas_group",
                " ip vrf forwarding Mgmt-vrf",
            ],
        ),
        (
            {
                "name": "tacas_group",
                "vrf": "Mgmt-vrf",
                "source_interface": Interface(
                    InterfaceType.GIGABITETHERNET, "0/0"
                ),
            },
            [
                "aaa group server tacacs+ tacas_group",
                " ip vrf forwarding Mgmt-vrf",
                " ip tacacs source-interface GigabitEthernet0/0",
            ],
        ),
    ]

    @pytest.mark.parametrize("kwargs, expected_lines", working_cases)
    def test_working_creations(self, kwargs, expected_lines):
        tacas_server_group_config = TacacsServerGroupConfig(**kwargs)
        assert tacas_server_group_config.name == kwargs["name"]
        assert tacas_server_group_config.vrf == kwargs.get("vrf")
        assert tacas_server_group_config.source_interface == kwargs.get(
            "source_interface"
        )

    @pytest.mark.parametrize("kwargs, expected_lines", working_cases)
    def test_working_creations_to_config_lines(self, kwargs, expected_lines):
        tacas_server_group_config = TacacsServerGroupConfig(**kwargs)
        assert tacas_server_group_config.to_config_lines() == expected_lines
