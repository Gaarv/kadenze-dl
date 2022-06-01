from pathlib import Path

import pytest
from kadenze_dl.settings import build_settings
from typer.testing import CliRunner

runner = CliRunner()


TEST_CONFIG_FILE = Path(".").absolute() / "kadenze_dl" / "configuration.yml"


def test_build_settings_config_file():
    settings = build_settings(courses=["awesome-course-1", "awesome-course-2"], resolution="360", config_file=TEST_CONFIG_FILE)
    assert settings.login == "myemail@gmail.com"
    assert settings.password == "mypassword"
    assert settings.download_path.as_posix() == "/home/user/videos/kadenze"
    assert settings.courses == ["all"]
    assert settings.resolution.value == "720"


def test_settings_singleton():
    s1 = build_settings(courses=["all"], resolution="720", config_file=TEST_CONFIG_FILE)
    s2 = build_settings(courses=[], resolution="360", config_file=TEST_CONFIG_FILE)
    assert s1 is s2
    assert s2.login == "myemail@gmail.com"
    assert s2.password == "mypassword"
    assert s2.download_path.as_posix() == "/home/user/videos/kadenze"
    assert s2.courses == ["all"]
    assert s2.resolution.value == "720"


def test_settings_cli_valid_arguments():
    test_login = "myemail@gmail.com"
    test_password = "mypassword"
    test_download_path = Path("/home/user/videos/kadenze")
    settings = build_settings(
        courses=["all"],
        resolution="720",
        login=test_login,
        password=test_password,
        download_path=test_download_path,
    )
    assert settings.login == test_login
    assert settings.password == test_password
    assert settings.download_path == test_download_path
    assert settings.courses == ["all"]
    assert settings.resolution.value == "720"


def test_settings_cli_invalid_arguments():
    test_download_path = Path("/home/user/videos/kadenze")
    with pytest.raises(ValueError):
        # no login, no password and no config file provided
        build_settings(courses=["all"], resolution="720", download_path=test_download_path)
