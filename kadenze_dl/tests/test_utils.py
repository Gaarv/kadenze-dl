from pathlib import Path

import kadenze_dl.utils as utils
from kadenze_dl.models import Session

TEST_DATA_PATH = Path(".").absolute().joinpath("kadenze_dl", "tests", "data")


def test_format_course():
    courses_data = TEST_DATA_PATH.joinpath("data-courses-data.json").read_text()
    courses = utils.get_courses_from_json(courses_data)
    formatted_courses = [utils.format_course(course) for course in courses]
    expected_courses = [
        "physics-based-sound-synthesis-for-games-and-interactive-systems-iv",
        "machine-learning-for-musicians-and-artists-v",
        "introduction-to-programming-for-the-visual-arts-with-p5-js-vi",
        "real-time-audio-signal-processing-in-faust",
        "creative-applications-of-deep-learning-with-tensorflow-i",
        "creative-applications-of-deep-learning-with-tensorflow-iv",
    ]
    assert formatted_courses == expected_courses


def test_extract_filename():
    video_url = (
        "https://cdnc-prod-assets-private.kadenze.com/uploads/lecture_medium/4894/file/Reb_L5_720.mp4?Expires"
        "=1482662443\u0026Signature=QklHU9hV7z2gwVp9yYfN21IITWxPZnPa7c3QOUByerXthMHnGy7-PfWvw~jrk5bE6sNtj2uee"
        "gCiGNsusW3ummw0zQoNzO4e592eduSgP6SuN0axaqsdqiYGHHDG0dExRD~DepPmG1vSat2lJ3d8SOA0mYOfYMYz5Qk-oJd-wRHsx"
        "LQPKLhTW5sOD6OjSSajr7Qruu0s5Ej-5WKm4XLdLORz6q~OJEnye~ra~HsXhxqOfEDxoUYojvQZZNVdSRXUSZigEJ7vgYyNop-N7"
        "~HVRUGjXU~Z~NsB3LtFctaEvoNWd3CMVH~zwHmTKEF1rmDDb2To~ABS6t8sXREUdZ36pQ__\u0026Key-Pair-Id=APKAIPB43QU"
        "CA2NXZVSQmp4"
    )
    filename = utils.extract_filename(video_url)
    assert filename == "Reb_L5_720.mp4"


def test_get_courses_from_json():
    courses_data = TEST_DATA_PATH.joinpath("data-courses-data.json").read_text("utf-8")
    courses = utils.get_courses_from_json(courses_data)
    assert len(courses) == 6


def test_get_sessions_from_json():
    sessions_data = TEST_DATA_PATH.joinpath("data-lectures-json.json").read_text("utf-8")
    courses = utils.get_sessions_from_json(sessions_data, course="real-time-audio-signal-processing-in-faust")
    assert len(courses) == 5


def test_get_videos_from_json():
    videos_data = TEST_DATA_PATH.joinpath("video_json.json").read_text("utf-8")
    session = Session(
        course="real-time-audio-signal-processing-in-faust",
        index=1,
        name="faust-overview-and-language-basics",
        path="/courses/real-time-audio-signal-processing-in-faust/sessions/faust-overview-and-language-basics",
    )
    videos_360 = utils.get_videos_from_json(videos_data, 360, session)
    videos_720 = utils.get_videos_from_json(videos_data, 720, session)
    assert len(videos_360) == 10
    assert len(videos_720) == 10
    assert len(videos_360) == max(v.index for v in videos_360)
    assert len(videos_720) == max(v.index for v in videos_720)


def test_get_video_title():
    videos_data = TEST_DATA_PATH.joinpath("video_json.json").read_text("utf-8")
    session = Session(
        course="real-time-audio-signal-processing-in-faust",
        index=1,
        name="faust-overview-and-language-basics",
        path="/courses/real-time-audio-signal-processing-in-faust/sessions/faust-overview-and-language-basics",
    )
    videos = utils.get_videos_from_json(videos_data, 720, session)
    videos_titles = [utils.get_video_title(v.title, utils.extract_filename(v.url)) for v in videos]  # type: ignore
    videos_titles_expected = [
        "Faust_C1_S1_1_V2_1080_2700kp_introduction.mp4",
        "Faust_C1_S1_2_V2_1080_2700kp_faust-online-editor.mp4",
        "Faust_C1_S1_3_V2_1080_2700kp_first-faust-program.mp4",
        "Faust_C1_S1_4_V2_1080_2700kp_adding-a-reverb.mp4",
        "Faust_C1_S1_5_V2_1080_2700kp_automating-triggering-and-generating-a-mobile-app.mp4",
        "Faust_C1_S1_6_V2_1080_2700kp_using-a-sawtooth-oscillator.mp4",
        "Faust_C1_S1_7_V2_1080_2700kp_breath-control.mp4",
        "Faust_C1_S1_8_V2_1080_2700kp_additive-synthesizer.mp4",
        "Faust_C1_S1_9_V2_1080_2700kp_polyphonic-midi-synthesizer.mp4",
        "Faust_C1_S1_10_V2_1080_2700kp_polyphonic-synthesizer-and-audio-effect.mp4",
    ]
    assert videos_titles == videos_titles_expected
