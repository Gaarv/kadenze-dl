import os
import json
import re
import requests
from progress import progress

filename_pattern = re.compile("file/(.*\.mp4)\?")
session_prefix_pattern = re.compile(r'\d+')


def format_course(course):
    return "{0}".format(course.split("/")[-1])


def extract_filename(video_url):
    filename = re.search(filename_pattern, video_url).group(1)
    return filename


def extract_session_prefix(filename):
    session_prefix = re.search(session_prefix_pattern, filename).group()
    return session_prefix


def get_courses_from_json(response):
    json_string = json.loads(response)
    courses = [course["course_path"] for course in json_string["courses"]]
    return courses


def get_sessions_from_json(response):
    json_string = json.loads(response)
    sessions = [session["delete_lecture_path"] for session in json_string["lectures"]]
    return sessions


def get_videos_from_json(response, resolution):
    json_string = json.loads(response)
    video_format = "h264_{0}_url".format(resolution)
    videos = [video[video_format] for video in json_string["videos"]]
    return videos


def write_video(video_url, full_path, filename, chunk_size=4096):
    size = int(requests.head(video_url).headers['Content-Length'])
    size_on_disk = check_if_file_exists(full_path, filename)
    if size_on_disk < size:
        with open(full_path + "/" + filename, 'wb') as fd:
            r = requests.get(video_url, stream=True)
            current_size = 0
            for chunk in r.iter_content(chunk_size=chunk_size):
                fd.write(chunk)
                current_size += chunk_size
                s = progress(current_size, size, filename)
                print(s, end='', flush=True)
            print(s)
    else:
        print("{0} already downloaded, skipping...".format(filename))


def check_if_file_exists(full_path, filename):
    try:
        size = os.path.getsize(full_path + "/" + filename)
    except os.error:
        size = 0
    return size
