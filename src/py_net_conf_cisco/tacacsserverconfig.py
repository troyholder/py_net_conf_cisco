"""
Data models for Cisco tacacs server configuration options.

This module provides dataclasses and enums for structuring tacacs server configuration options.

"""

from dataclasses import dataclass
from ipaddress import IPv4Address, IPv6Address
from typing import List, Optional, Union

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

    def to_config_lines(self) -> List[str]:
        return [
            f"tacacs-server host {self.ip_address} key {self.encrpyted_string}",
        ]


# f"tacacs-server host {vars.server_1_ipv4_address} key {vars.encrpyted_string_1}"
def tacas_server_from_config_lines(
    lines: List[str],
) -> Optional[TacacsServerConfig]:
    """
    Parse TACACS server configuration lines and return a TacacsServerConfig object.

    Args:
        lines: List of configuration lines

    Returns:
        TacacsServerConfig object if parsing successful, None otherwise
    """
    if not lines:
        return None

    # Find the TACACS server definition line
    tacacs_server_line = None
    key_line = None
    ip_address = IPv4Address("0.0.0.0")
    encrpyted_string = ""
    for line in lines:
        parts = line.strip().split()

        if tacacs_server_line and line.strip().startswith("tacacs-server "):
            raise ValueError("Multiple TACACS server definitions found")

        if line.strip().startswith("tacacs-server "):
            tacacs_server_line = line
            if parts[1] == "host":
                ip_address = IPv4Address(parts[2])
                if len(parts) > 3:
                    if parts[3] == "key":
                        encrpyted_string = parts[4]
                else:
                    ip_address = IPv4Address(parts[2])

        if key_line and line.strip().startswith(" key"):
            raise ValueError("Multiple TACACS server definitions found")

        if line.strip().startswith(" key"):
            key_line = line
            if len(parts) > 2:
                encrpyted_string = parts[2]

    if not tacacs_server_line:
        return None

    return TacacsServerConfig(
        ip_address=ip_address,
        encrpyted_string=encrpyted_string,
    )
