from ipaddress import IPv4Address

import pytest

from py_net_conf_cisco.loggingconfig import LoggingConfig


class TestCiscoConfig:
    """
    Test class for the CiscoConfig module logging config methods
    """

    get_logging_server_configs = [
        ("empty_config", []),
        (
            "config_from_file",
            [
                LoggingConfig(
                    syslog_ip_address=IPv4Address("192.168.1.50"),
                ),
                LoggingConfig(
                    syslog_ip_address=IPv4Address("192.168.1.51"),
                    vrf="Blue",
                ),
            ],
        ),
    ]

    @pytest.mark.parametrize(
        "config, logging_configs", get_logging_server_configs
    )
    def test_logging_servers_property(
        self,
        config,
        logging_configs: list[LoggingConfig],
        request,
    ):
        assert (
            request.getfixturevalue(config).logging_servers == logging_configs
        )

    set_logging_server_configs = [
        (
            "empty_config",
            [
                LoggingConfig(
                    syslog_ip_address=IPv4Address("192.168.1.50"),
                ),
                LoggingConfig(
                    syslog_ip_address=IPv4Address("192.168.1.51"),
                    vrf="Blue",
                ),
            ],
        ),
        (
            "config_from_file",
            [],
        ),
        (
            "config_from_file",
            [
                LoggingConfig(
                    syslog_ip_address=IPv4Address("192.168.2.51"),
                    vrf="Blue",
                ),
            ],
        ),
        (
            "config_from_file",
            [
                LoggingConfig(
                    syslog_ip_address=IPv4Address("192.168.2.51"),
                    vrf="Blue",
                ),
                LoggingConfig(
                    syslog_ip_address=IPv4Address("192.168.2.52"),
                    vrf="Blue",
                ),
                LoggingConfig(
                    syslog_ip_address=IPv4Address("192.168.2.53"),
                    vrf="Blue",
                ),
            ],
        ),
    ]

    @pytest.mark.parametrize(
        "config, logging_configs", set_logging_server_configs
    )
    def test_logging_servers_setter(
        self,
        config,
        logging_configs: list[LoggingConfig],
        request,
    ):
        config = request.getfixturevalue(config)
        config.logging_servers = logging_configs
        assert config.logging_servers == logging_configs
