import subprocess

import kadenze_dl.kadenzeclient as kadenze_client


def main():
    subprocess.run(["playwright", "install"])
    kadenze_client.download_all_courses_videos()


if __name__ == "__main__":
    main()
