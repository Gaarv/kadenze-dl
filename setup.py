from setuptools import setup, find_packages

setup(
    name="kadenze-dl",
    version="1.1.0",
    description="Small application to download Kadenze (https://www.kadenze.com) videos for courses you enrolled in",
    author="Gaarv",
    author_email="gaarv@users.noreply.github.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    url="https://github.com/gaarv/kadenze-dl",
    keywords=["kadenze", "download", "videos"],
    packages=find_packages(),
    python_requires=">=3.8, <4",
)
