from ipaddress import IPv4Address

import pytest
from test_ciscoconfig_interface import Interface, InterfaceType

from py_net_conf_cisco.tacacsgroupconfig import (
    TacacsServerGroupConfig,
    TacacsServerPrivateConfig,
)

# Objects for sample1.py
sample_server_1 = TacacsServerPrivateConfig(
    ip_address=IPv4Address("192.168.1.200"),
    key_mode=7,
    key="encrypted_string",
)

sample_server_2 = TacacsServerPrivateConfig(
    ip_address=IPv4Address("192.168.1.201"),
    key_mode=7,
    key="encrypted_string",
)
sample_group = TacacsServerGroupConfig(
    name="tacacs-servers",
    vrf="Mgmt-vrf",
    source_interface=Interface(
        interface_type=InterfaceType.GIGABITETHERNET,
        interface_number="0/0",
    ),
    server_private_list=[sample_server_1, sample_server_2],
)


# Objects for tests
test_group_1 = TacacsServerGroupConfig(
    name="test-group-1",
    vrf="Mgmt-vrf",
    source_interface=Interface(
        interface_type=InterfaceType.GIGABITETHERNET,
        interface_number="0/0",
    ),
    server_private_list=[sample_server_1, sample_server_2],
)
test_group_2 = TacacsServerGroupConfig(
    name="test-group-2",
    vrf="Blue",
    source_interface=Interface(
        interface_type=InterfaceType.TENGIGABITETHERNET,
        interface_number="0/1",
    ),
    server_private_list=[
        TacacsServerPrivateConfig(
            ip_address=IPv4Address("192.168.1.20"),
            key_mode=7,
            key="encrypted_string",
        ),
        TacacsServerPrivateConfig(
            ip_address=IPv4Address("192.168.1.21"),
            key_mode=7,
            key="encrypted_string",
        ),
    ],
)


class TestCiscoConfig:
    """
    Test class for the CiscoConfig module TACACS group config methods
    """

    get_tacacs_group_configs = [
        ("empty_config", []),
        (
            "config_from_file",
            [sample_group],
        ),
    ]

    @pytest.mark.parametrize(
        "config, tacacs_group_configs", get_tacacs_group_configs
    )
    def test_tacacs_group_property(
        self,
        config,
        tacacs_group_configs: list[TacacsServerGroupConfig],
        request,
    ):
        assert (
            request.getfixturevalue(config).tacacs_group == tacacs_group_configs
        )

    set_tacacs_server_server_configs = [
        (
            "empty_config",
            [
                test_group_1,
            ],
        ),
        (
            "config_from_file",
            [],
        ),
        (
            "config_from_file",
            [
                test_group_1,
            ],
        ),
        (
            "config_from_file",
            [
                test_group_1,
                test_group_2,
            ],
        ),
    ]

    @pytest.mark.parametrize(
        "config, tacacs_group_configs", set_tacacs_server_server_configs
    )
    def test_tacacs_group_setter(
        self,
        config,
        tacacs_group_configs: list[TacacsServerGroupConfig],
        request,
    ):
        config = request.getfixturevalue(config)
        config.tacacs_group = tacacs_group_configs
        assert config.tacacs_group == tacacs_group_configs
