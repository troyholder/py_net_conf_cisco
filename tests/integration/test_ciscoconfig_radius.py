from ipaddress import IPv4Address

import pytest

from py_net_conf_cisco import CiscoConfig
from py_net_conf_cisco.radiusserverconfig import RadiusServerConfig


class TestCiscoConfig:
    """
    Test class for the CiscoConfig module radius config methods
    """

    def test_radius_servers_property_empty_config(
        self, empty_config: CiscoConfig
    ):
        assert empty_config.radius_servers == []

    def test_radius_servers_property_config_from_file(
        self, config_from_file: CiscoConfig
    ):
        assert config_from_file.radius_servers == [
            RadiusServerConfig(
                ip_address=IPv4Address("192.168.1.100"),
                name="radius00",
                key="encrypted_string",
            ),
            RadiusServerConfig(
                ip_address=IPv4Address("192.168.1.101"),
                name="radius01",
                key="encrypted_string",
            ),
        ]

    def test_last_config_line_empty_config(self, empty_config: CiscoConfig):
        last_config_line = empty_config.last_config_line
        assert last_config_line.text == "!"
        assert last_config_line.index == 0

    def test__last_config_line_config_from_file(
        self, config_from_file: CiscoConfig
    ):
        last_config_line = config_from_file.last_config_line
        assert last_config_line.text == "end"
        assert last_config_line.index == 107

    @pytest.mark.parametrize(
        "radius_servers",
        [
            [],
            [
                RadiusServerConfig(
                    ip_address=IPv4Address("192.168.1.100"),
                    name="radius10",
                    key="encrypted_string",
                ),
                RadiusServerConfig(
                    ip_address=IPv4Address("192.168.1.101"),
                    name="radius11",
                    key="encrypted_string",
                ),
            ],
        ],
    )
    def test_changing_radius_server_when_there_are_none(
        self,
        empty_config: CiscoConfig,
        radius_servers: list[RadiusServerConfig],
    ):
        empty_config.radius_servers = radius_servers
        assert empty_config.radius_servers == radius_servers

    @pytest.mark.parametrize(
        "radius_servers",
        [
            # Remove all servers
            [],
            # Same number of servers
            [
                RadiusServerConfig(
                    ip_address=IPv4Address("192.168.1.200"),
                    name="radius20",
                    key="encrypted_string",
                ),
                RadiusServerConfig(
                    ip_address=IPv4Address("192.168.1.201"),
                    name="radius21",
                    key="encrypted_string",
                ),
            ],
            # Less servers
            [
                RadiusServerConfig(
                    ip_address=IPv4Address("192.168.1.200"),
                    name="radius20",
                    key="encrypted_string",
                ),
                RadiusServerConfig(
                    ip_address=IPv4Address("192.168.1.201"),
                    name="radius21",
                    key="encrypted_string",
                ),
            ],
            # More servers
            [
                RadiusServerConfig(
                    ip_address=IPv4Address("192.168.1.200"),
                    name="radius20",
                    key="encrypted_string",
                ),
                RadiusServerConfig(
                    ip_address=IPv4Address("192.168.1.201"),
                    name="radius21",
                    key="encrypted_string",
                ),
                RadiusServerConfig(
                    ip_address=IPv4Address("192.168.1.202"),
                    name="radius22",
                    key="encrypted_string",
                ),
            ],
        ],
    )
    def test_changing_radius_server_when_there_are_some(
        self,
        config_from_file: CiscoConfig,
        radius_servers: list[RadiusServerConfig],
    ):
        config_from_file.radius_servers = radius_servers
        assert config_from_file.radius_servers == radius_servers
