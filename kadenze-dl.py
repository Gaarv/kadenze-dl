from kadenzeclient import KadenzeClient


def main():
    client = KadenzeClient()
    client.download_all_courses_videos()


if __name__ == '__main__':
    main()
