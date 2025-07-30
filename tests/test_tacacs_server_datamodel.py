"""
Test suite for the tacacs server datamodels.
"""

import re
from ipaddress import IPv4Address

import pytest

from py_net_conf_cisco.interface_datamodel import Interface, InterfaceType
from py_net_conf_cisco.tacacsserverconfig import (
    TacacsServerConfig,
    TacacsServerGroupConfig,
    TacacsServerPrivateConfig,
)

server1 = IPv4Address("1.1.1.1")
server2 = IPv4Address("2.2.2.2")
encrpyted_string = "encrpyted_string"
server_private_1 = TacacsServerPrivateConfig(
    ip_address=server1, key_mode=0, key=encrpyted_string
)
server_private_2 = TacacsServerPrivateConfig(
    ip_address=server2, key_mode=0, key=encrpyted_string
)


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


# aaa group server tacacs+ tacacs-servers
# server-private 1.1.1.1 key 7 REDACT
# server-private 2.2.2.2 key 7 REDACT
# ip vrf forwarding Mgmt-vrf
# ip tacacs source-interface GigabitEthernet0/0
#
class TestTacacsServerGroupConfig:
    failing_cases = [
        (
            {},
            re.escape(
                "TacacsServerGroupConfig.__init__() missing 1 required positional argument: 'name'"
            ),
        ),
        (
            {
                "name": 1,
            },
            re.escape("name must be a string"),
        ),
        (
            {
                "name": "foo",
                "vrf": 9,
            },
            re.escape("vrf must be a string"),
        ),
        (
            {
                "name": "foo",
                "source_interface": 9,
            },
            re.escape("source_interface must be an Interface"),
        ),
        (
            {
                "name": "foo",
                "server_private_list": 9,
            },
            re.escape(
                "server_private_list must either be an empty list or list "
                + "of TacacsServerPrivateConfig objects"
            ),
        ),
        (
            {
                "name": "foo",
                "server_private_list": [9],
            },
            re.escape(
                "server_private_list must either be an empty list or list "
                + "of TacacsServerPrivateConfig objects"
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
        (
            {
                "name": "tacas_group",
                "vrf": "Mgmt-vrf",
                "server_private_list": [],
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
        (
            {
                "name": "tacas_group",
                "vrf": "Mgmt-vrf",
                "server_private_list": [server_private_1],
                "source_interface": Interface(
                    InterfaceType.GIGABITETHERNET, "0/0"
                ),
            },
            [
                "aaa group server tacacs+ tacas_group",
                server_private_1.to_config_lines()[0],
                " ip vrf forwarding Mgmt-vrf",
                " ip tacacs source-interface GigabitEthernet0/0",
            ],
        ),
        (
            {
                "name": "tacas_group",
                "vrf": "Mgmt-vrf",
                "server_private_list": [server_private_1, server_private_2],
                "source_interface": Interface(
                    InterfaceType.GIGABITETHERNET, "0/0"
                ),
            },
            [
                "aaa group server tacacs+ tacas_group",
                server_private_1.to_config_lines()[0],
                server_private_2.to_config_lines()[0],
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


class TestTacacsServerPrivateConfig:
    failing_cases = [
        (
            {},
            re.escape("ip_address or fqdn must be given"),
        ),
        (
            {
                "ip_address": "foo",
            },
            re.escape(
                "ip_address must be an IPv4Address or IPv6Address instance"
            ),
        ),
        (
            {
                "fqdn": 1,
            },
            re.escape("fqdn must be a string"),
        ),
        (
            {
                "ip_address": server1,
                "fqdn": "foo.bar",
            },
            re.escape("must not set ip_address and fqdn"),
        ),
        (
            {
                "ip_address": server1,
                "key_mode": 1,
            },
            re.escape("key_mode must be 0, 6, 7, or None"),
        ),
        (
            {
                "ip_address": server1,
                "key_mode": "1",
            },
            re.escape("key_mode must be 0, 6, 7, or None"),
        ),
        (
            {"ip_address": server1, "key_mode": 0, "key": 9},
            re.escape("key must be a string that does not start with a space"),
        ),
        (
            {"ip_address": server1, "key_mode": 0, "key": " foo"},
            re.escape(
                "key must not start with spaces to avoid possible issues"
            ),
        ),
    ]

    @pytest.mark.parametrize("kwargs, warning", failing_cases)
    def test_failing_creations(self, kwargs, warning):
        """Test failing creations"""
        with pytest.raises(TypeError, match=warning):
            tacas_server_private_config = TacacsServerPrivateConfig(**kwargs)  # pyright: ignore
            return tacas_server_private_config

    working_cases = [
        (
            {
                "ip_address": server1,
            },
            [f" server-private {str(server1)}"],
        ),
        (
            {
                "fqdn": "foo.bar",
            },
            [" server-private fqdn foo.bar"],
        ),
        (
            {
                "ip_address": server1,
            },
            [f" server-private {str(server1)}"],
        ),
        (
            {"ip_address": server1, "key": encrpyted_string},
            [f" server-private {str(server1)} {encrpyted_string}"],
        ),
        (
            {"ip_address": server1, "key_mode": 0, "key": encrpyted_string},
            [f" server-private {str(server1)} 0 {encrpyted_string}"],
        ),
        (
            {"ip_address": server1, "key": encrpyted_string},
            [f" server-private {str(server1)} {encrpyted_string}"],
        ),
        (
            {"ip_address": server1, "key_mode": 6, "key": encrpyted_string},
            [f" server-private {str(server1)} 6 {encrpyted_string}"],
        ),
        (
            {"ip_address": server1, "key_mode": 7, "key": encrpyted_string},
            [f" server-private {str(server1)} 7 {encrpyted_string}"],
        ),
    ]

    @pytest.mark.parametrize("kwargs, config_lines", working_cases)
    def test_working_cases(self, kwargs, config_lines):
        tacas_server_private_config = TacacsServerPrivateConfig(**kwargs)
        assert tacas_server_private_config

    @pytest.mark.parametrize("kwargs, config_lines", working_cases)
    def test_working_cases_to_config_lines(self, kwargs, config_lines):
        tacas_server_private_config = TacacsServerPrivateConfig(**kwargs)
        assert tacas_server_private_config.to_config_lines() == config_lines
