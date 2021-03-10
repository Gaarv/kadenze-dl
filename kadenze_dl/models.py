from typing import NamedTuple


class Session(NamedTuple):
    course: str
    index: int
    name: str
    path: str


class Video(NamedTuple):
    session: Session
    index: int
    title: str
    url: str
