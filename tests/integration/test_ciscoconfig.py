import pytest
import sample1

from py_net_conf_cisco import CiscoConfig


class TestCiscoConfig:
    """
    Test class for the CiscoConfig module
    """

    def test_empty_creation_fails(self):
        with pytest.raises(ValueError):
            config = CiscoConfig()
            return config

    def test_init_with_text(self):
        """Test initialization with config text."""
        config = CiscoConfig(config_text=sample1.config)
        assert config._parsed_config is not None

    def test_init_with_file(self, sample_config_file):
        """Test initialization with config file."""
        config = CiscoConfig(config_path=sample_config_file)
        assert config._parsed_config is not None

    last_line_params = [("empty_config", -1), ("config_from_file", -2)]

    @pytest.mark.parametrize("config, expected", last_line_params)
    def test__last_line(self, config, expected, request):
        config = request.getfixturevalue(config)
        assert (
            config._last_line() == config._parsed_config.config_objs[expected]
        )

    def find_hostname_line(self, parsed_config):
        return parsed_config.find_objects(r"^hostname\s+")[0]

    def test_seting_hostname_property_with_sample1(self, config_from_file):
        """Test setting the hostname"""
        config_from_file.hostname = "foo"
        assert config_from_file.hostname == "foo"
        hostname_line = self.find_hostname_line(config_from_file._parsed_config)
        assert hostname_line.text == "hostname foo"

    def test_seting_hostname_property_after_getting_hostanme(
        self, config_from_file
    ):
        """Test setting the hostname after getting the hostname"""
        hostname = config_from_file.hostname
        assert hostname == "TestSwitch"
        config_from_file.hostname = "foo"
        assert config_from_file.hostname == "foo"
        hostname_line = self.find_hostname_line(config_from_file._parsed_config)
        assert hostname_line.text == "hostname foo"

    def test_getting_hostname_property(self, config_from_file):
        """Test the hostname propeerty"""
        hostname = config_from_file.hostname
        assert hostname == "TestSwitch"
        hostname_line = self.find_hostname_line(config_from_file._parsed_config)
        assert hostname_line.text == "hostname TestSwitch"

    def test_seting_hostname_property_with_no_hostname_version_line(
        self, config_from_file
    ):
        """Test setting the hostname when there is not a hostname configured
        but there is a version line"""
        hostname_line = self.find_hostname_line(config_from_file._parsed_config)
        hostname_line.delete()
        config_from_file._parsed_config.commit()
        config_from_file.hostname = "foo"
        assert config_from_file.hostname == "foo"
        hostname_line = self.find_hostname_line(config_from_file._parsed_config)
        assert hostname_line.text == "hostname foo"

    def test_setting_hostname_property_with_empty_config(self, empty_config):
        empty_config.hostname = "foo"
        assert empty_config.hostname == "foo"
        hostname_line = self.find_hostname_line(empty_config._parsed_config)
        assert hostname_line.text == "hostname foo"

    def test_empty_hostname(self, empty_config):
        assert empty_config.hostname == ""

    def test_setting_hostname_with_empty_config(self):
        config = CiscoConfig(config_text="")
        config.hostname = "foo"
        assert config.hostname == "foo"
        hostname_line = self.find_hostname_line(config._parsed_config)
        assert hostname_line.text == "hostname foo"

    def test_setting_hostname_with_existing_config(self, config_from_file):
        config_from_file.hostname = "foo"
        assert config_from_file.hostname == "foo"
        hostname_line = self.find_hostname_line(config_from_file._parsed_config)
        assert hostname_line.text == "hostname foo"
