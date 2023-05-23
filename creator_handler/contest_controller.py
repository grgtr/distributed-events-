from dotenv import load_dotenv
from os import environ
from distributedEvents.settings import BASE_DIR
import requests

load_dotenv(BASE_DIR / '.env')

config = {
    "baseUrl": "https://api.contest.yandex.net/api/public/v2",

    "headers": {"Authorization": f"OAuth {environ['YANDEX_TOKEN']}"}
}


def have_access(contest_id) -> bool:
    result = requests.get(config["baseUrl"] + f"/contests/{contest_id}", headers=config["headers"])
    return result.ok


def get_standings(contest_id):
    result = requests.get(config["baseUrl"] + f"/contests/{contest_id}/standings", headers=config["headers"])
    if not result.ok:
        print("REQUEST ERROR")
        return []
    result = result.json()
    return result.get("rows")


def get_participants(contest_id):
    result = requests.get(config["baseUrl"] + f"/contests/{contest_id}/standings", headers=config["headers"])
    print(result)
    if not result.ok:
        print("REQUEST ERROR")
        return []
    result = result.json()
    return result.get("rows")