"""
Data models for Cisco logging server configuration options.

This module provides dataclasses and enums for structuring logging server configuration options.
"""

from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address
from typing import List, Optional


@dataclass
class LoggingConfig:
    """
    Represents a logging server configuration.

    This module is only built out for what is needed at this time. Lots of options and checks will need to be added.


    Attributes:
            syslog_ip_address: IPv4 or IPv6 address (ipaddress.IPv4Address | ipaddress.IPv6Address).
            syslog_fqdn: Name of the server.
    """

    syslog_ip_address: Optional[IPv4Address | IPv6Address] = None
    syslog_fqdn: Optional[str] = ""
    vrf: Optional[str] = ""

    def __post_init__(self):
        if not self.syslog_ip_address and not self.syslog_fqdn:
            raise TypeError(
                "At least one of syslog_ip_address or syslog_fqdn must be set."
            )
        if self.syslog_ip_address is not None and not isinstance(
            self.syslog_ip_address, (IPv4Address, IPv6Address)
        ):
            raise TypeError(
                "syslog_ip_address must be an IPv4Address or IPv6Address."
            )
        if not isinstance(self.syslog_fqdn, str):
            raise TypeError("syslog_fqdn must be a string.")
        if self.syslog_ip_address and self.syslog_fqdn:
            raise ValueError(
                "Only one of syslog_ip_address or syslog_fqdn can be set."
            )
        if not isinstance(self.vrf, str):
            raise TypeError("vrf must be a string.")

    def to_config_lines(self) -> List[str]:
        config = ""
        if self.syslog_ip_address:
            config += f"logging host {self.syslog_ip_address}"
        elif self.syslog_fqdn:
            config += f"logging host fqdn {self.syslog_fqdn}"
        if self.vrf:
            config += f" vrf {self.vrf}"
        return [config]
