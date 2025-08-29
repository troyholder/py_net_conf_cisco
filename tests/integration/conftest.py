import os
import tempfile

import pytest
import sample1

from py_net_conf_cisco import CiscoConfig


@pytest.fixture
def empty_config():
    """Create and empty config"""
    return CiscoConfig(config_text="!")


@pytest.fixture
def sample_config_file():
    """Create a temporary configuration file for testing."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".cfg", delete=False
    ) as f:
        f.write(sample1.config)
        temp_path = f.name

    yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def config_from_file(sample_config_file):
    """Create CiscoConfig instance from file."""
    return CiscoConfig(config_path=sample_config_file)
