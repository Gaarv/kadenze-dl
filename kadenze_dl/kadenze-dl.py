import asyncio
import subprocess

import kadenze_dl.kadenzeclient as kadenze_client


async def main():
    await kadenze_client.download_all_courses_videos()


if __name__ == "__main__":
    subprocess.run(["playwright", "install"])
    asyncio.run(main())
