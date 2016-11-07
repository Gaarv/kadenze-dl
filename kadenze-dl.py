from kadenzeclient import KadenzeClient


def main():
    client = KadenzeClient()
    client.download_videos_all()


if __name__ == '__main__':
    main()
