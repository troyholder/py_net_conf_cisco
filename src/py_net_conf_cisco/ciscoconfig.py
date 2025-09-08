from copy import copy
from ipaddress import IPv4Address, IPv4Interface, IPv6Address
from pathlib import Path
from typing import List, Optional, Union

from ciscoconfparse2 import BaseCfgLine, CiscoConfParse

from .interfaceconfig import Interface, InterfaceConfig, InterfaceType
from .loggingconfig import LoggingConfig, loggingconfig_from_config_lines
from .radiusserverconfig import RadiusServerConfig
from .tacacsgroupconfig import (
    TacacsServerGroupConfig,
    TacacsServerPrivateConfig,
)
from .tacacsserverconfig import TacacsServerConfig
from .vrfconfig import VRFConfig, vrf_from_config_lines


class CiscoConfig:
    def __init__(
        self,
        config_path: Optional[Union[str, Path]] = None,
        config_text: Optional[str] = None,
    ):
        self._hostname = None
        self._hostname_line = None
        if config_path is None and config_text is None:
            raise ValueError(
                "Either config_path or config_text must be provided"
            )

        if config_text is not None:
            config_lines = config_text.splitlines()
            self._parsed_config = CiscoConfParse(config_lines)
        else:
            self._parsed_config = CiscoConfParse(str(config_path))

    def get_text(self) -> List[str]:
        """Return the configuration as a string."""
        return self._parsed_config.get_text()

    def _last_line(self) -> BaseCfgLine:
        end_lines = self._parsed_config.find_objects(r"^end$")
        if end_lines:
            return self._parsed_config.config_objs[end_lines[0].index - 1]
        else:
            return self._parsed_config.config_objs[-1]

    @property
    def hostname(self) -> str:
        if self._hostname is None:
            hostname_objs = self._parsed_config.find_objects(r"^hostname\s+")
            if hostname_objs:
                self._hostname_line = hostname_objs[0]
                self._hostname = self._hostname_line.text.split()[1]
            else:
                self._hostname = ""
        return self._hostname

    @hostname.setter
    def hostname(self, value: str) -> None:
        self._hostname = value
        if self._hostname_line:
            self._hostname_line.text = f"hostname {value}"
        else:
            version_objs = self._parsed_config.find_objects(r"^version\s+")
            if version_objs:
                version_objs[0].insert_after(f"hostname {value}")
            else:
                if self._parsed_config.objs:
                    self._parsed_config.objs[0].insert_before(
                        f"hostname {value}"
                    )
                else:
                    self._parsed_config = CiscoConfParse([f"hostname {value}"])

    def _parse_interface_from_string(self, interface_string: str) -> Interface:
        for interface_type in InterfaceType:
            if interface_string.startswith(interface_type.value):
                interface_number = interface_string[len(interface_type.value) :]
                return Interface(
                    interface_type=interface_type,
                    interface_number=interface_number,
                )
        raise ValueError(
            f"Could not parse interface string: {interface_string}"
        )

    def _unexpected_config_line(self, line):
        raise ValueError(f"Unexpected config line: {line.text}")

    def _find_interface_lines(self, interface: InterfaceConfig):
        interface_text = interface.interface_line()
        return self._parsed_config.find_objects(r"^" + interface_text + r"$")

    def get_interface(
        self, interface: InterfaceConfig
    ) -> InterfaceConfig | None:
        """Return an InterfaceConfig object of the interface configuration"""
        found = InterfaceConfig(
            copy(interface.interface),
        )
        interface_lines = self._find_interface_lines(interface)
        if len(interface_lines) == 0:
            return None
        elif len(interface_lines) == 1:
            for line in interface_lines[0].children:
                line_split = line.text.split()
                # Handle lines starting with " ip address"
                if line.re_search(r"\s+ip\s+address\s"):
                    if line_split[2] == "dhcp":
                        found.dhcp_assigned = True
                    elif len(line_split) == 4:
                        found.dhcp_assigned = False
                        found.ip_address = IPv4Interface(
                            f"{line_split[2]}/{line_split[3]}"
                        )
                    elif len(line_split) == 5:
                        if line_split[4] == "secondary":
                            found.secondary_ip_addresses.append(
                                IPv4Interface(
                                    f"{line_split[2]}/{line_split[3]}"
                                )
                            )
                        else:
                            self._unexpected_config_line(line)
                    else:
                        self._unexpected_config_line(line)
                elif line.re_search(r"description\s+(\S.+)"):
                    found.description = " ".join(line_split[1:])
                elif line.re_search(r"^\s+shutdown"):
                    found.shutdown = True
                elif line.re_search(r"^\s+no shutdown"):
                    found.shutdown = False
                elif line.re_search(r"^\s+vrf forwarding"):
                    found.vrf = line_split[2]
                elif line.re_search(r"^\s+!.*"):
                    # Ignore lines that have been commented out
                    continue
                else:
                    self._unexpected_config_line(line)
        else:
            raise ValueError("Found multiple interfaces")
        return found

    def _add_interface_config_after_line(
        self, line: BaseCfgLine, interface: InterfaceConfig
    ) -> None:
        # Shutdown
        if interface.shutdown is not None:
            line.insert_after(" " + interface.shutdown_string())
        # Secondary IPs
        if interface.secondary_ip_addresses:
            for secondary_ip in interface.secondary_ip_strings()[::-1]:
                line.insert_after(" " + secondary_ip)
        # IP
        if interface.ip_address:
            line.insert_after(" " + interface.ip_string())
        # VRF
        if interface.vrf:
            line.insert_after(" " + interface.vrf_string())
        # Description
        if interface.description:
            line.insert_after(" " + interface.description_string())

    def set_interface(self, interface: InterfaceConfig) -> bool:
        interface_lines = self._find_interface_lines(interface)
        if len(interface_lines) == 0:
            interfaces = self._parsed_config.find_objects(r"^interface")
            first_interface = interfaces[0]
            first_interface.insert_before(interface.interface_string())
            self._parsed_config.commit()
            lines = self._parsed_config.find_objects(
                interface.interface_string()
            )
            self._add_interface_config_after_line(lines[0], interface)
            self._parsed_config.commit()
            return True

        interface_line = interface_lines[0]
        secondary_lines_replaced = 0
        secondary_lines_found = 0
        new_secondary_lines = len(interface.secondary_ip_addresses)
        last_found_secondary_line = None
        primary_ip_line = None

        if len(interface_lines) == 1:
            if not interface_line.has_children:
                self._add_interface_config_after_line(interface_line, interface)
                self._parsed_config.commit()
                return True
            else:
                for line in interface_line.children:
                    line_split = line.text.split()
                    # Handle lines starting with " ip address"
                    if line.re_search(r"\s+ip\s+address\s"):
                        primary_ip_line = line
                        if (
                            line_split[2] == "dhcp"
                            and interface.ip_address is not None
                        ):
                            if interface.dhcp_assigned is False:
                                line.re_sub(
                                    r"\S.*",
                                    interface.ip_string(),
                                )
                        elif len(line_split) == 4:
                            if interface.dhcp_assigned is True:
                                line.re_sub(r"\S.*", interface.ip_string())
                            elif interface.ip_address is not None:
                                if line_split[2] != str(
                                    interface.ip_address.ip
                                ) or line_split[3] != str(
                                    interface.ip_address.netmask
                                ):
                                    line.re_sub(
                                        r"\S.*",
                                        interface.ip_string(),
                                    )
                        elif len(line_split) == 5:
                            if line_split[4] == "secondary":
                                last_found_secondary_line = line
                                secondary_lines_found += 1
                                # No secondary IPs wanted
                                if any(
                                    [
                                        new_secondary_lines == 0,
                                        secondary_lines_found
                                        > new_secondary_lines,
                                    ]
                                ):
                                    line.re_sub(r"ip address.*", "!")
                                # Changing a secondary IP address
                                if (
                                    secondary_lines_replaced
                                    < new_secondary_lines
                                ):
                                    line.re_sub(
                                        r"\S.*",
                                        interface.secondary_ip_strings()[
                                            secondary_lines_replaced
                                        ],
                                    )
                                secondary_lines_replaced += 1
                            else:
                                self._unexpected_config_line(line)
                        else:
                            self._unexpected_config_line(line)

                    elif line.re_search(r"description\s+(\S.+)"):
                        if interface.description is None:
                            line.re_sub(
                                r"description.*",
                                "!",
                            )
                        else:
                            line.re_sub(
                                r"description.*",
                                interface.description_string(),
                            )
                    elif line.re_search(r"^\s+shutdown"):
                        if interface.shutdown is False:
                            line.re_sub(r"\S.*", interface.shutdown_string())
                    elif line.re_search(r"^\s+no shutdown"):
                        if interface.shutdown is True:
                            line.re_sub(r"\S.*", interface.shutdown_string())
                    elif line.re_search(r"^\s+vrf forwarding"):
                        if interface.vrf != line_split[2]:
                            line.re_sub(r"vrf.*", interface.vrf_string())
                    elif line.re_search(r"^\s+!.*"):
                        # Ignore lines that have been commented out
                        continue
                    else:
                        self._unexpected_config_line(line)
        else:
            raise ValueError("Found multiple interfaces")

        if secondary_lines_replaced < new_secondary_lines:
            additional_secondary_lines = None
            if last_found_secondary_line is None:
                # Handle not finding any secondary IPs
                if primary_ip_line:
                    additional_secondary_lines = primary_ip_line
                else:
                    raise ValueError(
                        "Trying to add secondary IP with no primary IP"
                    )
            else:
                additional_secondary_lines = last_found_secondary_line

            while secondary_lines_replaced < new_secondary_lines:
                spacing = additional_secondary_lines.re_match(r"^(\s+)")
                additional_secondary_lines.insert_after(
                    f"{spacing}{interface.secondary_ip_strings()[secondary_lines_replaced]}"
                )
                secondary_lines_replaced += 1

        self._parsed_config.commit()
        return True

    def _find_radius_server_lines(self) -> list[BaseCfgLine]:
        return self._parsed_config.find_objects(r"^radius server ")

    @property
    def last_config_line(self) -> BaseCfgLine:
        end_lines = self._parsed_config.find_objects(r"^end$")
        if len(end_lines) > 0:
            return end_lines[-1]
        else:
            return self._parsed_config.objs[-1]

    @property
    def radius_servers(self) -> list[RadiusServerConfig]:
        found = []
        server_lines = self._find_radius_server_lines()
        for line in server_lines:
            address_line = line.re_search_children(r"^ address ipv[4|6]")[0]
            key_line = line.re_search_children(r"^ key")[0]
            name = line.re_match(r"^radius server (\S+)")
            if "ipv4" in address_line:
                ip_address = IPv4Address(
                    address_line.re_match(r"address ipv4 (\S+)")
                )
            else:
                ip_address = IPv6Address(
                    address_line.re_match(r"address ipv4 (\S+)")
                )
            auth_port = address_line.re_match(
                r"auth-port (\S+)", default="1812"
            )
            acct_port = address_line.re_match(
                r"acct-port (\S+)", default="1813"
            )
            key = key_line.re_match(r"^ key \d (\S+)")
            found.append(
                RadiusServerConfig(
                    ip_address=ip_address,
                    name=name,
                    key=key,
                    auth_port=int(auth_port),
                    acct_port=int(acct_port),
                )
            )

        return found

    @radius_servers.setter
    def radius_servers(self, new_servers: list[RadiusServerConfig]) -> None:
        current_servers = self._find_radius_server_lines()
        current_server_count = len(current_servers)
        new_server_count = len(new_servers)
        if current_server_count == 0 and new_server_count == 0:
            return

        if current_server_count == 0:
            add_before_line = self.last_config_line
        else:
            last_current_radius_line = current_servers[-1].children[-1]
            index = self._parsed_config.objs.index(last_current_radius_line)
            add_before_line = self._parsed_config.objs[index + 1]

        for new_server in new_servers[::-1]:
            for line in new_server.to_config_lines()[::-1]:
                self._parsed_config.objs.insert(add_before_line.index, line)
                self._parsed_config.commit()

        if current_server_count > 0:
            for current_server in current_servers[::-1]:
                current_server_line = self._parsed_config.find_objects(
                    current_server.text
                )
                current_server_line[0].delete()
                self._parsed_config.commit()

    def _logging_server_lines(self):
        return self._parsed_config.find_objects(r"^logging ")

    @property
    def logging_servers(self) -> List[LoggingConfig]:
        found = []
        server_lines = self._logging_server_lines()
        for line in server_lines:
            parts = line.text.split()
            for index, word in enumerate(parts):
                # For now ignoring all lines that do not start with "logging host"
                if index < 3:
                    continue
                elif index == 3:
                    continue
            found.append(loggingconfig_from_config_lines([line.text]))

        return found

    @logging_servers.setter
    def logging_servers(self, new_servers: List[LoggingConfig]) -> None:
        current_servers = self._logging_server_lines()
        current_server_count = len(current_servers)
        new_server_count = len(new_servers)
        if current_server_count == 0 and new_server_count == 0:
            return
        add_after_line = self.last_config_line
        last_index = add_after_line.index

        if current_server_count > 0:
            last_index = current_servers[0].index
            for line in current_servers[::-1]:
                line.delete()
                self._parsed_config.commit()

        for new_server in new_servers[::-1]:
            for new_server_line in new_server.to_config_lines()[::-1]:
                self._parsed_config.config_objs.insert(
                    index=last_index,
                    item=new_server_line,
                )
                self._parsed_config.commit()

    def _find_tacacs_server_lines(self) -> list[BaseCfgLine]:
        return self._parsed_config.find_objects(
            r"^tacacs(-server host| server) "
        )

    def _find_tacacs_group_lines(self) -> list[BaseCfgLine]:
        return self._parsed_config.find_objects(r"^aaa group server tacacs\+")

    @property
    def tacacs_group(self) -> list[TacacsServerGroupConfig]:
        found = []
        group_lines = self._find_tacacs_group_lines()
        for line in group_lines:
            name = line.text.split()[-1]
            vrf = None
            source_interface = None
            server_private_list = []
            for child in line.children:
                if child.text.strip().startswith("server-private"):
                    parts = child.text.strip().split()
                    ip_address = IPv4Address(parts[1])
                    key_mode = None
                    key = None
                    if len(parts) > 2:
                        if parts[2] == "key":
                            if len(parts) > 3:
                                if parts[3].isdigit():
                                    key_mode = int(parts[3])
                                    if len(parts) > 4:
                                        key = parts[4]
                                else:
                                    key = parts[3]
                        elif parts[2].isdigit():
                            key_mode = int(parts[2])
                            if len(parts) > 3:
                                key = parts[3]
                        else:
                            key = parts[2]
                    server_private_list.append(
                        TacacsServerPrivateConfig(
                            ip_address=ip_address,
                            key_mode=key_mode,
                            key=key,
                        )
                    )
                elif child.text.strip().startswith("ip vrf forwarding"):
                    vrf = child.text.strip().split()[-1]
                elif child.text.strip().startswith(
                    "ip tacacs source-interface"
                ):
                    source_interface = self._parse_interface_from_string(
                        child.text.strip().split()[-1]
                    )
            found.append(
                TacacsServerGroupConfig(
                    name=name,
                    vrf=vrf,
                    source_interface=source_interface,
                    server_private_list=server_private_list,
                )
            )
        return found

    @tacacs_group.setter
    def tacacs_group(self, new_groups: list[TacacsServerGroupConfig]) -> None:
        current_groups = self._find_tacacs_group_lines()
        current_group_count = len(current_groups)
        new_group_count = len(new_groups)
        if current_group_count == 0 and new_group_count == 0:
            return

        if current_group_count > 0:
            for current_group in current_groups[::-1]:
                current_group.delete()
                self._parsed_config.commit()

        if new_group_count > 0:
            if current_group_count == 0:
                add_before_line = self.last_config_line
            else:
                add_before_line = current_groups[-1]

            for new_group in new_groups[::-1]:
                for line in new_group.to_config_lines()[::-1]:
                    self._parsed_config.objs.insert(add_before_line.index, line)
                    self._parsed_config.commit()

    @property
    def tacacs_servers(self) -> list[TacacsServerConfig]:
        found = []
        server_lines = self._find_tacacs_server_lines()
        for line in server_lines:
            parts = line.text.strip().split()
            if parts[1] == "host":
                ip_address = IPv4Address(parts[2])
                encrpyted_string = ""
                if len(parts) > 3:
                    if parts[3] == "key":
                        encrpyted_string = parts[4]
            else:
                ip_address = IPv4Address(parts[2])
                encrpyted_string = ""
                key_line = line.re_search_children(r"^ key")
                if key_line:
                    key_parts = key_line[0].text.strip().split()
                    if len(key_parts) > 2:
                        encrpyted_string = key_parts[2]

            found.append(
                TacacsServerConfig(
                    ip_address=ip_address,
                    encrpyted_string=encrpyted_string,
                )
            )
        return found

    @tacacs_servers.setter
    def tacacs_servers(self, new_servers: list[TacacsServerConfig]) -> None:
        current_servers = self._find_tacacs_server_lines()
        current_server_count = len(current_servers)
        new_server_count = len(new_servers)
        if current_server_count == 0 and new_server_count == 0:
            return

        if current_server_count == 0:
            add_before_line = self.last_config_line
        else:
            last_current_radius_line = current_servers[-1]
            index = self._parsed_config.objs.index(last_current_radius_line)
            add_before_line = self._parsed_config.objs[index + 1]

        for new_server in new_servers[::-1]:
            for line in new_server.to_config_lines()[::-1]:
                self._parsed_config.objs.insert(add_before_line.index, line)
                self._parsed_config.commit()

        if current_server_count > 0:
            for current_server in current_servers[::-1]:
                current_server_line = self._parsed_config.find_objects(
                    current_server.text
                )
                current_server_line[0].delete()
                self._parsed_config.commit()

    def _find_vrf_lines(self) -> list[BaseCfgLine]:
        return self._parsed_config.find_objects(r"^vrf definition ")

    @property
    def vrfs(self) -> list[VRFConfig]:
        found = []
        vrf_lines = self._find_vrf_lines()
        for line in vrf_lines:
            print(line.text)
            found.append(vrf_from_config_lines([line.text] + line.children))
        return found

    @vrfs.setter
    def vrfs(self, new_vrfs: list[VRFConfig]) -> None:
        current_vrfs = self._find_vrf_lines()
        current_vrf_count = len(current_vrfs)
        new_vrf_count = len(new_vrfs)
        if current_vrf_count == 0 and new_vrf_count == 0:
            return

        if current_vrf_count == 0:
            add_before_line = self.last_config_line
        else:
            last_current_vrf_line = current_vrfs[-1]
            # Find the last child of the last VRF or the VRF line itself
            if last_current_vrf_line.children:
                last_vrf_child = last_current_vrf_line.children[-1]
                index = self._parsed_config.objs.index(last_vrf_child)
            else:
                index = self._parsed_config.objs.index(last_current_vrf_line)
            add_before_line = self._parsed_config.objs[index + 1]

        for new_vrf in new_vrfs[::-1]:
            for line in new_vrf.to_config_lines()[::-1]:
                self._parsed_config.objs.insert(add_before_line.index, line)
                self._parsed_config.commit()

        if current_vrf_count > 0:
            for current_vrf in current_vrfs[::-1]:
                current_vrf.delete()
                self._parsed_config.commit()

    def has_vrf(self, vrf_name: str) -> bool:
        return any(vrf.name == vrf_name for vrf in self.vrfs)
