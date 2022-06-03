import importlib
from pathlib import Path
from unittest.mock import patch

import typer
from typer.testing import CliRunner

TEST_CONFIG_FILE = Path(".").absolute() / "kadenze_dl" / "configuration.yml"

runner = CliRunner()


def download_all_courses_videos_mock(self) -> None:
    return None


def test_cli_with_config():
    patch("kadenze_dl.kadenzeclient.KadenzeClient.download_all_courses_videos", download_all_courses_videos_mock).start()
    entrypoint: typer.Typer = importlib.import_module("kadenze_dl.kadenze-dl")  # type:ignore
    app = entrypoint.app  # type:ignore
    result = runner.invoke(app, ["--config-file", TEST_CONFIG_FILE.as_posix()])
    assert result.exit_code == 0


def test_cli_with_args():
    patch("kadenze_dl.kadenzeclient.KadenzeClient.download_all_courses_videos", download_all_courses_videos_mock).start()
    entrypoint: typer.Typer = importlib.import_module("kadenze_dl.kadenze-dl")  # type:ignore
    app = entrypoint.app  # type:ignore
    result = runner.invoke(app, ["--login", "myemail@gmail.com", "--password", "mypassword", "--download-path", "/home/user/videos/kadenze"])
    assert result.exit_code == 0


def test_cli_with_missing_arg():
    patch("kadenze_dl.kadenzeclient.KadenzeClient.download_all_courses_videos", download_all_courses_videos_mock).start()
    entrypoint: typer.Typer = importlib.import_module("kadenze_dl.kadenze-dl")  # type:ignore
    app = entrypoint.app  # type:ignore
    result = runner.invoke(app, ["--login", "myemail@gmail.com", "--password", "mypassword"])
    assert "No config file and or not enough mandatory arguments were provided" in result.stdout


def test_cli_bad_config_file():
    patch("kadenze_dl.kadenzeclient.KadenzeClient.download_all_courses_videos", download_all_courses_videos_mock).start()
    entrypoint: typer.Typer = importlib.import_module("kadenze_dl.kadenze-dl")  # type:ignore
    app = entrypoint.app  # type:ignore
    result = runner.invoke(app, ["--config-file", "requirements.txt"])
    assert "Error while building configuration from file or provided arguments" in result.stdout
