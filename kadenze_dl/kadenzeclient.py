import logging
import sys
import time
from pathlib import Path
from random import randint
from typing import List

import typer
from playwright._impl._browser import Browser
from playwright._impl._page import Page
from playwright.sync_api import sync_playwright

import kadenze_dl.utils as utils
from kadenze_dl.models import Session, Video
from kadenze_dl.settings import Settings

logger = logging.getLogger("client")
logger.addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.INFO)

conf: Settings = None  # type: ignore

BASE_URL = "https://www.kadenze.com"
COOKIES_XPATH = '//*[@id="iubenda-cs-banner"]/div/div/a'


def random_wait():
    time.sleep(randint(5, 8))


def execute_login(browser: Browser) -> Page:
    logger.info("Signing in www.kadenze.com ...")
    page: Page = browser.new_page()  # type: ignore
    _ = page.goto(BASE_URL)
    random_wait()
    _ = page.mouse.click(0, 0)
    _ = page.click(COOKIES_XPATH)
    _ = page.click("#email-login-btn")
    _ = page.fill("input#login_user_email", conf.login)
    _ = page.fill("input#login_user_password", conf.password)
    random_wait()
    _ = page.click("//*[@id='login_user']/button")
    random_wait()
    return page


def list_courses(page: Page) -> List[str]:
    try:
        _ = page.goto(BASE_URL + "/my_courses")
        random_wait()
        _ = page.click("text=View all")
        random_wait()
        div_courses = page.query_selector("div#my_courses")
        json_courses = div_courses.get_attribute("data-courses-data")  # type: ignore
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
        page_num = 1
        _ = page.goto(sessions_url)
        random_wait()
        div_sessions = page.query_selector("div#lectures_json")

        if div_sessions:
            json_sessions = div_sessions.get_attribute("data-lectures-json")  # type: ignore
            sessions = utils.get_sessions_from_json(json_sessions, course)

        # Courses with sessions > 10
        if page.query_selector("#pagination_page_number"):
            page_num += 1
            _ = page.goto(sessions_url + f"?page={page_num}")
            random_wait()
            div_sessions = page.query_selector("div#lectures_json")

            if div_sessions:
                json_sessions = div_sessions.get_attribute("data-lectures-json")  # type: ignore
                next_sessions = utils.get_sessions_from_json(json_sessions, course)
                sessions.extend(next_sessions)

    except Exception as e:
        logger.exception(f"Error while extracting sessions from course {course}: {e}")
    return sessions


def extract_session_videos(page: Page, session: Session) -> List[Video]:
    videos = []
    logger.info(f"Parsing session: {session.name}")
    try:
        _ = page.goto(BASE_URL + session.path)
        random_wait()
        div_videos = page.query_selector('//*[@id="video_json"]')
        json_videos = div_videos.get_attribute("value")  # type: ignore
        videos = utils.get_videos_from_json(json_videos, conf.resolution.value, session)
    except Exception:
        logger.info(f"Error while extracting videos from session={session.name}. Skipping...")
    return videos


def download_video(video: Video) -> None:
    filename = utils.extract_filename(video.url)
    download_path = conf.download_path
    if filename and download_path:
        session_prefix = str(video.session.index) + "-" + video.session.name
        full_path = download_path / video.session.course / session_prefix
        full_path.mkdir(parents=True, exist_ok=True)
        filename = utils.get_video_title(video.title, filename)
        utils.write_video(video.url, full_path, filename)
    else:
        logger.info(f"Could not extract filename: video={video.title}, session={video.session.name}, course={video.session.course}. Skipping...")


def download_course_videos(page: Page, course: str) -> None:
    videos: List[Video] = []
    sessions = extract_sessions(page, course)
    for session in sessions:
        session_videos = extract_session_videos(page, session)
        videos.extend(session_videos)
    videos = [v for v in videos if v.url is not None]  # filter out None urls (possible premium access)
    for video in videos:
        try:
            download_video(video)
        except Exception as e:
            logger.exception(f"Error while downloading video {video.title} from course {course}: {e}")


def download_all_courses_videos(settings: Settings) -> None:
    """main function to download all courses videos"""

    conf = settings
    p = sync_playwright().start()
    browser = p.firefox.launch(headless=True)
    try:
        page = execute_login(browser)  # type: ignore
        enrolled_courses = [utils.format_course(course) for course in list_courses(page)]
        if enrolled_courses:
            courses = [c for c in enrolled_courses if any(substring in c for substring in conf.courses)]
        else:
            courses = enrolled_courses
        logger.info("Selected courses for download: ")
        logger.info("\n".join(courses))
        for course in courses:
            download_course_videos(page, course)
        _ = page.close()
    except Exception as e:
        logger.exception(f"Error while running kadenze-dl: {e}")
    finally:
        browser.close()
        p.stop()
