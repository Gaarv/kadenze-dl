import os
import helpers
from requests import Session
from robobrowser import RoboBrowser
from settings import Settings


class KadenzeClient(object):
    def __init__(self):
        self.conf = Settings()
        self.base_url = "https://www.kadenze.com"
        self.session = Session()
        self.browser = RoboBrowser(history=True, session=self.session, parser="lxml", allow_redirects=False)

    def execute_login(self):
        print("Signing in www.kadenze.com ...")
        self.browser.open(self.base_url)
        signup_form = self.browser.get_form(id="login_user")
        signup_form['user[email]'].value = self.conf.login
        signup_form['user[password]'].value = self.conf.password
        self.browser.session.headers["Referer"] = self.base_url
        self.browser.submit_form(signup_form)

    def list_courses(self):
        self.browser.open(self.base_url)
        response = self.browser.parsed()[0].text
        courses = helpers.get_courses_from_json(response)
        return courses

    def list_sessions(self, course):
        sessions_url = "/".join((self.base_url, "courses", course, "sessions"))
        self.browser.open(sessions_url)
        links = self.browser.get_links()
        sessions = helpers.get_sessions_from_links(course, links)
        return sessions

    def list_videos(self, url):
        self.browser.open(self.base_url + url)
        response = self.browser.select("#video_json")[0]["value"]
        videos = helpers.get_videos_from_json(response)
        return videos

    def download_videos_per_session(self, course, session, session_videos):
        print("Parsing session: {0}".format(session))
        for i, video_url in enumerate(session_videos):
            filename = helpers.extract_filename(video_url)
            if i == 0:
                session_prefix = helpers.extract_session_prefix(filename)
                session_prefixed = session_prefix + "-" + session
                full_path = self.conf.path + "/" + course + "/" + session_prefixed
                os.makedirs(full_path, exist_ok=True)
            helpers.write_video(video_url, full_path, filename)

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
        enrolled_courses = [helpers.format_course(course) for course in self.list_courses()]
        courses = set(self.conf.courses).intersection(enrolled_courses)
        for course in courses:
            print("Parsing course: {0}".format(course))
            self.download_course_videos(course)
