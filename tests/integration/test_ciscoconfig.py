from ipaddress import IPv4Interface

import pytest
import sample1

from py_net_conf_cisco import CiscoConfig, InterfaceConfig
from py_net_conf_cisco.interfaceconfig import Interface, InterfaceType


class TestCiscoConfig:
    """
    Test class for the CiscoConfig module
    """

    def test_empty_creation_fails(self):
        with pytest.raises(ValueError):
            config = CiscoConfig()
            return config

    def test_init_with_text(self):
        """Test initialization with config text."""
        config = CiscoConfig(config_text=sample1.config)
        assert config._parsed_config is not None

    def test_init_with_file(self, sample_config_file):
        """Test initialization with config file."""
        config = CiscoConfig(config_path=sample_config_file)
        assert config._parsed_config is not None

    last_line_params = [("empty_config", -1), ("config_from_file", -2)]

    @pytest.mark.parametrize("config, expected", last_line_params)
    def test__last_line(self, config, expected, request):
        config = request.getfixturevalue(config)
        assert (
            config._last_line() == config._parsed_config.config_objs[expected]
        )

    def find_hostname_line(self, parsed_config):
        return parsed_config.find_objects(r"^hostname\s+")[0]

    def test_seting_hostname_property_with_sample1(self, config_from_file):
        """Test setting the hostname"""
        config_from_file.hostname = "foo"
        assert config_from_file.hostname == "foo"
        hostname_line = self.find_hostname_line(config_from_file._parsed_config)
        assert hostname_line.text == "hostname foo"

    def test_seting_hostname_property_after_getting_hostanme(
        self, config_from_file
    ):
        """Test setting the hostname after getting the hostname"""
        hostname = config_from_file.hostname
        assert hostname == "TestSwitch"
        config_from_file.hostname = "foo"
        assert config_from_file.hostname == "foo"
        hostname_line = self.find_hostname_line(config_from_file._parsed_config)
        assert hostname_line.text == "hostname foo"

    def test_getting_hostname_property(self, config_from_file):
        """Test the hostname propeerty"""
        hostname = config_from_file.hostname
        assert hostname == "TestSwitch"
        hostname_line = self.find_hostname_line(config_from_file._parsed_config)
        assert hostname_line.text == "hostname TestSwitch"

    def test_seting_hostname_property_with_no_hostname_version_line(
        self, config_from_file
    ):
        """Test setting the hostname when there is not a hostname configured
        but there is a version line"""
        hostname_line = self.find_hostname_line(config_from_file._parsed_config)
        hostname_line.delete()
        config_from_file._parsed_config.commit()
        config_from_file.hostname = "foo"
        assert config_from_file.hostname == "foo"
        hostname_line = self.find_hostname_line(config_from_file._parsed_config)
        assert hostname_line.text == "hostname foo"

    def test_setting_hostname_property_with_empty_config(self, empty_config):
        empty_config.hostname = "foo"
        assert empty_config.hostname == "foo"
        hostname_line = self.find_hostname_line(empty_config._parsed_config)
        assert hostname_line.text == "hostname foo"

    def test_empty_hostname(self, empty_config):
        assert empty_config.hostname == ""

    def test_setting_hostname_with_empty_config(self):
        config = CiscoConfig(config_text="")
        config.hostname = "foo"
        assert config.hostname == "foo"
        hostname_line = self.find_hostname_line(config._parsed_config)
        assert hostname_line.text == "hostname foo"

    def test_setting_hostname_with_existing_config(self, config_from_file):
        config_from_file.hostname = "foo"
        assert config_from_file.hostname == "foo"
        hostname_line = self.find_hostname_line(config_from_file._parsed_config)
        assert hostname_line.text == "hostname foo"

    @pytest.mark.parametrize(
        "interface,expected",
        [
            (
                InterfaceConfig(
                    Interface(
                        interface_type=InterfaceType.VLAN,
                        interface_number="10",
                    )
                ),
                InterfaceConfig(
                    Interface(
                        interface_type=InterfaceType.VLAN,
                        interface_number="10",
                    ),
                    description="Server VLAN",
                    ip_address=IPv4Interface("10.0.10.1/24"),
                    dhcp_assigned=False,
                    shutdown=False,
                ),
            ),
            (
                InterfaceConfig(
                    Interface(
                        interface_type=InterfaceType.GIGABITETHERNET,
                        interface_number="0/3",
                    )
                ),
                InterfaceConfig(
                    Interface(
                        interface_type=InterfaceType.GIGABITETHERNET,
                        interface_number="0/3",
                    ),
                    description="DHCP Test Interface",
                    ip_address=None,
                    dhcp_assigned=True,
                    shutdown=False,
                ),
            ),
            (
                InterfaceConfig(
                    Interface(
                        interface_type=InterfaceType.VLAN,
                        interface_number="20",
                    ),
                ),
                InterfaceConfig(
                    Interface(
                        interface_type=InterfaceType.VLAN,
                        interface_number="20",
                    ),
                    description="VRF VLAN",
                    ip_address=IPv4Interface("10.10.10.1/24"),
                    dhcp_assigned=False,
                    shutdown=False,
                    vrf="Blue",
                ),
            ),
            (
                InterfaceConfig(
                    Interface(
                        interface_type=InterfaceType.VLAN,
                        interface_number="30",
                    ),
                ),
                InterfaceConfig(
                    Interface(
                        interface_type=InterfaceType.VLAN,
                        interface_number="30",
                    ),
                    description="VRF VLAN with secondary IPs",
                    ip_address=IPv4Interface("10.20.10.1/24"),
                    dhcp_assigned=False,
                    shutdown=False,
                    vrf="Blue",
                    secondary_ip_addresses=[
                        IPv4Interface("10.20.20.1/24"),
                    ],
                ),
            ),
        ],
    )
    def test_getting_interface(self, config_from_file, interface, expected):
        assert config_from_file.get_interface(interface) == expected

    def test_interface_that_does_not_exist(self, empty_config):
        interface = InterfaceConfig(
            Interface(
                interface_type=InterfaceType.LOOPBACK,
                interface_number="1234",
            ),
        )
        assert empty_config.get_interface(interface) is None

    @pytest.mark.parametrize(
        "interface",
        [
            # No change to the secondary IPs
            InterfaceConfig(
                Interface(
                    interface_type=InterfaceType.VLAN,
                    interface_number="30",
                ),
                description="Red VRF VLAN with secondary IPs",
                ip_address=IPv4Interface("1.1.1.1/24"),
                dhcp_assigned=False,
                shutdown=True,
                vrf="Red,",
                secondary_ip_addresses=[
                    IPv4Interface("10.20.20.1/24"),
                ],
            ),
            # Change interface to using DHCP
            InterfaceConfig(
                Interface(
                    interface_type=InterfaceType.VLAN,
                    interface_number="30",
                ),
                description="Red VRF VLAN with secondary IPs",
                dhcp_assigned=True,
                shutdown=True,
                vrf="Red,",
                secondary_ip_addresses=[
                    IPv4Interface("10.20.20.1/24"),
                ],
            ),
            # Change secondaries
            InterfaceConfig(
                Interface(
                    interface_type=InterfaceType.VLAN,
                    interface_number="30",
                ),
                description="Red VRF VLAN with secondary IPs",
                ip_address=IPv4Interface("1.1.1.1/24"),
                dhcp_assigned=False,
                shutdown=True,
                vrf="Red,",
                secondary_ip_addresses=[
                    IPv4Interface("10.10.10.1/24"),
                ],
            ),
            # Removal of secondaries,
            InterfaceConfig(
                Interface(
                    interface_type=InterfaceType.VLAN,
                    interface_number="30",
                ),
                description="Red VRF VLAN with secondary IPs",
                ip_address=IPv4Interface("1.1.1.1/24"),
                dhcp_assigned=False,
                shutdown=True,
                vrf="Red,",
            ),
            # More secondaries,
            InterfaceConfig(
                Interface(
                    interface_type=InterfaceType.VLAN,
                    interface_number="30",
                ),
                description="Red VRF VLAN with secondary IPs",
                ip_address=IPv4Interface("1.1.1.1/24"),
                dhcp_assigned=False,
                shutdown=True,
                vrf="Red,",
                secondary_ip_addresses=[
                    IPv4Interface("10.20.20.1/24"),
                    IPv4Interface("10.20.21.1/24"),
                ],
            ),
            # Less secondaries,
            InterfaceConfig(
                Interface(
                    interface_type=InterfaceType.VLAN,
                    interface_number="40",
                ),
                description="Red VRF VLAN with secondary IPs",
                ip_address=IPv4Interface("1.1.1.1/24"),
                dhcp_assigned=False,
                shutdown=True,
                vrf="Red,",
                secondary_ip_addresses=[
                    IPv4Interface("10.30.10.1/24"),
                ],
            ),
            # Change and more secondaries,
            InterfaceConfig(
                Interface(
                    interface_type=InterfaceType.VLAN,
                    interface_number="30",
                ),
                description="Red VRF VLAN with secondary IPs",
                ip_address=IPv4Interface("1.1.1.1/24"),
                dhcp_assigned=False,
                shutdown=True,
                vrf="Red,",
                secondary_ip_addresses=[
                    IPv4Interface("2.2.2.2/24"),
                    IPv4Interface("3.3.3.3/24"),
                ],
            ),
            # Change and less secondaries,
            InterfaceConfig(
                Interface(
                    interface_type=InterfaceType.VLAN,
                    interface_number="40",
                ),
                description="Red VRF VLAN with secondary IPs",
                ip_address=IPv4Interface("1.1.1.1/24"),
                dhcp_assigned=False,
                shutdown=True,
                vrf="Red,",
                secondary_ip_addresses=[
                    IPv4Interface("10.20.20.1/24"),
                ],
            ),
            # Add secondary IP when there was none
            InterfaceConfig(
                Interface(
                    interface_type=InterfaceType.VLAN,
                    interface_number="1",
                ),
                ip_address=IPv4Interface("192.168.1.1/24"),
                dhcp_assigned=False,
                shutdown=False,
                secondary_ip_addresses=[
                    IPv4Interface("10.20.20.1/24"),
                ],
            ),
            # Start with blank interface,
            InterfaceConfig(
                Interface(
                    interface_type=InterfaceType.GIGABITETHERNET,
                    interface_number="0/4",
                ),
                description="Red VRF VLAN with secondary IPs",
                ip_address=IPv4Interface("1.1.1.1/24"),
                dhcp_assigned=False,
                shutdown=True,
                vrf="Red,",
                secondary_ip_addresses=[
                    IPv4Interface("10.20.20.1/24"),
                ],
            ),
            # Start with no interface,
            InterfaceConfig(
                Interface(
                    interface_type=InterfaceType.GIGABITETHERNET,
                    interface_number="0/5",
                ),
                description="Red VRF VLAN with secondary IPs",
                ip_address=IPv4Interface("1.1.1.1/24"),
                dhcp_assigned=False,
                shutdown=True,
                vrf="Red,",
                secondary_ip_addresses=[
                    IPv4Interface("10.20.20.1/24"),
                ],
            ),
            # Test ip change from DHCP to static
            InterfaceConfig(
                Interface(
                    interface_type=InterfaceType.GIGABITETHERNET,
                    interface_number="0/3",
                ),
                ip_address=IPv4Interface("1.1.1.1/24"),
                dhcp_assigned=False,
                shutdown=False,
            ),
            # Test enabling and interface
            InterfaceConfig(
                Interface(
                    InterfaceType.VLAN,
                    interface_number="1",
                ),
                ip_address=IPv4Interface("192.168.1.1/24"),
                dhcp_assigned=False,
                shutdown=False,
            ),
        ],
    )
    def test_setting_interface(self, config_from_file, interface):
        assert config_from_file.set_interface(interface) is True
        assert config_from_file.get_interface(interface) == interface

    def test__unexpected_config_line(self, empty_config):
        with pytest.raises(ValueError):
            empty_config._unexpected_config_line(
                empty_config._parsed_config.config_objs[0]
            )
            return empty_config

    def test__unexpected_config_line_with_config_obj(self, empty_config):
        with pytest.raises(ValueError):
            empty_config._unexpected_config_line(
                empty_config._parsed_config.config_objs[0]
            )
            return empty_config

    def test_multiple_interface_lines(self, empty_config):
        line = empty_config._parsed_config.config_objs[0]
        line.insert_after("interface GigabitEthernet0/6")
        line.insert_after("interface GigabitEthernet0/6")
        interface = InterfaceConfig(
            Interface(
                interface_type=InterfaceType.GIGABITETHERNET,
                interface_number="0/6",
            ),
        )
        with pytest.raises(ValueError, match="Found multiple interfaces"):
            empty_config._unexpected_config_line(
                empty_config.get_interface(interface)
            )
            pass
        with pytest.raises(ValueError, match="Found multiple interfaces"):
            empty_config._unexpected_config_line(
                empty_config.set_interface(interface)
            )
            return empty_config

    @pytest.mark.parametrize(
        "interface,lines,match",
        [
            (  # Test for an unknown interface configuration line
                InterfaceConfig(
                    Interface(
                        interface_type=InterfaceType.VLAN, interface_number="1"
                    ),
                ),
                [
                    " bogus_line",
                ],
                "Unexpected config line:  bogus_line",
            ),
            (  # Test ip config with 5 words that are not a known option)
                InterfaceConfig(
                    Interface(
                        interface_type=InterfaceType.VLAN,
                        interface_number="1",
                    ),
                ),
                [
                    " ip address 192.168.1.1 255.255.255.0 bogus",
                ],
                "Unexpected config line:  ip address 192.168.1.1 255.255.255.0 bogus",
            ),
            (  # Test ip config with known option)
                InterfaceConfig(
                    Interface(
                        interface_type=InterfaceType.VLAN,
                        interface_number="1",
                    ),
                ),
                [
                    " ip address bogus",
                ],
                "Unexpected config line:  ip address bogus",
            ),
        ],
    )
    def test_get_interface_config_exceptions(
        self, config_from_file, interface, lines, match
    ):
        interface_line = config_from_file._find_interface_lines(interface)[0]
        for line in lines:
            interface_line.insert_after(line)
        with pytest.raises(ValueError, match=match):
            config_from_file.get_interface(interface)

    @pytest.mark.parametrize(
        "interface,lines,match",
        [
            (  # Test for an unknown interface configuration line
                InterfaceConfig(
                    Interface(
                        interface_type=InterfaceType.VLAN,
                        interface_number="1",
                    ),
                ),
                [
                    " bogus_line",
                ],
                "Unexpected config line:  bogus_line",
            ),
            (  # Test ip config with 5 words that are not a known option
                InterfaceConfig(
                    Interface(
                        interface_type=InterfaceType.VLAN,
                        interface_number="1",
                    ),
                ),
                [
                    " ip address 192.168.1.1 255.255.255.0 bogus",
                ],
                "Unexpected config line:  ip address 192.168.1.1 255.255.255.0 bogus",
            ),
            (  # Test ip config with known option
                InterfaceConfig(
                    Interface(
                        interface_type=InterfaceType.VLAN,
                        interface_number="1",
                    ),
                ),
                [
                    " ip address bogus",
                ],
                "Unexpected config line:  ip address bogus",
            ),
        ],
    )
    def test_set_interface_config_exceptions(
        self, config_from_file, interface, lines, match
    ):
        interface_line = config_from_file._find_interface_lines(interface)[0]
        for line in lines:
            interface_line.insert_after(line)
        with pytest.raises(ValueError, match=match):
            config_from_file.set_interface(interface)

    def test_add_secondary_with_no_primary(self, config_from_file: CiscoConfig):
        interface = InterfaceConfig(
            Interface(
                interface_type=InterfaceType.VLAN,
                interface_number="1",
            ),
            secondary_ip_addresses=[
                IPv4Interface("1.1.1.1/24"),
            ],
        )

        exception_string = "Trying to add secondary IP with no primary IP"
        interface_line = config_from_file._find_interface_lines(interface)[0]
        ip_line = interface_line.re_search_children(r"ip address.*")[0]
        ip_line.re_sub(r"ip address.*", "!")
        config_from_file._parsed_config.commit()
        with pytest.raises(ValueError, match=exception_string):
            config_from_file.set_interface(interface)
