import json
import os
import re
from typing import List

import requests
from slugify import slugify

from kadenze_dl.progress import progress

filename_pattern = re.compile("file/(.*\.mp4)\?")
session_prefix_pattern = re.compile(r"\d+")


def format_course(course: str) -> str:
    return "{0}".format(course.split("/")[-1])


def extract_filename(video_url: str) -> str:
    filename = re.search(filename_pattern, video_url).group(1)
    return filename


def extract_session_prefix(filename: str) -> str:
    session_prefix = re.search(session_prefix_pattern, filename).group()
    return session_prefix


def get_courses_from_json(response: str) -> List[str]:
    try:
        json_string = json.loads(response)
        courses = [course["course_path"] for course in json_string["courses"]]
    except ValueError:
        print("Error getting the courses list. Check that you're enrolled on selected courses.")
        courses = []
    return courses


def get_sessions_from_json(response: str) -> List[str]:
    try:
        json_string = json.loads(response)
        sessions = [session["course_session_path"] for session in json_string["lectures"]]
    except ValueError:
        print("This course doesn't seem to have any video yet, skipping...")
        sessions = []
    return sessions


def get_videos_from_json(response: str, resolution: int) -> List[str]:
    try:
        json_string = json.loads(response)
        video_format = "h264_{0}_url".format(resolution)
        videos = [video[video_format] for video in json_string["videos"]]
    except ValueError:
        print("Error getting videos list. Check if the course has indeed videos available.")
        videos = []
    return videos


def get_videos_titles_from_json(response: str) -> List[str]:
    try:
        json_string = json.loads(response)
        videos_titles = [video["title"] for video in json_string["videos"]]
    except ValueError:
        print("Error getting videos titles. Files names will be used.")
        videos_titles = []
    return videos_titles


def get_video_title(session_num: int, i: int, videos_titles: List[str], filename: str) -> str:
    try:
        slug = slugify(videos_titles[session_num][i])
        video_title = "_".join(filename.split(".")[:-1]) + "p_" + slug + "." + filename.split(".")[-1]
    except IndexError:
        video_title = filename
    return video_title


def write_video(video_url: str, full_path: str, filename: str, chunk_size=4096) -> None:
    size = int(requests.head(video_url).headers["Content-Length"])
    size_on_disk = check_if_file_exists(full_path, filename)
    if size_on_disk < size:
        with open(full_path + "/" + filename, "wb") as fd:
            r = requests.get(video_url, stream=True)
            current_size = 0
            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)
                current_size += chunk_size
                s = progress(current_size, size, filename)
                print(s, end="", flush=True)
            print(s)
    else:
        print("{0} already downloaded, skipping...".format(filename))


def check_if_file_exists(full_path: str, filename: str) -> int:
    try:
        size = os.path.getsize(full_path + "/" + filename)
    except os.error:
        size = 0
    return size
