"""
Data models for Cisco tacacs server configuration options.

This module provides dataclasses and enums for structuring tacacs server configuration options.
"""

import collections
from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address
from typing import Optional


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


@dataclass
class TacacsServerGroupConfig:
    group_name: str
    servers: list[TacacsServerConfig]
    vrf: Optional[str] = None
    interface: Optional[str] = None

    def __post_init__(self):
        if len(self.servers) == 0:
            raise TypeError("servers must be a non-empty list")
        for index, server in enumerate(self.servers):
            if type(server) is not TacacsServerConfig:
                raise TypeError(
                    f"server at {str(index)} of servers is not a TacacsServerGroupConfig"
                )
        duplicates = [
            server_ip
            for server_ip, count in collections.Counter(
                str(server.ip_address) for server in self.servers
            ).items()
            if count > 1
        ]
        raise TypeError(
            f"duplicate servers in servers list: {', '.join(duplicates)}"
        )
