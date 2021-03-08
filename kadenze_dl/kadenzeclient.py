import asyncio
import logging
import os
from random import randint
from typing import List

from playwright._impl._browser import Browser, Page
from playwright.async_api import async_playwright

import kadenze_dl.helpers as helpers
from kadenze_dl.settings import Settings

logger = logging.getLogger("logger")
logger.setLevel(logging.WARNING)

BASE_URL = "https://www.kadenze.com"
conf = Settings()


async def log(message: str):
    print(message)


async def execute_login(browser: Browser) -> Page:
    await log("Signing in www.kadenze.com ...")
    page = await browser.new_page()
    await page.goto(BASE_URL)
    await page.click("#email-login-btn")
    await page.fill("input#login_user_email", conf.login)
    await page.fill("input#login_user_password", conf.password)
    await asyncio.sleep(randint(3, 8))
    await page.click("//*[@id='login_user']/button")
    await asyncio.sleep(randint(3, 8))
    return page


async def list_courses(page: Page) -> List[str]:
    try:
        await page.goto(BASE_URL + "/my_courses")
        await page.click("text=View all")
        await asyncio.sleep(randint(3, 8))
        div_courses = await page.query_selector("div#my_courses")
        json_courses = await div_courses.get_attribute("data-courses-data")
        courses = helpers.get_courses_from_json(json_courses)
    except Exception:
        await log("Course page not found, maybe check your login/password.")
        courses = []
    return courses


async def list_sessions(page: Page, course: str) -> List[str]:
    sessions_url = "/".join((BASE_URL, "courses", course, "sessions"))
    await page.goto(sessions_url)
    div_sessions = await page.query_selector("div#lectures_json")
    json_sessions = await div_sessions.get_attribute("data-lectures-json")
    sessions = helpers.get_sessions_from_json(json_sessions)
    return sessions


async def extract_videos(page: Page, url: str) -> str:
    await page.goto(BASE_URL + url)
    div_videos = await page.query_selector("#video_json")
    json_videos = await div_videos.get_attribute("value")
    return json_videos


def download_videos_per_session(course: str, session_num: int, session: str, session_videos: List[str], videos_titles: List[str]):
    print("Parsing session: {0}".format(session))
    for i, video_url in enumerate(session_videos):
        filename = helpers.extract_filename(video_url)
        if i == 0:
            session_prefix = helpers.extract_session_prefix(filename)
            session_prefixed = session_prefix + "-" + session
            full_path = conf.path + "/" + course + "/" + session_prefixed
            os.makedirs(full_path, exist_ok=True)
        if conf.videos_titles:
            filename = helpers.get_video_title(session_num, i, videos_titles, filename)
        helpers.write_video(video_url, full_path, filename)


async def download_course_videos(page: Page, course: str):
    sessions = await list_sessions(page, course)
    json_videos = [await extract_videos(page, url) for url in sessions]
    videos = [helpers.get_videos_from_json(json_video, conf.video_format) for json_video in json_videos]
    videos_titles = [helpers.get_videos_titles_from_json(json_video) for json_video in json_videos]
    videos_per_sessions = zip(sessions, videos)
    for session_num, (session_data, session_videos) in enumerate(videos_per_sessions):
        session_data = session_data.replace("courses/", "").replace("sessions/", "")
        course, session = session_data.split("/")[-2], session_data.split("/")[-1]
        download_videos_per_session(course, session_num, session, session_videos, videos_titles)


async def download_all_courses_videos():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        page = await execute_login(browser)
        enrolled_courses = [helpers.format_course(course) for course in await list_courses(page)]
        if conf.selected_only and enrolled_courses:
            courses = [c for c in enrolled_courses if any(substring in c for substring in conf.courses)]
        else:
            courses = enrolled_courses
        await log("Selected courses for download: ")
        await log("\n".join(courses))
        for course in courses:
            await log(f"Parsing course: {course}")
            await download_course_videos(page, course)
        await log("Closing browser...")
        await page.close()
        await browser.close()
        await asyncio.sleep(1)
