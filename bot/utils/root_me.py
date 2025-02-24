import asyncio
from urllib.parse import urlparse

from aiohttp import ClientSession
from bs4 import BeautifulSoup


async def fetch(session, url):
    """Aсинхронный GET запрос"""
    async with session.get(url, ssl=False) as response:
        return await response.text()


async def get_rootme_profile(nickname: str) -> str:
    async with ClientSession() as session:
        profile_link = f"https://www.root-me.org/{nickname}?lang=en"
        return await fetch(session, profile_link)


async def get_solved_tasks_of_student(nickname: str) -> list[str]:
    html = await get_rootme_profile(nickname)
    soup = BeautifulSoup(html, "html.parser")
    tasks = soup.find_all(
        "a",
        href=lambda href: href and "fr/Challenges/" in href,
        title=lambda title: not title,
    )
    task_names = [task.text for task in tasks]
    return task_names


def scribe_root_me(root_me_link: str):
    """
    Спарсить никнейм с ссылки профиля ROOT-ME.

    пример:
        Input: https://www.root-me.org/Banzai-443597?lang=ru
        Output: Banzai-443597
    """
    # Parse the URL
    parsed_url = urlparse(root_me_link)

    # Extract the path and split it
    path_parts = parsed_url.path.strip("/").split("/")

    # The nickname is typically the last part of the path
    if path_parts:
        return path_parts[-1]
    else:
        raise ValueError("No valid nickname found in the URL.")


if __name__ == "__main__":
    """Example of usage."""

    names = asyncio.run(get_solved_tasks_of_student("DarkMK692"))
    print(names)
