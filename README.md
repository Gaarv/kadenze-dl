kadenze-dl
===

Small application to download Kadenze (https://www.kadenze.com) videos for courses you enrolled in.

It scrapes the site content based on your profile information given in the configuration file to download H264 720p videos courses.

I made it in order to have offline access to this great online course : (https://www.kadenze.com/courses/creative-applications-of-deep-learning-with-tensorflow/info), check it out !


Install
---

For now, download and unzip package. Will be on PyPI when finalized.

Install requirements (Python 3):
  
    pip install -r requirements.txt

Usage 
---

Replace placeholder fields in the configuration file in YAML format, example :

    kadenze:
        login: "myemail@gmail.com"
        password: "mypassword"
    download:
        path: "/home/user/videos/kadenze"
        courses:
            - "physics-based-sound-synthesis-for-games-and-interactive-systems-iv"
            - "creative-applications-of-deep-learning-with-tensorflow-i"

course name should be as it appears in the URL, examples :

    https://www.kadenze.com/courses/physics-based-sound-synthesis-for-games-and-interactive-systems-iv
    https://www.kadenze.com/courses/creative-applications-of-deep-learning-with-tensorflow-iv

In configuration.yml :
    
    courses:
       - "physics-based-sound-synthesis-for-games-and-interactive-systems-iv"
       - "creative-applications-of-deep-learning-with-tensorflow-i"

Run the application :

	python kadenze-dl.py

Notes
---
You must be enrolled in the course for which you want to download related videos.

Please be fair to Kadenze and keep the videos for offline and personal use only, do not redistribute them

Videos already present in the same path but incomplete are re-downloaded at the next run

Credits
---
Thanks to [Vladimir Ignatyev](https://gist.github.com/vladignatyev) for the progress console bar :
https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
