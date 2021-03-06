import json
import logging
import re
import sys
from pathlib import Path
from typing import List, Optional

import requests
from slugify import slugify

from kadenze_dl.models import Session, Video

logger = logging.getLogger("utils")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

filename_pattern = re.compile("file/(.*\.mp4)\?")


def format_course(course: str) -> str:
    formatted_course = course.split("/")[-1]
    return f"{formatted_course}"


def extract_filename(video_url: str) -> Optional[str]:
    try:
        filename = re.search(filename_pattern, video_url).group(1)
    except Exception:
        filename = None
    return filename


def get_courses_from_json(response: str) -> List[str]:
    try:
        json_string = json.loads(response)
        courses = [course["course_path"] for course in json_string["courses"]]
    except ValueError:
        logger.info("Error getting the courses list. Check that you're enrolled on selected courses.")
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
                logger.exception(f"Error while extracting session metadata from course {course} at index {i}: {e}")
    except Exception as e:
        logger.exception(f"Error while extracting session metadata from course {course}: {e}")
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
                logger.exception(f"Error while extracting video metadata from session {session.name} at index {i}: {e}")
    except Exception as e:
        logger.exception(f"Error getting videos: {e}")
    return videos


def get_video_title(video_title: str, filename: str) -> str:
    try:
        slug = slugify(video_title)
        video_title = "_".join(filename.split(".")[:-1]) + "p_" + slug + "." + filename.split(".")[-1]
    except IndexError:
        video_title = filename
    return video_title


def write_video(video_url: str, full_path: str, filename: str, chunk_size: int = 4096):
    try:
        size = int(requests.head(video_url).headers["Content-Length"])
        size_on_disk = check_if_file_exists(full_path, filename)
        if size_on_disk < size:
            fd = Path(full_path)
            fd.mkdir(parents=True, exist_ok=True)
            with open(fd / filename, "wb") as f:
                r = requests.get(video_url, stream=True)
                current_size = 0
                for chunk in r.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    current_size += chunk_size
                    s = progress(current_size, size, filename)
                    print(s, end="", flush=True)
                print(s)
        else:
            logger.info(f"{filename} already downloaded, skipping...")
    except Exception as e:
        logger.exception(f"Error while writing video to {full_path}/{filename}: {e}")


def check_if_file_exists(full_path: str, filename: str) -> int:
    f = Path(full_path + "/" + filename)
    if f.exists():
        return f.stat().st_size
    else:
        return 0


def progress(count, total, status=""):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))
    percents = round(100.0 * count / float(total), 1)
    bar = "=" * filled_len + "-" * (bar_len - filled_len)
    s = "[%s] %s%s filename: %s\r" % (bar, percents, "%", status)
    return s
