from ipaddress import IPv4Address

import pytest

from py_net_conf_cisco.tacacsserverconfig import TacacsServerConfig

# Objects for sample1.py
sample_server_1_ipaddress = IPv4Address("192.168.1.200")
sample_server_1_secret = "tacacs_secret"
sample_server_2_ipaddress = IPv4Address("192.168.1.201")
sample_server_2_secret = "tacacs_secret"
sample_server_1 = TacacsServerConfig(
    ip_address=sample_server_1_ipaddress,
    encrpyted_string=sample_server_1_secret,
)

sample_server_2 = TacacsServerConfig(
    ip_address=sample_server_2_ipaddress,
    encrpyted_string=sample_server_2_secret,
)


# Objects for tests
test_server_1_ipaddress = IPv4Address("10.0.0.1")
test_server_1_secret = "test_tacacs_secret"
test_server_2_ipaddress = IPv4Address("10.0.0.2")
test_server_2_secret = "test_tacacs_secret"
test_server_3_ipaddress = IPv4Address("10.0.0.3")
test_server_3_secret = "test_tacacs_secret"
test_server_1 = TacacsServerConfig(
    ip_address=test_server_1_ipaddress,
    encrpyted_string=test_server_1_secret,
)
test_server_2 = TacacsServerConfig(
    ip_address=test_server_2_ipaddress,
    encrpyted_string=test_server_2_secret,
)
test_server_3 = TacacsServerConfig(
    ip_address=test_server_3_ipaddress,
    encrpyted_string=test_server_3_secret,
)


class TestCiscoConfig:
    """
    Test class for the CiscoConfig module TACACS server config methods
    """

    get_tacacs_server_configs = [
        ("empty_config", []),
        (
            "config_from_file",
            [
                sample_server_1,
                sample_server_2,
            ],
        ),
    ]

    @pytest.mark.parametrize(
        "config, tacacs_server_configs", get_tacacs_server_configs
    )
    def test_tacacs_servers_property(
        self,
        config,
        tacacs_server_configs: list[TacacsServerConfig],
        request,
    ):
        assert (
            request.getfixturevalue(config).tacacs_server_servers
            == tacacs_server_configs
        )

    set_tacacs_server_server_configs = [
        (
            "empty_config",
            [
                test_server_1,
                test_server_2,
            ],
        ),
        (
            "config_from_file",
            [],
        ),
        (
            "config_from_file",
            [
                test_server_1,
            ],
        ),
        (
            "config_from_file",
            [
                test_server_1,
                test_server_2,
                test_server_2,
            ],
        ),
    ]

    @pytest.mark.parametrize(
        "config, tacacs_server_configs", set_tacacs_server_server_configs
    )
    def test_tacacs_server_servers_setter(
        self,
        config,
        tacacs_server_configs: list[TacacsServerConfig],
        request,
    ):
        config = request.getfixturevalue(config)
        config.tacacs_server_servers = tacacs_server_configs
        assert config.tacacs_server_servers == tacacs_server_configs
