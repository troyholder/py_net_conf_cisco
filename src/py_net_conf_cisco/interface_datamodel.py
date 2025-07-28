"""
Data models for Cisco interface configuration options.

This module provides dataclasses and enums for structuring interface configuration options.
"""

import string
from dataclasses import dataclass, field
from enum import Enum
from ipaddress import IPv4Interface
from typing import Optional

interface_number_chars = set(string.digits + "/")


class InterfaceType(Enum):
    """
    Allowabld interface types
    """

    ETHERNET = "Ethernet"
    GIGABITETHERNET = "GigabitEthernet"
    TENGIGABITETHERNET = "TenGigabitEthernet"
    TWENTYFIVEGIGABITETHERNET = "TwentyFiveGigE"
    FORTYGIGABITETHERNET = "FortyGigabitEthernet"
    HUNDREDGIGABITETHERNET = "HundredGigE"
    VLAN = "Vlan"
    LOOPBACK = "Loopback"
    PORT_CHANNEL = "Port-channel"
    NVE = "nve"


@dataclass
class Interface:
    """
    Represents an interface

    Attributes:
            interface_type: The type of interface (e.g., GigabitEthernet).
            interface_number: The number of the interface as a string (e.g., 1/1/1).
            subinterface_number: Optional subinterface number.
    """

    interface_type: InterfaceType
    interface_number: str
    subinterface_number: Optional[int] = None

    def __post_init__(self):
        if type(self.interface_type) is not InterfaceType:
            raise TypeError("interface_type is not a InterfaceType")
        if type(self.interface_number) is not str:
            raise TypeError("interface_number is not a string")
        if (
            self.subinterface_number is not None
            and type(self.subinterface_number) is not int
        ):
            raise TypeError("subinterface_number is not an integer")
        if (
            self.subinterface_number is not None
            and self.subinterface_number < 0
        ):
            raise ValueError("subinterface_number must be a positive integer")
        # interface_number_chars = set(string.digits + "/")
        unexpected_chars = list(
            set(self.interface_number) - interface_number_chars
        )
        unexpected_chars.sort()
        if unexpected_chars:
            raise ValueError(
                f"interface_number contains unexpected characters: {', '.join(unexpected_chars)}"
            )

    def __str__(self) -> str:
        return f"{self.interface_type.value}{self.interface_number}{'' if self.subinterface_number is None else '.' + str(self.subinterface_number)}"


@dataclass
class InterfaceConfig:
    """
    Represents an interface configuration.

    Attributes:
            interface: Interface object
            ip_address: Optional IPv4 interface address (ipaddress.IPv4Interface).
            vrf: Optional VRF assignment as a string.
            dhcp_assigned: If True, IP address is assigned by DHCP.
            description: Optional interface description.
            shutdown: If True, the interface is administratively shut down.
            secondary_ip_addresses: Optional list of secondary  IPv4 interface address (ipaddress.IPv4Interface).
    """

    interface: Interface
    ip_address: Optional[IPv4Interface] = None
    vrf: Optional[str] = None
    dhcp_assigned: Optional[bool] = None
    description: Optional[str] = None
    shutdown: Optional[bool] = None
    secondary_ip_addresses: list[IPv4Interface] = field(default_factory=list)

    def __post_init__(self):
        # Verify that the ip address the interface has is either DHCP or staticall assigned.
        if any(
            [
                self.dhcp_assigned is True and self.ip_address is not None,
                self.dhcp_assigned is False and self.ip_address is None,
            ]
        ):
            raise ValueError(
                "An interface cannot have both a static IP and be configured for DHCP."
            )

    def interface_line(self):
        """Return the the parent line for the interface configuration"""
        return f"interface {self.interface.interface_type.value}{self.interface.interface_number}{'' if self.interface.subinterface_number is None else '.' + str(self.interface.subinterface_number)}"

    def to_config_lines(self):
        """
        Render the interface configuration as Cisco-style CLI lines.
        """
        lines = [self.interface_line()]
        if self.description is not None:
            lines.append(f" description {self.description}")
        if self.vrf is not None:
            lines.append(f" vrf forwarding {self.vrf}")
        if self.ip_address is not None:
            lines.append(
                f" ip address {str(self.ip_address.ip)} {str(self.ip_address.netmask)}"
            )
        elif self.dhcp_assigned:
            lines.append(" ip address dhcp")
        for ip in self.secondary_ip_addresses:
            lines.append(f" ip address {ip.ip} {ip.netmask} secondary")
        if self.shutdown is not None:
            lines.append(f" {'no ' if not self.shutdown else ''}shutdown")
        lines.append("!")
        return lines

    def interface_string(self) -> str:
        return f"interface {self.interface.interface_type.value}{self.interface.interface_number}"

    def description_string(self) -> str:
        return f"description {self.description}" if self.description else ""

    def vrf_string(self) -> str:
        return f"vrf forwarding {self.vrf}" if self.vrf else ""

    def ip_string(self) -> str:
        if self.dhcp_assigned:
            return "ip address dhcp"
        if self.ip_address:
            return f"ip address {self.ip_address.ip} {self.ip_address.netmask}"
        return ""

    def secondary_ip_strings(self) -> list[str]:
        strings = []
        if self.secondary_ip_addresses:
            for ip in self.secondary_ip_addresses:
                strings.append(f"ip address {ip.ip} {ip.netmask} secondary")
        return strings

    def shutdown_string(self) -> str:
        if self.shutdown is None:
            return ""
        else:
            return f"{'no ' if not self.shutdown else ''}shutdown"
