import subprocess
from pathlib import Path
from typing import List, Optional

import typer

from kadenze_dl.kadenzeclient import KadenzeClient
from kadenze_dl.settings import build_settings

app = typer.Typer()


@app.command()
def main(
    login: Optional[str] = typer.Option(None, help="Login (email only) to kadenze"),
    password: Optional[str] = typer.Option(None, help="Password to kadenze"),
    resolution: str = typer.Option("720", help="Video resolution. Valid values are 360 and 720"),
    download_path: Optional[Path] = typer.Option(None, help="Absolute path to where to save videos on disk"),
    courses: List[str] = typer.Option(["all"], help="Courses to download, usage can be repeated."),
    config_file: Path = typer.Option(None, help="Path to a YAML configuration file that will take precedence over all CLI arguments"),
    proxy: Optional[str] = typer.Option(None, help="Proxy URL, ie. http://127.0.0.1:3128"),
):
    try:
        if config_file:
            typer.secho(f"Loading configuration from {config_file.as_posix()}", fg=typer.colors.GREEN)
        if config_file or all([login, password, download_path]):
            settings = build_settings(courses, resolution, config_file, login, password, download_path, proxy)
            subprocess.run(["playwright", "install", "firefox"])
            kadenze_client = KadenzeClient(settings)
            kadenze_client.download_all_courses_videos()
        else:
            typer.secho("No config file and or not enough mandatory arguments were provided. Check --help", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(e, fg=typer.colors.RED)


if __name__ == "__main__":
    app()
