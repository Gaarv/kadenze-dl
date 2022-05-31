import time
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
COOKIES_XPATH = '//*[@id="iubenda-cs-banner"]/div/div/a'


class KadenzeClient:
    def __init__(self, settings: Settings) -> None:
        self.conf = settings

    def execute_login(self, browser: Browser) -> Page:
        typer.echo("Signing in www.kadenze.com ...")
        page: Page = browser.new_page()  # type: ignore
        _ = page.goto(BASE_URL)
        random_wait()
        _ = page.mouse.click(0, 0)  # Click popup banner
        _ = page.click(COOKIES_XPATH)  # Click cookie consent
        _ = page.click("#email-login-btn")
        _ = page.fill("input#login_user_email", self.conf.login)
        _ = page.fill("input#login_user_password", self.conf.password)
        random_wait()
        _ = page.click("//*[@id='login_user']/button")
        random_wait()
        return page

    def list_courses(self, page: Page) -> List[str]:
        try:
            _ = page.goto(BASE_URL + "/my_courses")
            random_wait()
            _ = page.click("text=View all")
            random_wait()
            div_courses = page.query_selector("div#my_courses")
            json_courses = div_courses.get_attribute("data-courses-data")  # type: ignore
            courses = utils.get_courses_from_json(json_courses)
        except Exception as e:
            typer.secho(f"Error while listing courses: {e}", fg=typer.colors.RED)
            courses = []
        return courses

    def extract_sessions(self, page: Page, course: str) -> List[Session]:
        sessions = []
        typer.echo(f"Parsing course: {course}")
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
            typer.secho(f"Error while extracting sessions from course {course}: {e}", fg=typer.colors.RED)
        return sessions

    def extract_session_videos(self, page: Page, session: Session) -> List[Video]:
        videos = []
        typer.echo(f"Parsing session: {session.name}")
        try:
            _ = page.goto(BASE_URL + session.path)
            random_wait()
            div_videos = page.query_selector('//*[@id="video_json"]')
            json_videos = div_videos.get_attribute("value")  # type: ignore
            videos = utils.get_videos_from_json(json_videos, self.conf.resolution.value, session)
        except Exception:
            typer.secho(f"Error while extracting videos from session={session.name}. Skipping...", fg=typer.colors.RED)
        return videos

    def download_video(self, video: Video) -> None:
        filename = utils.extract_filename(video.url)
        download_path = self.conf.download_path
        if filename and download_path:
            session_prefix = str(video.session.index) + "-" + video.session.name
            full_path = download_path / video.session.course / session_prefix
            full_path.mkdir(parents=True, exist_ok=True)
            filename = utils.get_video_title(video.title, filename)
            utils.write_video(video.url, full_path, filename)
        else:
            typer.secho(
                f"Could not extract filename: video={video.title}, session={video.session.name}, course={video.session.course}. Skipping...",
                fg=typer.colors.BLUE,
            )

    def download_course_videos(self, page: Page, course: str) -> None:
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

    def download_all_courses_videos(self) -> None:
        """main function to download all courses videos"""

        p = sync_playwright().start()
        browser = p.firefox.launch(headless=True)
        try:
            page = self.execute_login(browser)  # type: ignore
            enrolled_courses = [utils.format_course(course) for course in self.list_courses(page)]
            if enrolled_courses:
                courses = [c for c in enrolled_courses if any(substring in c for substring in self.conf.courses)]
            else:
                courses = enrolled_courses
            typer.echo("Selected courses for download:\n")
            typer.echo("\n".join(courses))
            for course in courses:
                self.download_course_videos(page, course)
            _ = page.close()
        except Exception as e:
            typer.secho(f"Error while running kadenze-dl: {e}", fg=typer.colors.RED)
        finally:
            browser.close()
            p.stop()


def random_wait():
    time.sleep(randint(5, 8))
