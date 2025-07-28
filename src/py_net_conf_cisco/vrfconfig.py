"""
Data model for Cisco VRF configuration options.
"""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class VRFConfig:
    """
    Represents a VRF configuration.

    Attributes:
            name: Required VRF name
            rd: Optional router distinguisher
            address_family_ipv4_exports: List of target VPN extended community strings
            address_family_ipv4_imports: List of target VPN extended community strings
    """

    name: str
    rd: Optional[str] = None
    address_family_ipv4_exports: List[str] = field(default_factory=list)
    address_family_ipv4_imports: List[str] = field(default_factory=list)

    def to_config_lines(self):
        lines = [
            f"vrf definition {self.name}",
        ]
        if self.rd is not None:
            lines.append(f" rd {self.rd}")

        if any(
            [self.address_family_ipv4_exports, self.address_family_ipv4_imports]
        ):
            lines.append(" !")
            lines.append(" address-family ipv4")
            for export in self.address_family_ipv4_exports:
                lines.append(f"  route-target export {export}")

            for export in self.address_family_ipv4_imports:
                lines.append(f"  route-target import {export}")
            lines.append(" exit-address-family")

        return lines
