"""
Data models for Cisco tacacs server configuration options.

This module provides dataclasses and enums for structuring tacacs server configuration options.

As of 17.9.5 the option tree looks like:
    aaa group server tacacs+ <group-name>
    ├── accounting
    │   └── acknowledge
    │       └── broadcast
    ├── cache
    │   ├── authentication
    │   │   └── profile <profile-name>
    │   ├── authorization
    │   │   └── profile <profile-name>
    │   └── expiry <seconds>
    │       ├── enforce
    │       │   ├── hours
    │       │   └── minutes
    │       ├── failover
    │       │   ├── hours
    │       │   └── minutes
    │       ├── hours
    │       └── minutes
    ├── dns-alias-lookup
    ├── host <ip-address|hostname>
    ├── ip
    │   ├── tacacs
    │   │   └── source-interface <interface-type> <interface-number>
    │   └── vrf
    │       └── forwarding <vrf-name>
    ├── ipv6
    │   └── tacacs
    │       └── source-interface <ipv6-interface-type> <ipv6-interface-number>
    ├── pick-method
    │   ├── least-used
    │   ├── ordered
    │   └── round-robin
    ├── server
    │   ├── <ip-address|hostname>
    │   └── name <server-name>
    ├── server-private
    │   ├── <ip-address|hostname>
    │   ├── <ipv6-address>
    │   ├── fqdn
    │   └── <server-address-chosen-above>
    │       ├── key (...)
    │       ├── nat
    │       │   ├── key (...)
    │       │   ├── port <1-65535>
    │       │   │   ├── key (...)
    │       │   │   └── timeout <1-1000>
    │       │   │       └── key (...)
    │       │   ├── single-connection
    │       │   │   ├── key (...)
    │       │   │   ├── port <1-65535>
    │       │   │   │   ├── key (...)
    │       │   │   │   └── timeout <1-1000>
    │       │   │   │       └── key (...)
    │       │   │   └── timeout <1-1000>
    │       │   │       └── key (...)
    │       │   └── timeout <1-1000>
    │       │       └── key (...)
    │       ├── port <1-65535>
    │       │   ├── key (...)
    │       │   └── timeout <1-1000>
    │       │       └── key (...)
    │       ├── single-connection
    │       │   ├── key (...)
    │       │   ├── port <1-65535>
    │       │   │   ├── key (...)
    │       │   │   └── timeout <1-1000>
    │       │   │       └── key (...)
    │       │   └── timeout <1-1000>
    │       │       └── key (...)
    │       └── timeout <1-1000>
    │           └── key (...)
    └── timeout <seconds>
"""

from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address
from typing import List, Optional

from .interface_datamodel import Interface


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
    name: str
    vrf: Optional[str] = None
    source_interface: Optional[Interface] = None

    def __post_init__(self):
        pass

    def to_config_lines(self) -> List[str]:
        lines = [f"aaa group server tacacs+ {self.name}"]
        if self.vrf:
            lines.append(f" ip vrf forwarding {self.vrf}")
        if self.source_interface:
            lines.append(
                f" ip tacacs source-interface {str(self.source_interface)}"
            )
        return lines
