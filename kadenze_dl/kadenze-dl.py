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
    resolution: str = typer.Argument("720", help="Video resolution. Valid values are 360 and 720"),
    download_path: Optional[Path] = typer.Option(None, help="Absolute path to where to save videos on disk"),
    courses: List[str] = typer.Argument(["all"], help="List of courses to download, comma-separated"),
    config_file: Path = typer.Option(None, help="Path to a YAML configuration file that will take precedence over all CLI arguments"),
):
    try:
        typer.secho(f"Loading configuration from {config_file.as_posix()}.", fg=typer.colors.GREEN)
        settings = build_settings(courses, resolution, config_file, login, password, download_path)
        subprocess.run(["playwright", "install"])
        kadenze_client = KadenzeClient(settings)
        kadenze_client.download_all_courses_videos()
    except Exception as e:
        typer.secho(e, fg=typer.colors.RED)


if __name__ == "__main__":
    app()
