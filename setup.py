from setuptools import setup

setup(
    name="kadenze-dl",
    packages=["kadenze_dl"],
    version="1.0",
    description="Small application to download Kadenze (https://www.kadenze.com) videos for courses you enrolled in",
    author="Gaarv",
    author_email="gaarv@users.noreply.github.com",
    url="https://github.com/gaarv/kadenze-dl",
    keywords=["kadenze", "download", "videos"],
    install_requires=["PyYAML==5.4.1", "requests==2.25.1", "python-slugify==4.0.1", "playwright==1.9.1"],
)
