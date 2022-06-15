![Build Status](https://github.com/gaarv/kadenze-dl/actions/workflows/test.yml/badge.svg)

kadenze-dl
===

Small application to download Kadenze (https://www.kadenze.com) videos for courses you enrolled in.

Download videos for offline usage / archive based on your profile information given in the configuration file to download videos courses.


## Install (Docker)

Image size is 1.86GB.

    docker pull <repository/image>

## Install (from sources)

Preferably in a virtual environment, install package (Python >=3.8). Download or clone repository, then into root directory:

    pip3 install -U .


## Usage (Docker)

    docker run --rm \
        -v /path/to/download:/tmp/download \
        -v /absolute/path/to/configuration.yml:/app/configuration.yml \
        <repository/image> ./kadenze-dl --config-file /app/configuration.yml


## Usage (from sources)

Change directory to `kadenze_dl`:

    cd kadenze_dl/


Run the app, example:

    python3 kadenze-dl.py --login "myemail@gmail.com" --password "mypassword" --download-path /home/user/videos/kadenze


## Configuration file

A YAML configuration file can also be used, template is available as `configuration.yml` in `kadenze_dl` directory:

    python3 kadenze-dl.py --config-file configuration.yml


Replace placeholder fields in the configuration file in YAML format, example:

    kadenze:
        login: "myemail@gmail.com"
        password: "mypassword"
    download:
        proxy: ""                                      # Proxy URL, ie. "http://127.0.0.1:3128". Empty string "" if none.
        resolution: "720"                              # Video resolution to download. Valid values are "720" or "360".
        download_path: "/home/user/videos/kadenze"     # The absolute path to download to
        courses:                                       # Courses to download, as they appear in the URL. You can also use the keyword "all"
                - "creative-applications-of-deep-learning-with-tensorflow-i"
                - "physics-based-sound-synthesis-for-games-and-interactive-systems-iv"


Courses names must be reported as they appears in the URL, examples:

    https://www.kadenze.com/courses/creative-applications-of-deep-learning-with-tensorflow-i
    https://www.kadenze.com/courses/physics-based-sound-synthesis-for-games-and-interactive-systems-iv


In configuration.yml:
    
    courses:
       - "creative-applications-of-deep-learning-with-tensorflow-i"
       - "physics-based-sound-synthesis-for-games-and-interactive-systems-iv"


You can also use:

    courses:
       - "all"

To download all courses listed in your "Home" page (including archived ones).

For manual selected courses, you can get links from the "Home" page of your account or from the "Dashboard" URL on the left panel inside a course.

![Home](./images/kadenze1.png)

![Dashboard](./images/kadenze2.png)


## Help

List all commands available with 

    python3 kadenze-dl.py --help


## Notes

- kadenze-dl only support login from email / password.
- you must be enrolled in the course for which you want to download related videos as they need to appear in your account. 
- **please be fair to Kadenze** and keep the videos for offline and personal use only, do not redistribute them
- videos already present in the same path but incomplete are re-downloaded at the next run


## Credits

Thanks to [Vladimir Ignatyev](https://gist.github.com/vladignatyev) for the progress console bar :
https://gist.github.com/vladignatyev/06860ec2040cb497f0f3