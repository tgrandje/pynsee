# Copyright : INSEE, 2021

import os
import requests
import urllib3
from functools import lru_cache

import pynsee


@lru_cache(maxsize=None)
def _get_envir_token():
    proxies = {
        "http": os.environ.get("http_proxy", pynsee._config["http_proxy"]),
        "https": os.environ.get("https_proxy", pynsee._config["https_proxy"])
    }

    try:
        token = os.environ["insee_token"]
        headers = {"Accept": "application/xml", "Authorization": "Bearer " + token}
        url_test = "https://api.insee.fr/series/BDM/V1/data/CLIMAT-AFFAIRES"
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        request_test = requests.get(url_test, proxies=proxies, headers=headers, verify=False)
        if request_test.status_code != 200:
            raise ValueError("Token from python environment is not working")
    except Exception:
        token = None

    return token
