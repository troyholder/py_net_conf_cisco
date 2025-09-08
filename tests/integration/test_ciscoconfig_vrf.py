import pytest

from py_net_conf_cisco.vrfconfig import VRFConfig

# Objects for sample1.py
sample_vrf_1 = VRFConfig(
    name="Blue",
    rd="rd 65500:0",
)

# Objects for tests
test_vrf_1 = VRFConfig(
    name="Red",
    rd="rd 65511:10",
)
test_vrf_2 = VRFConfig(
    name="Green",
)


class TestCiscoConfig:
    """
    Test class for the CiscoConfig module logging vrf methods
    """

    get_vrf_configs = [
        ("empty_config", []),
        (
            "config_from_file",
            [
                test_vrf_1,
            ],
        ),
    ]

    @pytest.mark.parametrize("config, vrf_configs", get_vrf_configs)
    def test_vrfs_property(
        self,
        config,
        vrf_configs: list[VRFConfig],
        request,
    ):
        assert request.getfixturevalue(config).vrfs == vrf_configs

    set_vrf_configs = [
        (
            "empty_config",
            [
                test_vrf_1,
                test_vrf_2,
            ],
        ),
        (
            "config_from_file",
            [],
        ),
        (
            "config_from_file",
            [
                test_vrf_1,
            ],
        ),
        (
            "config_from_file",
            [
                test_vrf_1,
                test_vrf_2,
            ],
        ),
    ]

    @pytest.mark.parametrize("config, vrf_configs", set_vrf_configs)
    def test_vrf_setter(
        self,
        config,
        vrf_configs: list[VRFConfig],
        request,
    ):
        config = request.getfixturevalue(config)
        config.vrfs = vrf_configs
        assert config.vrfs == vrf_configs
