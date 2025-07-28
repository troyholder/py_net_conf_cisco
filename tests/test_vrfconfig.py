"""
Test suite for the VRF datamodels.
"""

import pytest

from py_net_conf_cisco.vrfconfig import VRFConfig


class TestVRFConfig:
    """Test class for the VRFConfig dataclass."""

    failing_cases = [
        ({}),
        (
            {
                "rd": "65500:00",
            }
        ),
    ]

    @pytest.mark.parametrize("kwargs", failing_cases)
    def test_vrf_config_failing_cases(self, kwargs):
        """Test VRFConfig instantiation with no name fails"""
        with pytest.raises(Exception):
            vrf = VRFConfig(**kwargs)
            return vrf

    working_cases = [
        (
            {
                "name": "foo",
            },
            [
                "vrf definition foo",
            ],
        ),
        (
            {
                "name": "foo",
                "rd": "65500:00",
            },
            ["vrf definition foo", " rd 65500:00"],
        ),
        (
            {
                "name": "foo",
                "rd": "65500:00",
                "address_family_ipv4_exports": ["65500:11", "65500:22"],
            },
            [
                "vrf definition foo",
                " rd 65500:00",
                " !",
                " address-family ipv4",
                "  route-target export 65500:11",
                "  route-target export 65500:22",
                " exit-address-family",
            ],
        ),
        (
            {
                "name": "foo",
                "rd": "65500:00",
                "address_family_ipv4_imports": ["65500:11", "65500:22"],
            },
            [
                "vrf definition foo",
                " rd 65500:00",
                " !",
                " address-family ipv4",
                "  route-target import 65500:11",
                "  route-target import 65500:22",
                " exit-address-family",
            ],
        ),
        (
            {
                "name": "foo",
                "rd": "65500:00",
                "address_family_ipv4_exports": ["65500:11", "65500:22"],
                "address_family_ipv4_imports": ["65500:11", "65500:22"],
            },
            [
                "vrf definition foo",
                " rd 65500:00",
                " !",
                " address-family ipv4",
                "  route-target export 65500:11",
                "  route-target export 65500:22",
                "  route-target import 65500:11",
                "  route-target import 65500:22",
                " exit-address-family",
            ],
        ),
    ]

    @pytest.mark.parametrize("kwargs, config_lines", working_cases)
    def test_vrf_config_working_cases(self, kwargs, config_lines):
        """Test VRFConfig instantiation"""
        vrf = VRFConfig(**kwargs)

        assert vrf.to_config_lines() == config_lines

    failing_from_config_lines_cases = [
        (
            [
                "vrf definition Blue",
                " rd 65500:0",
                " !",
                " address-family ipv4",
                "  route-target export 65500:0",
                "  route-target import 65500:0",
                " exit-address-family",
                "vrf definition Red",
                " rd 65500:0",
                " !",
                " address-family ipv4",
                "  route-target export 65500:0",
                "  route-target import 65500:0",
                " exit-address-family",
            ],
        )
    ]
