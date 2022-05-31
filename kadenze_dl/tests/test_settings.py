from pathlib import Path

from kadenze_dl.settings import build_settings
from typer.testing import CliRunner

runner = CliRunner()


TEST_CONFIG_FILE = Path(".").absolute() / "kadenze_dl" / "configuration.yml"


def test_build_settings():
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
