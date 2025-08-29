"""
Test suite for the interface datamodels.
"""

import ipaddress
import re
from ipaddress import IPv4Interface

import pytest

from py_net_conf_cisco.interfaceconfig import (
    Interface,
    InterfaceConfig,
    InterfaceType,
)


class TestInterface:
    failing_cases = [
        (
            {},
            TypeError,
            re.escape(
                "Interface.__init__() missing 2 required positional arguments: 'interface_type' and 'interface_number'"
            ),
        ),
        (
            {
                "interface_type": "foo",
            },
            TypeError,
            re.escape(
                "Interface.__init__() missing 1 required positional argument: 'interface_number'"
            ),
        ),
        (
            {
                "interface_number": "foo",
            },
            TypeError,
            re.escape(
                "Interface.__init__() missing 1 required positional argument: 'interface_type'"
            ),
        ),
        (
            {
                "interface_type": "foo",
                "interface_number": "bar",
            },
            TypeError,
            re.escape("interface_type is not a InterfaceType"),
        ),
        (
            {
                "interface_type": InterfaceType.GIGABITETHERNET,
                "interface_number": 9,
            },
            TypeError,
            re.escape("interface_number is not a string"),
        ),
        (
            {
                "interface_type": InterfaceType.GIGABITETHERNET,
                "interface_number": "1/1",
                "subinterface_number": "0",
            },
            TypeError,
            re.escape("subinterface_number is not an integer"),
        ),
        (
            {
                "interface_type": InterfaceType.GIGABITETHERNET,
                "interface_number": "1/1",
                "subinterface_number": -1,
            },
            ValueError,
            re.escape("subinterface_number must be a positive integer"),
        ),
        (
            {
                "interface_type": InterfaceType.GIGABITETHERNET,
                "interface_number": "1/A",
            },
            ValueError,
            re.escape("interface_number contains unexpected characters: A"),
        ),
        (
            {
                "interface_type": InterfaceType.GIGABITETHERNET,
                "interface_number": "1.A",
            },
            ValueError,
            re.escape("interface_number contains unexpected characters: ., A"),
        ),
    ]

    @pytest.mark.parametrize("kwargs, error_type, warning", failing_cases)
    def test_failing_creations(self, kwargs, error_type, warning):
        """Test failing creations"""
        with pytest.raises(error_type, match=warning):
            interface = Interface(**kwargs)  # pyright: ignore  # ty: ignore[missing-argument]
            return interface

    working_cases = [
        (
            {
                "interface_type": InterfaceType.GIGABITETHERNET,
                "interface_number": "9",
            },
            "GigabitEthernet9",
        ),
        (
            {
                "interface_type": InterfaceType.GIGABITETHERNET,
                "interface_number": "9",
                "subinterface_number": 11,
            },
            "GigabitEthernet9.11",
        ),
        (
            {
                "interface_type": InterfaceType.GIGABITETHERNET,
                "interface_number": "1/1",
            },
            "GigabitEthernet1/1",
        ),
        (
            {
                "interface_type": InterfaceType.GIGABITETHERNET,
                "interface_number": "1/1",
                "subinterface_number": 11,
            },
            "GigabitEthernet1/1.11",
        ),
        (
            {
                "interface_type": InterfaceType.VLAN,
                "interface_number": "20",
            },
            "Vlan20",
        ),
        (
            {
                "interface_type": InterfaceType.PORT_CHANNEL,
                "interface_number": "1",
            },
            "Port-channel1",
        ),
        (
            {
                "interface_type": InterfaceType.PORT_CHANNEL,
                "interface_number": "1",
                "subinterface_number": 11,
            },
            "Port-channel1.11",
        ),
    ]

    @pytest.mark.parametrize("kwargs, string", working_cases)
    def test_working_creations(self, kwargs, string):
        interface = Interface(**kwargs)  # ty: ignore[missing-argument]
        assert interface.interface_type == kwargs["interface_type"]
        assert interface.interface_number == kwargs["interface_number"]

    @pytest.mark.parametrize("kwargs, string", working_cases)
    def test_string_representation(self, kwargs, string):
        interface = Interface(**kwargs)  # ty: ignore[missing-argument]
        assert str(interface) == string


class TestInterfaceConfig:
    """Test class for the InterfaceConfig dataclass."""

    def test_empty_creation_throws_excptions(self):
        """Test a empty creation fails"""
        with pytest.raises(TypeError):
            interface = InterfaceConfig()  # pyright: ignore  # ty: ignore[missing-argument]
            return interface

    def test_creation_with_no_interface_type_throws_exception(self):
        """Test a creation with no InterfaceType failes"""
        with pytest.raises(TypeError):
            interface = InterfaceConfig(Interface(interface_number="1"))  # pyright: ignore  # ty: ignore[missing-argument]
            return interface

    def test_creation_with_no_number_type_throws_exception(self):
        """Test a creation with no InterfaceType failes"""
        with pytest.raises(TypeError):
            interface = InterfaceConfig(Interface(InterfaceType.ETHERNET))  # pyright: ignore  # ty: ignore[missing-argument]
            return interface

    def test_basic_creation(self):
        """Test with only an InterfaceType"""
        interface = InterfaceConfig(
            Interface(InterfaceType.ETHERNET, interface_number="1")
        )
        assert interface is not None
        assert interface.ip_address is None
        assert interface.vrf is None
        assert interface.description is None
        assert interface.shutdown is None

    def test_interface_with_ip(self):
        """Test interface creation with IP address."""
        interface = InterfaceConfig(
            Interface(
                interface_type=InterfaceType.ETHERNET,
                interface_number="1",
            ),
            ip_address=IPv4Interface("1.1.1.1/24"),
        )
        assert interface.interface.interface_type == InterfaceType.ETHERNET
        assert interface.ip_address == IPv4Interface("1.1.1.1/24")
        assert interface.dhcp_assigned is not True

    def test_interface_with_dhcp(self):
        """Test the IP address can be set with DHCP"""
        interface = InterfaceConfig(
            Interface(
                interface_type=InterfaceType.ETHERNET, interface_number="1"
            ),
            dhcp_assigned=True,
        )
        assert interface.interface.interface_type == InterfaceType.ETHERNET
        assert interface.ip_address is None
        assert interface.dhcp_assigned

    def test_interface_with_dhcp_and_ip_fails(self):
        """Test the IP address and DHCP fails"""
        with pytest.raises(Exception):
            interface = InterfaceConfig(
                Interface(
                    interface_type=InterfaceType.ETHERNET,
                    interface_number="1",
                ),
                dhcp_assigned=True,
                ip_address=IPv4Interface("1.1.1.1/24"),
            )
            return interface

    def test_interface_with_false_dhcp_and_no_ip_fails(self):
        """Test the IP address and DHCP fails"""
        with pytest.raises(Exception):
            interface = InterfaceConfig(
                Interface(
                    interface_type=InterfaceType.ETHERNET,
                    interface_number="1",
                ),
                dhcp_assigned=False,
            )
            return interface

    # Testing parameterization cases
    cases = [
        (
            {  # Test with minimal configuration
                "interface": Interface(InterfaceType.ETHERNET, "1"),
            },
            ["interface Ethernet1", "!"],
            {
                "interface_string": "interface Ethernet1",
                "description_string": "",
                "vrf_string": "",
                "ip_string": "",
                "secondary_ip_strings": [],
                "shutdown_string": "",
            },
        ),
        (  # Test with an IP address
            {
                "interface": Interface(
                    InterfaceType.ETHERNET,
                    "1",
                ),
                "ip_address": ipaddress.IPv4Interface("192.168.1.1/24"),
            },
            [
                "interface Ethernet1",
                " ip address 192.168.1.1 255.255.255.0",
                "!",
            ],
            {
                "interface_string": "interface Ethernet1",
                "description_string": "",
                "vrf_string": "",
                "ip_string": "ip address 192.168.1.1 255.255.255.0",
                "secondary_ip_strings": [],
                "shutdown_string": "",
            },
        ),
        (  # Test with an IP address and a VRF)
            {
                "interface": Interface(
                    InterfaceType.ETHERNET,
                    "1",
                ),
                "ip_address": ipaddress.IPv4Interface("1.1.1.1/24"),
                "vrf": "test",
            },
            [
                "interface Ethernet1",
                " vrf forwarding test",
                " ip address 1.1.1.1 255.255.255.0",
                "!",
            ],
            {
                "interface_string": "interface Ethernet1",
                "description_string": "",
                "vrf_string": "vrf forwarding test",
                "ip_string": "ip address 1.1.1.1 255.255.255.0",
                "secondary_ip_strings": [],
                "shutdown_string": "",
            },
        ),
        (  # Test with DHCP address
            {
                "interface": Interface(
                    InterfaceType.ETHERNET,
                    "1",
                ),
                "dhcp_assigned": True,
            },
            [
                "interface Ethernet1",
                " ip address dhcp",
                "!",
            ],
            {
                "interface_string": "interface Ethernet1",
                "description_string": "",
                "vrf_string": "",
                "ip_string": "ip address dhcp",
                "secondary_ip_strings": [],
                "shutdown_string": "",
            },
        ),
        (  # Test with a description
            {
                "interface": Interface(
                    InterfaceType.ETHERNET,
                    "1",
                ),
                "description": "Test description",
            },
            ["interface Ethernet1", " description Test description", "!"],
            {
                "interface_string": "interface Ethernet1",
                "description_string": "description Test description",
                "vrf_string": "",
                "ip_string": "",
                "secondary_ip_strings": [],
                "shutdown_string": "",
            },
        ),
        (  # Test with shutdown
            {
                "interface": Interface(
                    InterfaceType.ETHERNET,
                    "1",
                ),
                "shutdown": True,
            },
            ["interface Ethernet1", " shutdown", "!"],
            {
                "interface_string": "interface Ethernet1",
                "description_string": "",
                "vrf_string": "",
                "ip_string": "",
                "secondary_ip_strings": [],
                "shutdown_string": "shutdown",
            },
        ),
        (  # Test with shutdown False
            {
                "interface": Interface(
                    InterfaceType.ETHERNET,
                    "1",
                ),
                "shutdown": False,
            },
            ["interface Ethernet1", " no shutdown", "!"],
            {
                "interface_string": "interface Ethernet1",
                "description_string": "",
                "vrf_string": "",
                "ip_string": "",
                "secondary_ip_strings": [],
                "shutdown_string": "no shutdown",
            },
        ),
        (  # Test with secondary IPs
            {
                "interface": Interface(
                    InterfaceType.VLAN,
                    "10",
                ),
                "ip_address": IPv4Interface("10.0.10.1/24"),
                "secondary_ip_addresses": [
                    IPv4Interface("10.0.11.1/24"),
                    IPv4Interface("10.0.12.1/24"),
                ],
            },
            [
                "interface Vlan10",
                " ip address 10.0.10.1 255.255.255.0",
                " ip address 10.0.11.1 255.255.255.0 secondary",
                " ip address 10.0.12.1 255.255.255.0 secondary",
                "!",
            ],
            {
                "interface_string": "interface Vlan10",
                "description_string": "",
                "vrf_string": "",
                "ip_string": "ip address 10.0.10.1 255.255.255.0",
                "secondary_ip_strings": [
                    "ip address 10.0.11.1 255.255.255.0 secondary",
                    "ip address 10.0.12.1 255.255.255.0 secondary",
                ],
                "shutdown_string": "",
            },
        ),
    ]

    @pytest.mark.parametrize("kwargs,expected_lines,expected_strings", cases)
    def test_to_interface_line(self, kwargs, expected_lines, expected_strings):
        interface = InterfaceConfig(**kwargs)  # ty: ignore[missing-argument]
        assert interface.interface_line() == expected_lines[0]

    @pytest.mark.parametrize("kwargs,expected_lines,expected_strings", cases)
    def test_to_config_lines(self, kwargs, expected_lines, expected_strings):
        interface = InterfaceConfig(**kwargs)  # ty: ignore[missing-argument]
        assert interface.to_config_lines() == expected_lines

    @pytest.mark.parametrize("kwargs,expected_lines,expected_strings", cases)
    def test_to_expected_strings(
        self, kwargs, expected_lines, expected_strings
    ):
        interface = InterfaceConfig(**kwargs)  # ty: ignore[missing-argument]
        assert (
            interface.interface_string() == expected_strings["interface_string"]
        )
        assert (
            interface.description_string()
            == expected_strings["description_string"]
        )
        assert interface.vrf_string() == expected_strings["vrf_string"]
        assert interface.ip_string() == expected_strings["ip_string"]
        assert (
            interface.secondary_ip_strings()
            == expected_strings["secondary_ip_strings"]
        )
        assert (
            interface.shutdown_string() == expected_strings["shutdown_string"]
        )
