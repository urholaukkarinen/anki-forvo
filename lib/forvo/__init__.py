import json
import requests
from requests.compat import urljoin

FORVO_API_BASE_URL = "https://apifree.forvo.com"


class Forvo(object):

    def __init__(self, api_key):
        self.api_key = api_key

    def get_word_pronunciations(self, word, limit=None):
        params = {
            "key": self.api_key,
            "limit": limit,
            "action": "word-pronunciations",
            "format": "json",
            "word": word
        }

        url = urljoin(FORVO_API_BASE_URL, "/".join(["{}/{}".format(key, value) for key, value in params.items() if value]))

        response = requests.get(url)

        if response.status_code is not 200:
            return []

        result_json = json.loads(response.text)

        if "items" not in result_json:
            return []

        return result_json["items"]

    def get_languages(self):
        pass
