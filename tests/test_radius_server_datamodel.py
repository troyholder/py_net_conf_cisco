"""
Test suite for the radius server datamodels.
"""

from ipaddress import IPv4Address, IPv6Address

import pytest

from py_net_conf_cisco.radiusserverconfig import RadiusServerConfig


class TestRadiusServerConfig:
    """Test class for the RadiusServerConfig dataclass."""

    ipv4 = IPv4Address("1.1.1.1")
    ipv6 = IPv6Address("2001:db8::1")

    failing_cases = [
        ({}),
        (
            {
                "auth_port": 123,
            }
        ),
        (
            {
                "acct_port": 456,
            }
        ),
        (
            {
                "auth_port": 123,
                "acct_port": 456,
            }
        ),
        (
            {
                "ip_address": ipv4,
                "auth_port": 123,
            }
        ),
        (
            {
                "ip_address": ipv4,
                "acct_port": 456,
            }
        ),
        (
            {
                "ip_address": ipv4,
                "auth_port": 123,
                "acct_port": 456,
            }
        ),
        (
            {
                "ip_address": ipv6,
                "auth_port": 123,
            }
        ),
        (
            {
                "ip_address": ipv6,
                "acct_port": 456,
            }
        ),
        (
            {
                "ip_address": ipv6,
                "auth_port": 123,
                "acct_port": 456,
            }
        ),
        (
            {
                "name": "foo",
                "auth_port": 123,
            }
        ),
        (
            {
                "name": "foo",
                "acct_port": 456,
            }
        ),
        (
            {
                "name": "foo",
                "auth_port": 123,
                "acct_port": 456,
            }
        ),
        (
            {
                "name": "foo",
                "auth_port": 123,
            }
        ),
        (
            {
                "name": "foo",
                "acct_port": 456,
            }
        ),
        (
            {
                "name": "foo",
                "auth_port": 123,
                "acct_port": 456,
            }
        ),
        (
            {
                "auth_port": 123,
                "key": "encrpted_string",
            }
        ),
        (
            {
                "acct_port": 456,
                "key": "encrpted_string",
            }
        ),
        (
            {
                "auth_port": 123,
                "acct_port": 456,
                "key": "encrypted_string",
            }
        ),
        (
            {
                "ip_address": ipv4,
                "auth_port": 123,
                "key": "encrypted_string",
            }
        ),
        (
            {
                "ip_address": ipv4,
                "acct_port": 456,
                "key": "encrypted_string",
            }
        ),
        (
            {
                "ip_address": ipv4,
                "auth_port": 123,
                "acct_port": 456,
                "key": "encrypted_string",
            }
        ),
        (
            {
                "ip_address": ipv6,
                "auth_port": 123,
                "key": "encrypted_string",
            }
        ),
        (
            {
                "ip_address": ipv6,
                "acct_port": 456,
                "key": "encrypted_string",
            }
        ),
        (
            {
                "ip_address": ipv6,
                "auth_port": 123,
                "acct_port": 456,
                "key": "encrypted_string",
            }
        ),
        (
            {
                "name": "foo",
                "auth_port": 123,
                "key": "encrypted_string",
            }
        ),
        (
            {
                "name": "foo",
                "acct_port": 456,
                "key": "encrypted_string",
            }
        ),
        (
            {
                "name": "foo",
                "auth_port": 123,
                "acct_port": 456,
                "key": "encrypted_string",
            }
        ),
        (
            {
                "name": "foo",
                "auth_port": 123,
                "key": "encrypted_string",
            }
        ),
        (
            {
                "name": "foo",
                "acct_port": 456,
                "key": "encrypted_string",
            }
        ),
        (
            {
                "name": "foo",
                "auth_port": 123,
                "acct_port": 456,
                "key": "encrypted_string",
            }
        ),
    ]

    @pytest.mark.parametrize("kwargs", failing_cases)
    def test_failing_creation(self, kwargs):
        """Test a failing creation"""
        with pytest.raises(TypeError):
            interface = RadiusServerConfig(**kwargs)  # pyright: ignore
            return interface

    working_cases = [
        (
            {
                "ip_address": ipv4,
                "name": "foo",
                "key": "encrypted_string",
            },
            ipv4,
            "foo",
            "encrypted_string",
            1812,
            1813,
            [
                "radius server foo",
                " address ipv4 1.1.1.1",
                " key 7 encrypted_string",
            ],
        ),
        (
            {
                "ip_address": ipv6,
                "name": "foo",
                "key": "encrypted_string",
            },
            ipv6,
            "foo",
            "encrypted_string",
            1812,
            1813,
            [
                "radius server foo",
                " address ipv4 2001:db8::1",
                " key 7 encrypted_string",
            ],
        ),
        (
            {
                "ip_address": ipv4,
                "name": "foo",
                "auth_port": 123,
                "key": "encrypted_string",
            },
            ipv4,
            "foo",
            "encrypted_string",
            123,
            1813,
            [
                "radius server foo",
                " address ipv4 1.1.1.1 auth-port 123",
                " key 7 encrypted_string",
            ],
        ),
        (
            {
                "ip_address": ipv4,
                "name": "foo",
                "acct_port": 456,
                "key": "encrypted_string",
            },
            ipv4,
            "foo",
            "encrypted_string",
            1812,
            456,
            [
                "radius server foo",
                " address ipv4 1.1.1.1 acct-port 456",
                " key 7 encrypted_string",
            ],
        ),
        (
            {
                "ip_address": ipv4,
                "name": "foo",
                "auth_port": 123,
                "acct_port": 456,
                "key": "encrypted_string",
            },
            ipv4,
            "foo",
            "encrypted_string",
            123,
            456,
            [
                "radius server foo",
                " address ipv4 1.1.1.1 auth-port 123 acct-port 456",
                " key 7 encrypted_string",
            ],
        ),
        (
            {
                "ip_address": ipv6,
                "name": "foo",
                "auth_port": 123,
                "key": "encrypted_string",
            },
            ipv6,
            "foo",
            "encrypted_string",
            123,
            1813,
            [
                "radius server foo",
                " address ipv4 2001:db8::1 auth-port 123",
                " key 7 encrypted_string",
            ],
        ),
        (
            {
                "ip_address": ipv6,
                "name": "foo",
                "acct_port": 456,
                "key": "encrypted_string",
            },
            ipv6,
            "foo",
            "encrypted_string",
            1812,
            456,
            [
                "radius server foo",
                " address ipv4 2001:db8::1 acct-port 456",
                " key 7 encrypted_string",
            ],
        ),
        (
            {
                "ip_address": ipv6,
                "name": "foo",
                "auth_port": 123,
                "acct_port": 456,
                "key": "encrypted_string",
            },
            ipv6,
            "foo",
            "encrypted_string",
            123,
            456,
            [
                "radius server foo",
                " address ipv4 2001:db8::1 auth-port 123 acct-port 456",
                " key 7 encrypted_string",
            ],
        ),
    ]

    @pytest.mark.parametrize(
        "kwargs, ip, name, key, auth_port, acct_port, config_lines",
        working_cases,
    )
    def test_working_creations(
        self, kwargs, ip, name, key, auth_port, acct_port, config_lines
    ):
        radius_server = RadiusServerConfig(**kwargs)
        assert radius_server.ip_address == ip
        assert radius_server.name == name
        assert radius_server.auth_port == auth_port
        assert radius_server.acct_port == acct_port

    @pytest.mark.parametrize(
        "kwargs, ip, name, key, auth_port, acct_port, config_lines",
        working_cases,
    )
    def test_working_creations_config_lines(
        self, kwargs, ip, name, key, auth_port, acct_port, config_lines
    ):
        radius_server = RadiusServerConfig(**kwargs)
        assert radius_server.to_config_lines() == config_lines
