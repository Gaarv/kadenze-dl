import logging
import sys
import time
from pathlib import Path
from random import randint
from typing import List

from playwright._impl._browser import Browser, Page
from playwright.sync_api import sync_playwright

import kadenze_dl.utils as utils
from kadenze_dl.models import Session, Video
from kadenze_dl.settings import Settings

logger = logging.getLogger("client")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)


BASE_URL = "https://www.kadenze.com"
conf = Settings()


def execute_login(browser: Browser) -> Page:
    logger.info("Signing in www.kadenze.com ...")
    page: Page = browser.new_page()
    page.goto(BASE_URL)
    page.click("#email-login-btn")
    page.fill("input#login_user_email", conf.login)
    page.fill("input#login_user_password", conf.password)
    time.sleep(randint(3, 8))
    page.click("//*[@id='login_user']/button")
    time.sleep(randint(3, 8))
    return page


def list_courses(page: Page) -> List[str]:
    try:
        page.goto(BASE_URL + "/my_courses")
        page.click("text=View all")
        time.sleep(randint(3, 8))
        div_courses = page.query_selector("div#my_courses")
        json_courses = div_courses.get_attribute("data-courses-data")
        courses = utils.get_courses_from_json(json_courses)
    except Exception as e:
        logger.exception(f"Error while listing courses: {e}")
        courses = []
    return courses


def extract_sessions(page: Page, course: str) -> List[Session]:
    sessions = []
    logger.info(f"Parsing course: {course}")
    sessions_url = "/".join((BASE_URL, "courses", course, "sessions"))
    try:
        page.goto(sessions_url)
        div_sessions: Page = page.query_selector("div#lectures_json")
        json_sessions = div_sessions.get_attribute("data-lectures-json")
        sessions = utils.get_sessions_from_json(json_sessions, course)
    except Exception as e:
        logger.exception(f"Error while extracting sessions from course {course}: {e}")
    return sessions


def extract_session_videos(page: Page, session: Session) -> List[Video]:
    videos = []
    try:
        logger.info(f"Parsing session: {session.name}")
        page.goto(BASE_URL + session.path)
        div_videos: Page = page.query_selector("#video_json")
        json_videos = div_videos.get_attribute("value")
        videos = utils.get_videos_from_json(json_videos, conf.video_format, session)
    except Exception as e:
        logger.exception(f"Error while extracting videos from session {session.name}: {e}")
    return videos


def download_video(video: Video):
    filename = utils.extract_filename(video.url)
    if filename is not None:
        session_prefix = str(video.session.index) + "-" + video.session.name
        full_path = conf.path + "/" + video.session.course + "/" + session_prefix
        Path(full_path).mkdir(parents=True, exist_ok=True)
        if conf.videos_titles:
            filename = utils.get_video_title(video.title, filename)
        utils.write_video(video.url, full_path, filename)
    else:
        logger.info(
            f"Could not extract filename of video {video.title} from session {video.session.name} and course {video.session.course}, skipping..."
        )


def download_course_videos(page: Page, course: str):
    sessions = extract_sessions(page, course)
    videos = [extract_session_videos(page, session) for session in sessions]
    videos = [v for sublist in videos for v in sublist]
    for video in videos:
        try:
            download_video(video)
        except Exception as e:
            logger.exception(f"Error while downloading video {video.title} from course {course}: {e}")


def download_all_courses_videos():
    p = sync_playwright().start()
    browser = p.firefox.launch(headless=True)
    try:
        page = execute_login(browser)
        enrolled_courses = [utils.format_course(course) for course in list_courses(page)]
        if conf.selected_only and enrolled_courses:
            courses = [c for c in enrolled_courses if any(substring in c for substring in conf.courses)]
        else:
            courses = enrolled_courses
        logger.info("Selected courses for download: ")
        logger.info("\n".join(courses))
        for course in courses:
            download_course_videos(page, course)
        page.close()
    except Exception as e:
        logger.exception(f"Error while running kadenze-dl: {e}")
    finally:
        browser.close()
        p.stop()
