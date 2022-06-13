import subprocess
import time
from pathlib import Path
from unittest.mock import patch

from kadenze_dl.kadenzeclient import KadenzeClient
from kadenze_dl.settings import build_settings
from playwright.sync_api import sync_playwright

TEST_CONFIG_FILE = Path(".").absolute() / "kadenze_dl" / "configuration.yml"


def download_all_courses_videos_mock(self) -> None:
    subprocess.run(["playwright", "install"])
    p = sync_playwright().start()
    browser = p.firefox.launch(headless=True)
    time.sleep(1)
    browser.close()
    p.stop()


def test_playwright_install():
    patch("kadenze_dl.kadenzeclient.KadenzeClient.download_all_courses_videos", download_all_courses_videos_mock).start()
    settings = build_settings(courses=["all"], resolution="720", config_file=TEST_CONFIG_FILE)
    kadendze_client = KadenzeClient(settings)
    kadendze_client.download_all_courses_videos()
