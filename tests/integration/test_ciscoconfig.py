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

    get_text_tests = [
        ("empty_config", ["!"]),
        ("config_from_file", sample1.config.split("\n")),
    ]

    @pytest.mark.parametrize("config, expected", get_text_tests)
    def test_get_text(self, config, expected, request):
        config = request.getfixturevalue(config)
        assert config.get_text() == expected
