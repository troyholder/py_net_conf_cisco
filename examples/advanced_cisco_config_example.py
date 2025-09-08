#!/usr/bin/env python3
"""
Advanced example script demonstrating complex CiscoConfig functionality.

This script:
1. Loads an advanced Cisco configuration file with VRF, TACACS, RADIUS, and logging
2. Makes sophisticated configuration changes using CiscoConfig properties
3. Demonstrates interface VRF assignments, TACACS group management, RADIUS server updates, and logging modifications
4. Saves the modified configuration to a new file
"""

from ipaddress import IPv4Address, IPv4Interface
from pathlib import Path

from py_net_conf_cisco.ciscoconfig import CiscoConfig
from py_net_conf_cisco.interfaceconfig import (
    Interface,
    InterfaceConfig,
    InterfaceType,
)
from py_net_conf_cisco.loggingconfig import LoggingConfig
from py_net_conf_cisco.radiusserverconfig import RadiusServerConfig
from py_net_conf_cisco.tacacsgroupconfig import (
    TacacsServerGroupConfig,
    TacacsServerPrivateConfig,
)
from py_net_conf_cisco.tacacsserverconfig import TacacsServerConfig


def main():
    # Define file paths
    input_file = Path("advanced_config.cfg")
    output_file = Path("advanced_config_modified.cfg")

    print(f"Loading advanced configuration from: {input_file}")
    print("=" * 60)

    # Load the configuration file
    config = CiscoConfig(config_path=input_file)

    # Display current hostname
    print(f"Current hostname: {config.hostname}")

    # Change the hostname
    print("Changing hostname to 'EnterpriseRouter'")
    config.hostname = "EnterpriseRouter"
    print(f"New hostname: {config.hostname}")
    print()

    # Work with VRF-assigned interfaces
    print("INTERFACE VRF MANAGEMENT:")
    print("-" * 40)

    # Modify the Management interface (GigabitEthernet0/1)
    mgmt_interface = Interface(
        interface_type=InterfaceType.GIGABITETHERNET, interface_number="0/1"
    )

    # Get current management interface configuration
    mgmt_config_query = InterfaceConfig(interface=mgmt_interface)
    current_mgmt_config = config.get_interface(mgmt_config_query)

    if current_mgmt_config:
        print(f"Current management interface VRF: {current_mgmt_config.vrf}")
        print(f"Current management IP: {current_mgmt_config.ip_address}")

        # Modify the management interface with new IP and keep VRF
        modified_mgmt_config = InterfaceConfig(
            interface=mgmt_interface,
            description="Enhanced Management Network - NOC Access",
            ip_address=IPv4Interface("10.1.2.1/24"),
            vrf="MANAGEMENT",
            shutdown=False,
        )

        print("Modifying management interface with new IP and description")
        config.set_interface(modified_mgmt_config)

    # Work with Guest interface
    guest_interface = Interface(
        interface_type=InterfaceType.GIGABITETHERNET, interface_number="0/2"
    )

    guest_config_query = InterfaceConfig(interface=guest_interface)
    current_guest_config = config.get_interface(guest_config_query)

    if current_guest_config:
        print(f"Current guest interface VRF: {current_guest_config.vrf}")

        # Modify guest interface to use a different VRF
        modified_guest_config = InterfaceConfig(
            interface=guest_interface,
            description="Isolated Guest Network - Limited Access",
            ip_address=IPv4Interface("192.168.200.1/24"),
            vrf="GUEST",
            shutdown=False,
        )

        print("Updating guest interface configuration")
        config.set_interface(modified_guest_config)

    # Add a new interface with VRF assignment
    new_dmz_interface = Interface(
        interface_type=InterfaceType.GIGABITETHERNET, interface_number="0/3"
    )

    new_dmz_config = InterfaceConfig(
        interface=new_dmz_interface,
        description="DMZ Network - Public Services",
        ip_address=IPv4Interface("172.16.10.1/24"),
        shutdown=False,
    )

    print("Adding new DMZ interface (GigabitEthernet0/3)")
    config.set_interface(new_dmz_config)
    print()

    # Work with RADIUS servers
    print("RADIUS SERVER MANAGEMENT:")
    print("-" * 40)

    # Get current RADIUS servers
    current_radius_servers = config.radius_servers
    print(f"Current RADIUS servers: {len(current_radius_servers)}")
    for server in current_radius_servers:
        print(f"  - {server.name}: {server.ip_address}:{server.auth_port}")

    # Create new RADIUS server configuration
    new_radius_servers = [
        RadiusServerConfig(
            ip_address=IPv4Address("10.1.1.210"),
            name="NEW-PRIMARY-RADIUS",
            key="0A1B2C3D4E5F6789",
            auth_port=1812,
            acct_port=1813,
        ),
        RadiusServerConfig(
            ip_address=IPv4Address("10.1.1.211"),
            name="NEW-BACKUP-RADIUS",
            key="9F8E7D6C5B4A3210",
            auth_port=1812,
            acct_port=1813,
        ),
        RadiusServerConfig(
            ip_address=IPv4Address("10.1.1.212"),
            name="EMERGENCY-RADIUS",
            key="ABCDEF1234567890",
            auth_port=1645,  # Non-standard port
            acct_port=1646,
        ),
    ]

    print("Replacing RADIUS servers with new configuration")
    config.radius_servers = new_radius_servers

    updated_radius_servers = config.radius_servers
    print(f"Updated RADIUS servers: {len(updated_radius_servers)}")
    for server in updated_radius_servers:
        print(f"  - {server.name}: {server.ip_address}:{server.auth_port}")
    print()

    # Work with TACACS server groups
    print("TACACS SERVER GROUP MANAGEMENT:")
    print("-" * 40)

    # Get current TACACS groups
    current_tacacs_groups = config.tacacs_group
    print(f"Current TACACS groups: {len(current_tacacs_groups)}")
    for group in current_tacacs_groups:
        print(f"  - Group: {group.name}")
        print(f"    VRF: {group.vrf}")
        print(f"    Source Interface: {group.source_interface}")
        print(f"    Private Servers: {len(group.server_private_list)}")

    # Create enhanced TACACS group configuration
    enhanced_tacacs_groups = [
        TacacsServerGroupConfig(
            name="ENHANCED-CORP-TACACS",
            vrf="MANAGEMENT",
            source_interface=Interface(
                interface_type=InterfaceType.LOOPBACK, interface_number="100"
            ),
            server_private_list=[
                TacacsServerPrivateConfig(
                    ip_address=IPv4Address("10.1.1.160"),
                    key_mode=7,
                    key="NewPrimaryTacacsKey123",
                ),
                TacacsServerPrivateConfig(
                    ip_address=IPv4Address("10.1.1.161"),
                    key_mode=7,
                    key="NewBackupTacacsKey456",
                ),
                TacacsServerPrivateConfig(
                    ip_address=IPv4Address("10.1.1.162"),
                    key_mode=7,
                    key="EmergencyTacacsKey789",
                ),
            ],
        ),
        TacacsServerGroupConfig(
            name="GUEST-TACACS",
            vrf="GUEST",
            server_private_list=[
                TacacsServerPrivateConfig(
                    ip_address=IPv4Address("192.168.200.10"),
                    key_mode=7,
                    key="GuestTacacsKey999",
                ),
            ],
        ),
    ]

    print("Updating TACACS server groups with enhanced configuration")
    config.tacacs_group = enhanced_tacacs_groups

    updated_tacacs_groups = config.tacacs_group
    print(f"Updated TACACS groups: {len(updated_tacacs_groups)}")
    for group in updated_tacacs_groups:
        print(f"  - Group: {group.name}")
        print(f"    VRF: {group.vrf}")
        print(f"    Source Interface: {group.source_interface}")
        print(f"    Private Servers: {len(group.server_private_list)}")
    print()

    # Work with TACACS servers (individual servers)
    print("TACACS SERVER MANAGEMENT:")
    print("-" * 40)

    # Get current TACACS servers
    current_tacacs_servers = config.tacacs_servers
    print(f"Current individual TACACS servers: {len(current_tacacs_servers)}")
    for server in current_tacacs_servers:
        print(f"  - {server.ip_address}: {server.encrpyted_string}")

    # Create new TACACS server configuration
    new_tacacs_servers = [
        TacacsServerConfig(
            ip_address=IPv4Address("10.1.1.170"),
            encrpyted_string="GlobalTacacsKey001",
        ),
        TacacsServerConfig(
            ip_address=IPv4Address("10.1.1.171"),
            encrpyted_string="GlobalTacacsKey002",
        ),
    ]

    print("Updating individual TACACS servers")
    config.tacacs_servers = new_tacacs_servers

    updated_tacacs_servers = config.tacacs_servers
    print(f"Updated individual TACACS servers: {len(updated_tacacs_servers)}")
    for server in updated_tacacs_servers:
        print(f"  - {server.ip_address}: {server.encrpyted_string}")
    print()

    # Work with logging servers
    print("LOGGING SERVER MANAGEMENT:")
    print("-" * 40)

    # Get current logging servers
    current_logging_servers = config.logging_servers
    print(f"Current logging servers: {len(current_logging_servers)}")
    for server in current_logging_servers:
        if server.syslog_ip_address:
            print(f"  - IP: {server.syslog_ip_address}, VRF: {server.vrf}")
        else:
            print(f"  - FQDN: {server.syslog_fqdn}, VRF: {server.vrf}")

    # Create new logging server configuration
    new_logging_servers = [
        LoggingConfig(
            syslog_ip_address=IPv4Address("10.1.1.60"),
            vrf="",
        ),
        LoggingConfig(
            syslog_ip_address=IPv4Address("10.1.1.61"),
            vrf="MANAGEMENT",
        ),
        LoggingConfig(
            syslog_ip_address=IPv4Address("192.168.200.20"),
            vrf="GUEST",
        ),
        LoggingConfig(
            syslog_fqdn="syslog.corporate.local",
            vrf="MANAGEMENT",
        ),
    ]

    print("Updating logging servers with VRF-aware configuration")
    config.logging_servers = new_logging_servers

    updated_logging_servers = config.logging_servers
    print(f"Updated logging servers: {len(updated_logging_servers)}")
    for server in updated_logging_servers:
        if server.syslog_ip_address:
            print(f"  - IP: {server.syslog_ip_address}, VRF: {server.vrf}")
        else:
            print(f"  - FQDN: {server.syslog_fqdn}, VRF: {server.vrf}")
    print()

    # Save the modified configuration
    print("CONFIGURATION SAVE:")
    print("-" * 40)
    print(f"Saving enhanced configuration to: {output_file}")

    # Get the configuration text and write to file
    config_lines = config.get_text()
    with open(output_file, "w") as f:
        for line in config_lines:
            f.write(line + "\n")

    print("Advanced configuration modification complete!")
    print(f"Original file: {input_file}")
    print(f"Modified file: {output_file}")
    print()

    # Display comprehensive summary of changes made
    print("COMPREHENSIVE SUMMARY OF CHANGES:")
    print("=" * 60)
    print("✓ Hostname changed from 'AdvancedRouter' to 'EnterpriseRouter'")
    print()
    print("✓ Interface VRF Management:")
    print("  • Enhanced GigabitEthernet0/1 (Management VRF)")
    print("    - Updated IP from 10.1.1.1/24 to 10.1.2.1/24")
    print("    - Enhanced description for NOC access")
    print("  • Modified GigabitEthernet0/2 (Guest VRF)")
    print("    - Updated IP to 192.168.200.1/24")
    print("    - Enhanced security description")
    print("  • Added GigabitEthernet0/3 (DMZ)")
    print("    - New DMZ network: 172.16.10.1/24")
    print()
    print("✓ RADIUS Server Infrastructure:")
    print("  • Replaced 2 existing servers with 3 new servers")
    print("  • Added emergency RADIUS with non-standard ports")
    print("  • Enhanced security keys and naming convention")
    print()
    print("✓ TACACS Server Group Management:")
    print("  • Enhanced CORP-TACACS group with 3 servers")
    print("  • Added new GUEST-TACACS group for guest network")
    print("  • Implemented VRF-aware TACACS configuration")
    print("  • Updated source interface assignments")
    print()
    print("✓ Individual TACACS Servers:")
    print("  • Replaced existing servers with new global servers")
    print("  • Updated encryption keys for enhanced security")
    print()
    print("✓ Logging Infrastructure:")
    print("  • Implemented VRF-aware logging")
    print("  • Added dedicated logging per network segment")
    print("  • Included FQDN-based logging for management VRF")
    print("  • Enhanced redundancy with multiple log servers")


if __name__ == "__main__":
    main()
