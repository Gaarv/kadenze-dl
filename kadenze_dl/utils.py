import json
import re
from pathlib import Path
from typing import List, Optional

import requests
import typer
from slugify import slugify

from kadenze_dl.models import Session, Video

FILENAME_PATTERN = re.compile("file/(.*\\.mp4)\\?")


def format_course(course: str) -> str:
    formatted_course = course.split("/")[-1]
    return f"{formatted_course}"


def extract_filename(video_url: str) -> Optional[str]:
    filename = None
    try:
        match = re.search(FILENAME_PATTERN, video_url)
        if match:
            filename = match.group(1)
    except Exception as e:
        typer.secho(f"Error while extracting filename: {e}", fg=typer.colors.RED)
    return filename


def get_courses_from_json(response: str) -> List[str]:
    try:
        json_string = json.loads(response)
        courses = [course["course_path"] for course in json_string["courses"]]
    except ValueError:
        typer.secho("Error getting the courses list. Check that you're enrolled on selected courses.", fg=typer.colors.RED)
        courses = []
    return courses


def get_sessions_from_json(response: str, course: str) -> List[Session]:
    sessions = []
    try:
        d = json.loads(response)
        lectures = d["lectures"]
        for i, lecture in enumerate(lectures, start=1):
            try:
                session = Session(course, lecture["order"], slugify(lecture["title"]), lecture["course_session_path"])
                sessions.append(session)
            except Exception as e:
                typer.secho(f"Error while extracting session metadata from course {course} at index {i}: {e}", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(f"Error while extracting session metadata from course {course}: {e}", fg=typer.colors.RED)
    return sessions


def get_videos_from_json(response: str, resolution: int, session: Session) -> List[Video]:
    videos = []
    try:
        d = json.loads(response)
        video_format = f"h264_{resolution}_url"
        vs = d["videos"]
        for i, v in enumerate(vs, start=1):
            try:
                video = Video(session, v["order"], v["title"], v[video_format])
                videos.append(video)
            except Exception as e:
                typer.secho(f"Error while extracting video metadata from session {session.name} at index {i}: {e}", fg=typer.colors.RED)
    except Exception as e:
        typer.secho(f"Error getting videos: {e}", fg=typer.colors.RED)
    return videos


def get_video_title(video_title: str, filename: str) -> str:
    try:
        slug = slugify(video_title)
        video_title = "_".join(filename.split(".")[:-1]) + "p_" + slug + "." + filename.split(".")[-1]
    except IndexError:
        video_title = filename
    return video_title


def write_video(video_url: str, full_path: Path, filename: str, chunk_size: int = 4096) -> None:
    try:
        size = int(requests.head(video_url).headers["Content-Length"])
        size_on_disk = check_if_file_exists(full_path, filename)
        if size_on_disk < size:
            full_path.mkdir(parents=True, exist_ok=True)
            r = requests.get(video_url, stream=True)
            current_size = 0
            with open(full_path / filename, "wb") as f:
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    current_size += chunk_size
                    s = progress(current_size, size, filename)
                    print(s, end="", flush=True)
                typer.echo(s)  # type: ignore
        else:
            typer.echo(f"{filename} already downloaded, skipping...")
    except Exception as e:
        typer.secho(f"Error while writing video to {full_path.joinpath(filename).as_posix()}: {e}", fg=typer.colors.RED)


def check_if_file_exists(full_path: Path, filename: str) -> int:
    f = full_path / filename
    if f.exists():
        return f.stat().st_size
    else:
        return 0


def progress(count, total, status="") -> str:
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = "=" * filled_len + "-" * (bar_len - filled_len)
    s = f"[{bar}] {percents}% filename: {status}\r"
    return s
