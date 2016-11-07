import json
import re
import os
import requests
from requests import Session
from robobrowser import RoboBrowser
from config import Config


class KadenzeClient:
    def __init__(self):
        self.config = Config()
        self.base_url = "https://www.kadenze.com"
        self.session = create_session()
        self.browser = RoboBrowser(history=True, session=self.session, parser="lxml", allow_redirects=False)

    def execute_login(self):
        self.browser.open(self.base_url)
        signup_form = self.browser.get_form(id="login_user")
        signup_form['user[email]'].value = self.config.login
        signup_form['user[password]'].value = self.config.password
        self.browser.session.headers["Referer"] = self.base_url
        self.browser.submit_form(signup_form)

    def list_courses(self):
        self.browser.open(self.base_url)
        response = self.browser.parsed()[0].text
        courses = get_courses_from_json(response)
        return courses

    def list_sessions(self, course):
        sessions_url = "/".join((self.base_url, "courses", course, "sessions"))
        self.browser.open(sessions_url)
        results = [link["href"] for link in self.browser.get_links() if self.config.courses in link["href"]]
        sessions = [result for result in results if "sessions/" in result]
        return sessions

    def list_videos(self, url):
        self.browser.open(self.base_url + url)
        response = self.browser.select("#video_json")[0]["value"]
        videos = get_videos_from_json(response)
        return videos

    def download_videos_all(self):
        self.execute_login()
        courses = [format_course(course) for course in self.list_courses()]
        sessions = [self.list_sessions(course) for course in courses if course in self.config.courses]
        videos_to_download = [self.list_videos(session) for session in sessions[0]]
        videos_per_sessions = zip(videos_to_download, sessions[0])
        for videos_session, session_name in videos_per_sessions:
            download_videos_per_session(videos_session, session_name, self.config.path)


def format_course(course):
    return "{0}".format(course.split("/")[-1])


def create_session():
    session = Session()
    return session


def get_courses_from_json(response):
    json_string = json.loads(response)
    courses = [course["course_path"] for course in json_string["courses"]]
    return courses


def get_videos_from_json(response):
    json_string = json.loads(response)
    videos = [video["h264_720_url"] for video in json_string["videos"]]
    return videos


def download_videos_per_session(videos_session, session_name, path):
    for video in videos_session:
        full_path = (path + session_name) \
            .replace("courses/", "") \
            .replace("sessions/", "")
        write_video(video, full_path)


def write_video(file_url, full_path):
    print("Downloading video to {0}".format(full_path))
    r = requests.get(file_url, stream=True)
    pattern = re.search("file/(.*mp4)", file_url)
    filename = pattern.group(1)
    os.makedirs(full_path, exist_ok=True)
    with open(full_path + "/" + filename, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=4096):
            fd.write(chunk)
