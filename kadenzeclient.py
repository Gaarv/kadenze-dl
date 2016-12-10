import json
import re
import os
import requests
from requests import Session
from robobrowser import RoboBrowser
from config import Config
from progress import progress


class KadenzeClient(object):
    current_session = None
    current_prefix = None

    def __init__(self):
        self.config = Config()
        self.base_url = "https://www.kadenze.com"
        self.session = create_session()
        self.browser = RoboBrowser(history=True, session=self.session, parser="lxml", allow_redirects=False)

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(KadenzeClient, cls).__new__(cls)
        return cls.instance

    def execute_login(self):
        print("Signing in www.kadenze.com ...")
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

    def download_videos_per_session(self, course, session, session_videos):
        print("Parsing session: {0}".format(session))
        for i, video_url in enumerate(session_videos):
            pattern = re.search("file/(.*mp4)", video_url)
            filename = pattern.group(1)
            if i == 0:
                session_prefix = re.search(r'\d+', filename).group()
                session_prefixed = session_prefix + "-" + session
                full_path = self.config.path + "/" + course + "/" + session_prefixed
                os.makedirs(full_path, exist_ok=True)
            write_video(video_url, full_path, filename)

    def download_course_videos(self, course):
        sessions = self.list_sessions(course)
        videos = [self.list_videos(url) for url in sessions]
        videos_per_sessions = zip(sessions, videos)
        for session_data, session_videos in videos_per_sessions:
            session_data = session_data.replace("courses/", "").replace("sessions/", "")
            course, session = session_data.split("/")[-2], session_data.split("/")[-1]
            self.download_videos_per_session(course, session, session_videos)

    def download_all_courses_videos(self):
        self.execute_login()
        enrolled_courses = [format_course(course) for course in self.list_courses()]
        courses = set(self.config.courses).intersection(enrolled_courses)
        for course in courses:
            print("Parsing course: {0}".format(course))
            self.download_course_videos(course)


def create_session():
    session = Session()
    return session


def format_course(course):
    return "{0}".format(course.split("/")[-1])


def get_courses_from_json(response):
    json_string = json.loads(response)
    courses = [course["course_path"] for course in json_string["courses"]]
    return courses


def get_videos_from_json(response):
    json_string = json.loads(response)
    videos = [video["h264_720_url"] for video in json_string["videos"]]
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
