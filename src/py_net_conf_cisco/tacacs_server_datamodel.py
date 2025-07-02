"""
Data models for Cisco tacacs server configuration options.

This module provides dataclasses and enums for structuring tacacs server configuration options.
"""

from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address


@dataclass
class TacacsServerConfig:
    """
    Represents a tacacs server configuration.

    Attributes:
            ip_address: IP address (ipaddress.IPv4Address|ipaddress.IPv6Address).
            encrpyted_string: Encryption key.
    """

    ip_address: IPv4Address | IPv6Address
    encrpyted_string: str

    def __post_init__(self):
        if not isinstance(self.ip_address, (IPv4Address, IPv6Address)):
            raise TypeError(
                "ip_address must be an IPv4Address or IPv6Address instance"
            )
        if not isinstance(self.encrpyted_string, str):
            raise TypeError("encrpyted_string must be a string")
