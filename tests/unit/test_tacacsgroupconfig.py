"""
Test suite for the tacacs server datamodels.
"""

import re

import pytest
import vars

from py_net_conf_cisco.interfaceconfig import Interface, InterfaceType
from py_net_conf_cisco.tacacsgroupconfig import (
    TacacsServerGroupConfig,
    TacacsServerPrivateConfig,
)

server_private_1 = TacacsServerPrivateConfig(
    ip_address=vars.server_1_ipv4_address,
    key_mode=0,
    key=vars.encrpyted_string_1,
)
server_private_2 = TacacsServerPrivateConfig(
    ip_address=vars.server_2_ipv4_address,
    key_mode=0,
    key=vars.encrpyted_string_2,
)


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
            tacas_server_group_config = TacacsServerGroupConfig(**kwargs)  # pyright: ignore # ty: ignore[missing-argument]
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
        tacas_server_group_config = TacacsServerGroupConfig(**kwargs)  # ty: ignore[missing-argument]
        assert tacas_server_group_config.name == kwargs["name"]
        assert tacas_server_group_config.vrf == kwargs.get("vrf")
        assert tacas_server_group_config.source_interface == kwargs.get(
            "source_interface"
        )

    @pytest.mark.parametrize("kwargs, expected_lines", working_cases)
    def test_working_creations_to_config_lines(self, kwargs, expected_lines):
        tacas_server_group_config = TacacsServerGroupConfig(**kwargs)  # ty: ignore[missing-argument]
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
                "ip_address": vars.server_1_ipv4_address,
                "fqdn": "foo.bar",
            },
            re.escape("must not set ip_address and fqdn"),
        ),
        (
            {
                "ip_address": vars.server_1_ipv4_address,
                "key_mode": 1,
            },
            re.escape("key_mode must be 0, 6, 7, or None"),
        ),
        (
            {
                "ip_address": vars.server_1_ipv4_address,
                "key_mode": "1",
            },
            re.escape("key_mode must be 0, 6, 7, or None"),
        ),
        (
            {"ip_address": vars.server_1_ipv4_address, "key_mode": 0, "key": 9},
            re.escape("key must be a string that does not start with a space"),
        ),
        (
            {
                "ip_address": vars.server_1_ipv4_address,
                "key_mode": 0,
                "key": " foo",
            },
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
                "ip_address": vars.server_1_ipv4_address,
            },
            [f" server-private {str(vars.server_1_ipv4_address)}"],
        ),
        (
            {
                "fqdn": "foo.bar",
            },
            [" server-private fqdn foo.bar"],
        ),
        (
            {
                "ip_address": vars.server_1_ipv4_address,
            },
            [f" server-private {str(vars.server_1_ipv4_address)}"],
        ),
        (
            {
                "ip_address": vars.server_1_ipv4_address,
                "key": vars.encrpyted_string_1,
            },
            [
                f" server-private {str(vars.server_1_ipv4_address)} {vars.encrpyted_string_1}"
            ],
        ),
        (
            {
                "ip_address": vars.server_1_ipv4_address,
                "key_mode": 0,
                "key": vars.encrpyted_string_1,
            },
            [
                f" server-private {str(vars.server_1_ipv4_address)} 0 {vars.encrpyted_string_1}"
            ],
        ),
        (
            {
                "ip_address": vars.server_1_ipv4_address,
                "key": vars.encrpyted_string_1,
            },
            [
                f" server-private {str(vars.server_1_ipv4_address)} {vars.encrpyted_string_1}"
            ],
        ),
        (
            {
                "ip_address": vars.server_1_ipv4_address,
                "key_mode": 6,
                "key": vars.encrpyted_string_1,
            },
            [
                f" server-private {str(vars.server_1_ipv4_address)} 6 {vars.encrpyted_string_1}"
            ],
        ),
        (
            {
                "ip_address": vars.server_1_ipv4_address,
                "key_mode": 7,
                "key": vars.encrpyted_string_1,
            },
            [
                f" server-private {str(vars.server_1_ipv4_address)} 7 {vars.encrpyted_string_1}"
            ],
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
