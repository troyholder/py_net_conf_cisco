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

from dataclasses import dataclass, field
from ipaddress import IPv4Address, IPv6Address
from typing import List, Optional, Union

from .interfaceconfig import Interface

_KEY_MODES: List[Union[int, None]] = [0, 6, 7, None]


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
class TacacsServerPrivateConfig:
    """
    Represents a tacacs group's server-private configuration.

    Attributes:
            ip_address: IP address (ipaddress.IPv4Address|ipaddress.IPv6Address).
            encrpyted_string: Encryption key.
    """

    ip_address: Optional[IPv4Address | IPv6Address] = None
    fqdn: Optional[str] = None
    key_mode: Optional[int] = None
    key: Optional[str] = None

    def __post_init__(self):
        if self.ip_address is None and self.fqdn is None:
            raise TypeError("ip_address or fqdn must be given")
        if self.ip_address is not None and not isinstance(
            self.ip_address, (IPv4Address, IPv6Address)
        ):
            raise TypeError(
                "ip_address must be an IPv4Address or IPv6Address instance"
            )
        if self.fqdn is not None and not isinstance(self.fqdn, str):
            raise TypeError("fqdn must be a string")
        if self.ip_address is not None and self.fqdn is not None:
            raise TypeError("must not set ip_address and fqdn")
        if self.key_mode not in _KEY_MODES:
            raise TypeError("key_mode must be 0, 6, 7, or None")
        if self.key is not None and not isinstance(self.key, str):
            raise TypeError(
                "key must be a string that does not start with a space"
            )
        if self.key is not None and self.key[0] == " ":
            raise TypeError(
                "key must not start with spaces to avoid possible issues"
            )

    def to_config_lines(self):
        line = " server-private "
        if self.ip_address:
            line += str(self.ip_address)
        else:
            line += "fqdn " + str(self.fqdn)
        if isinstance(self.key_mode, int):
            line += " " + str(self.key_mode)
        if isinstance(self.key, str):
            line += " " + self.key

        return [line]


@dataclass
class TacacsServerGroupConfig:
    name: str
    vrf: Optional[str] = None
    source_interface: Optional[Interface] = None
    server_private_list: List[Union[TacacsServerPrivateConfig, None]] = field(
        default_factory=list
    )

    def __post_init__(self):
        if self.name is not None and not isinstance(self.name, str):
            raise TypeError("name must be a string")
        if self.vrf is not None and not isinstance(self.vrf, str):
            raise TypeError("vrf must be a string")
        if self.source_interface is not None and not isinstance(
            self.source_interface, Interface
        ):
            raise TypeError("source_interface must be an Interface")
        if not isinstance(self.server_private_list, list) or not all(
            isinstance(server, TacacsServerPrivateConfig)
            for server in self.server_private_list
        ):
            raise TypeError(
                "server_private_list must either be an empty list or list "
                + "of TacacsServerPrivateConfig objects"
            )

    def to_config_lines(self) -> List[str]:
        lines = [f"aaa group server tacacs+ {self.name}"]
        if self.server_private_list:
            for server in self.server_private_list:
                if server is not None:
                    lines += server.to_config_lines()
        if self.vrf:
            lines.append(f" ip vrf forwarding {self.vrf}")
        if self.source_interface:
            lines.append(
                f" ip tacacs source-interface {str(self.source_interface)}"
            )
        return lines
