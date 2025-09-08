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


def vrf_from_config_lines(lines: List[str]) -> Optional[VRFConfig]:
    """
    Parse VRF configuration lines and return a VRFConfig object.

    Args:
        lines: List of configuration lines

    Returns:
        VRFConfig object if parsing successful, None otherwise
    """
    if not lines:
        return None

    # Find the VRF definition line
    vrf_line = None
    for line in lines:
        if line.strip().startswith("vrf definition "):
            vrf_line = line
            break

    if not vrf_line:
        return None

    # Extract VRF name
    name = vrf_line.strip().split()[-1]
    rd = None
    address_family_ipv4_exports = []
    address_family_ipv4_imports = []

    # Parse the configuration lines
    in_address_family = False
    for line in lines:
        stripped_line = line.strip()

        if stripped_line.startswith("rd "):
            rd = stripped_line.split("rd ", 1)[1]
        elif stripped_line == "address-family ipv4":
            in_address_family = True
        elif stripped_line == "exit-address-family":
            in_address_family = False
        elif in_address_family and stripped_line.startswith(
            "route-target export "
        ):
            target = stripped_line.split()[-1]
            address_family_ipv4_exports.append(target)
        elif in_address_family and stripped_line.startswith(
            "route-target import "
        ):
            target = stripped_line.split()[-1]
            address_family_ipv4_imports.append(target)

    return VRFConfig(
        name=name,
        rd=rd,
        address_family_ipv4_exports=address_family_ipv4_exports,
        address_family_ipv4_imports=address_family_ipv4_imports,
    )
