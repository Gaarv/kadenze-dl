import time
from enum import Enum, unique
from random import randint
from typing import List

import typer
from playwright._impl._browser import Browser
from playwright._impl._page import Page
from playwright.sync_api import sync_playwright

import kadenze_dl.utils as utils
from kadenze_dl.models import Session, Video
from kadenze_dl.settings import Settings

BASE_URL = "https://www.kadenze.com"


@unique
class KadenzeSelectors(str, Enum):
    cookies_consent = '//*[@id="iubenda-cs-banner"]/div/div/a'
    login_email_button = "#email-login-btn"
    login_email_input = "input#login_user_email"
    login_password_input = "input#login_user_password"
    login_button = "//*[@id='login_user']/button"
    view_all_courses = "text=View all"
    view_my_courses = "div#my_courses"
    view_lectures = "div#lectures_json"
    pagination = "#pagination_page_number"
    pagination_next_disabled = ".next.is-disabled"
    videos = '//*[@id="video_json"]'


class KadenzeClient:
    def __init__(self, settings: Settings) -> None:
        self.conf = settings

    def execute_login(self, browser: Browser) -> Page:  # pragma: no cover
        typer.echo("Signing in www.kadenze.com ...")
        page: Page = browser.new_page()  # type: ignore
        _ = page.goto(BASE_URL)
        random_wait()
        _ = page.mouse.click(0, 0)  # Click popup banner
        _ = page.click(KadenzeSelectors.cookies_consent)  # Click cookie consent
        _ = page.click(KadenzeSelectors.login_email_button)
        _ = page.fill(KadenzeSelectors.login_email_input, self.conf.login)
        _ = page.fill(KadenzeSelectors.login_password_input, self.conf.password)
        random_wait()
        _ = page.click(KadenzeSelectors.login_button)
        random_wait()
        return page

    def list_courses(self, page: Page) -> List[str]:  # pragma: no cover
        try:
            _ = page.goto(BASE_URL + "/my_courses")
            random_wait()
            _ = page.click(KadenzeSelectors.view_all_courses)
            random_wait()
            div_courses = page.query_selector(KadenzeSelectors.view_my_courses)
            json_courses = div_courses.get_attribute("data-courses-data")  # type: ignore
            courses = utils.get_courses_from_json(json_courses)
        except Exception as e:
            typer.secho(f"Error while listing courses: {e}", fg=typer.colors.RED)
            courses = []
        return courses

    def extract_sessions(self, page: Page, course: str) -> List[Session]:  # pragma: no cover
        sessions = []
        typer.echo(f"Parsing course: {course}")
        sessions_url = "/".join((BASE_URL, "courses", course, "sessions"))
        page_num = 1

        try:
            while True:
                sessions_url = sessions_url if page_num == 1 else sessions_url + f"?page={page_num}"
                _ = page.goto(sessions_url)
                random_wait()
                div_sessions = page.query_selector(KadenzeSelectors.view_lectures)
                if div_sessions:
                    json_sessions = div_sessions.get_attribute("data-lectures-json")  # type: ignore
                    _sessions = utils.get_sessions_from_json(json_sessions, course)
                    sessions.extend(_sessions)

                # for courses with more than 10 sessions
                if page.query_selector(KadenzeSelectors.pagination) and not page.query_selector(KadenzeSelectors.pagination_next_disabled):
                    page_num += 1
                else:
                    break

        except Exception as e:
            typer.secho(f"Error while extracting sessions from course {course}: {e}", fg=typer.colors.RED)

        return sessions

    def extract_session_videos(self, page: Page, session: Session) -> List[Video]:  # pragma: no cover
        videos = []
        typer.echo(f"Parsing session: {session.name}")
        try:
            _ = page.goto(BASE_URL + session.path)
            random_wait()
            div_videos = page.query_selector(KadenzeSelectors.videos)
            json_videos = div_videos.get_attribute("value")  # type: ignore
            videos = utils.get_videos_from_json(json_videos, self.conf.resolution.value, session)
        except Exception:
            typer.secho(f"Error while extracting videos from session={session.name}. Skipping...", fg=typer.colors.RED)
        return videos

    def download_video(self, video: Video) -> None:  # pragma: no cover
        filename = utils.extract_filename(video.url)
        download_path = self.conf.download_path
        if filename and download_path:
            session_prefix = str(video.session.index) + "-" + video.session.name
            full_path = download_path / video.session.course / session_prefix
            full_path.mkdir(parents=True, exist_ok=True)
            filename = utils.get_video_title(video.title, filename)
            utils.write_video(video.url, full_path, filename, proxy=self.conf.proxy)
        else:
            typer.secho(
                f"Could not extract filename: video={video.title}, session={video.session.name}, course={video.session.course}. Skipping...",
                fg=typer.colors.BLUE,
            )

    def download_course_videos(self, page: Page, course: str) -> None:  # pragma: no cover
        videos: List[Video] = []
        sessions = self.extract_sessions(page, course)
        for session in sessions:
            session_videos = self.extract_session_videos(page, session)
            videos.extend(session_videos)
        videos = [v for v in videos if v.url is not None]  # filter out None urls (possible premium access)
        for video in videos:
            try:
                self.download_video(video)
            except Exception as e:
                typer.secho(f"Error while downloading video {video.title} from course {course}: {e}", fg=typer.colors.RED)

    def download_all_courses_videos(self) -> None:  # pragma: no cover
        """main function to download all courses videos"""

        p = sync_playwright().start()
        proxy = {"server": self.conf.proxy} if self.conf.proxy else None
        browser = p.firefox.launch(headless=True, proxy=proxy)  # type: ignore
        try:
            page = self.execute_login(browser)  # type: ignore
            enrolled_courses = [utils.format_course(course) for course in self.list_courses(page)]
            if "all" in self.conf.courses:
                courses = enrolled_courses
            elif enrolled_courses:
                courses = [c for c in enrolled_courses if any(substring in c for substring in self.conf.courses)]
            else:
                courses = enrolled_courses
            typer.echo("Selected courses for download:")
            typer.echo("\n".join(courses))
            for course in courses:
                self.download_course_videos(page, course)
            _ = page.close()
        except Exception as e:
            typer.secho(f"Error while running kadenze-dl: {e}", fg=typer.colors.RED)
        finally:
            browser.close()
            p.stop()


def random_wait():  # pragma: no cover
    time.sleep(randint(5, 8))
