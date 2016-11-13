import json
import re
import os
import requests
from requests import Session
from robobrowser import RoboBrowser
from config import Config
from multiprocessing import Process


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
        results = [link["href"] for link in self.browser.get_links() if course in link["href"]]
        sessions = {result for result in results if "sessions/" in result}
        return list(sessions)

    def list_videos(self, url):
        self.browser.open(self.base_url + url)
        response = self.browser.select("#video_json")[0]["value"]
        videos = get_videos_from_json(response)
        return videos

    def download_course_videos(self, course):
        jobs = []
        sessions = self.list_sessions(course)
        videos = [self.list_videos(url) for url in sessions]
        videos_per_sessions = zip(sessions, videos)
        for session_name, session_videos in videos_per_sessions:
            p = Process(target=download_videos_per_session, args=(self.config.path, session_name, session_videos))
            jobs.append(p)
            p.start()

    def download_all_courses_videos(self):
        self.execute_login()
        enrolled_courses = [format_course(course) for course in self.list_courses()]
        courses = set(self.config.courses).intersection(enrolled_courses)
        for course in courses:
            self.download_course_videos(course)


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


def download_videos_per_session(base_path, session_name, session_videos):
    session_name = session_name.replace("courses/", "").replace("sessions/", "")
    for video_url in session_videos:
        write_video(base_path, session_name, video_url)


def write_video(base_path, session_name, video_url):
    r = requests.get(video_url, stream=True)
    pattern = re.search("file/(.*mp4)", video_url)
    filename = pattern.group(1)
    session_prefix = re.search(r'\d+', filename).group()
    course, session = session_name.split("/")[-2], session_name.split("/")[-1]
    session = session_prefix + "-" + session
    full_path = base_path + "/" + course + "/" + session
    print("Downloading {0}...".format(session + "/" + filename))
    os.makedirs(full_path, exist_ok=True)
    with open(full_path + "/" + filename, 'wb') as fd:
        for chunk in r.iter_content(chunk_size=4096):
            fd.write(chunk)
