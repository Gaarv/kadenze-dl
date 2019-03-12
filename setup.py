from setuptools import setup

setup(
    name='kadenze-dl',
    packages=['kadenze-dl'],
    version='1.0',
    description='Small application to download Kadenze (https://www.kadenze.com) videos for courses you enrolled in',
    author='Gaarv',
    author_email='gaarv@users.noreply.github.com',
    url='https://github.com/gaarv/kadenze-dl',
    keywords=['kadenze', 'download', 'videos'],
    install_requires=[
        "requests==2.20.0",
        "robobrowser==0.5.3",
        "PyYAML==3.12",
        "lxml==4.2.1",
        "python-slugify==1.2.5"
    ],
)
