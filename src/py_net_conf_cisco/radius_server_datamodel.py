"""
Data models for Cisco radius server configuration options.

This module provides dataclasses and enums for structuring radius server configuration options.
"""

from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address
from typing import Optional


@dataclass
class RadiusServerConfig:
    """
    Represents a radius server configuration.

    Attributes:
            ip_address: IPv4 address (ipaddress.IPv4Address).
            name: Name of the server.
            key: Encrypted key.
            auth_port: Integer for the port that auth requests are sent. Defaults to 1812
            acct_port: Integer for the port that auth requests are sent. Defaults to 1813
    """

    ip_address: IPv4Address | IPv6Address
    name: str
    key: str
    auth_port: Optional[int] = 1812
    acct_port: Optional[int] = 1813

    def to_config_lines(self):
        lines = [
            f"radius server {self.name}",
            f" address ipv4 {self.ip_address}"
            + f"{' auth-port ' + str(self.auth_port) if self.auth_port != 1812 else ''}"
            + f"{' acct-port ' + str(self.acct_port) if self.acct_port != 1813 else ''}",
            f" key 7 {self.key}",
        ]
        return lines
