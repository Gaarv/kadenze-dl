from distutils.core import setup

setup(
    name='kadenze-dl',
    packages=['kadenze-dl'],
    version='1.0',
    description='Small application to download Kadenze (https://www.kadenze.com) videos for courses you enrolled in',
    author='Gaarv',
    author_email='gaarv@users.noreply.github.com',
    url='https://github.com/gaarv/kadenze-dl',
    download_url='https://github.com/gaarv/kadenze-dl/tarball/1.0',
    keywords=['kadenze', 'download', 'videos'],
    classifiers=[],
    install_requires=[
        "requests==2.10.0",
        "robobrowser==0.5.3",
        "PyYAML==3.12",
        "lxml==3.6.4"
    ],
)
