#!/usr/bin/env python3
"""
Simple example script demonstrating CiscoConfig functionality.

This script:
1. Loads a basic Cisco configuration file
2. Makes several configuration changes using CiscoConfig properties
3. Saves the modified configuration to a new file
"""

from ipaddress import IPv4Interface
from pathlib import Path

from py_net_conf_cisco.ciscoconfig import CiscoConfig
from py_net_conf_cisco.interfaceconfig import (
    Interface,
    InterfaceConfig,
    InterfaceType,
)


def main():
    # Define file paths
    input_file = Path("basic_config.cfg")
    output_file = Path("basic_config_modified.cfg")

    print(f"Loading configuration from: {input_file}")

    # Load the configuration file
    config = CiscoConfig(config_path=input_file)

    # Display current hostname
    print(f"Current hostname: {config.hostname}")

    # Change the hostname
    print("Changing hostname to 'ModifiedRouter'")
    config.hostname = "ModifiedRouter"

    # Work with interfaces - modify the WAN interface (GigabitEthernet0/0)
    wan_interface = Interface(
        interface_type=InterfaceType.GIGABITETHERNET, interface_number="0/0"
    )

    # Get current WAN interface configuration
    wan_config_query = InterfaceConfig(interface=wan_interface)
    current_wan_config = config.get_interface(wan_config_query)

    if current_wan_config:
        print(
            f"Current WAN interface description: {current_wan_config.description}"
        )
        print(f"Current WAN IP address: {current_wan_config.ip_address}")

        # Modify the WAN interface
        modified_wan_config = InterfaceConfig(
            interface=wan_interface,
            description="Modified WAN Interface - External Connection",
            ip_address=IPv4Interface("192.168.100.1/24"),
            shutdown=False,
        )

        print("Modifying WAN interface with new description and IP address")
        config.set_interface(modified_wan_config)

    # Work with the LAN interface (GigabitEthernet0/1)
    lan_interface = Interface(
        interface_type=InterfaceType.GIGABITETHERNET, interface_number="0/1"
    )

    # Get current LAN interface configuration
    lan_config_query = InterfaceConfig(interface=lan_interface)
    current_lan_config = config.get_interface(lan_config_query)

    if current_lan_config:
        print(
            f"Current LAN interface description: {current_lan_config.description}"
        )
        print(f"Current LAN IP address: {current_lan_config.ip_address}")

        # Modify the LAN interface
        modified_lan_config = InterfaceConfig(
            interface=lan_interface,
            description="Modified LAN Interface - Internal Network",
            ip_address=IPv4Interface("10.0.10.1/24"),
            shutdown=False,
        )

        print("Modifying LAN interface with new description and IP address")
        config.set_interface(modified_lan_config)

    # Add a new VLAN interface
    vlan_interface = Interface(
        interface_type=InterfaceType.VLAN, interface_number="100"
    )

    new_vlan_config = InterfaceConfig(
        interface=vlan_interface,
        description="Management VLAN Interface",
        ip_address=IPv4Interface("192.168.100.1/24"),
        shutdown=False,
    )

    print("Adding new VLAN 100 interface")
    config.set_interface(new_vlan_config)

    # Save the modified configuration
    print(f"Saving modified configuration to: {output_file}")

    # Get the configuration text and write to file
    config_lines = config.get_text()
    with open(output_file, "w") as f:
        for line in config_lines:
            f.write(line + "\n")

    print("Configuration modification complete!")
    print(f"Original file: {input_file}")
    print(f"Modified file: {output_file}")

    # Display summary of changes made
    print("\nSummary of changes made:")
    print("- Changed hostname from 'TestRouter' to 'ModifiedRouter'")
    print("- Modified WAN interface (GigabitEthernet0/0):")
    print("  * Updated description")
    print("  * Changed IP from 192.168.1.1/24 to 192.168.100.1/24")
    print("- Modified LAN interface (GigabitEthernet0/1):")
    print("  * Updated description")
    print("  * Changed IP from 10.0.1.1/24 to 10.0.10.1/24")
    print("- Added new VLAN 100 interface with management IP")


if __name__ == "__main__":
    main()
