# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 15:54:21 2023

@author: thomas.grandjean
"""

import logging
import os
import urllib3
import requests
from requests_cache import CachedSession
import time
import warnings
import importlib
from unittest import mock

import pynsee
from pynsee.utils._get_token import _get_token
from pynsee.utils._get_credentials import _get_credentials
from pynsee.utils._wait_api_query_limit import _wait_api_query_limit

logger = logging.getLogger(__name__)


def mock_pool(*args, **kwargs):
    class MockedPool:
        def __init__(
            self,
            processes=None,
            initializer=None,
            initargs=(),
            maxtasksperchild=None,
        ):
            self.initializer = initializer
            self.initargs = initargs

        def imap(self, func, iterable, chunksize=1):
            for args in iterable:
                if self.initializer:
                    self.initializer(*self.initargs)
                yield func(args)

        def __enter__(self, *args, **kwargs):
            return self

        def __exit__(self, *args, **kwargs):
            pass

    return MockedPool(*args, **kwargs)


class MockedSession(CachedSession):
    def __init__(self, *args, **kwargs):
        super().__init__(
            cache_name="pynsee-tests.sqlite",
            expire_after=3600 * 24 * 15,
            ignored_parameters=("Authorization", "access_token"),
            filter_fn=lambda session: "api.insee.fr/token" not in session.url,
            allowable_codes=(200, 401, 403, 404),
            *args,
            **kwargs,
        )

    def get(self, *args, **kwargs):
        r = super().get(*args, **kwargs)
        if not r.from_cache:
            print(
                f"{args[0]}, code={r.status_code}, from_cache={r.from_cache}"
            )
        return r

    def post(self, *args, **kwargs):
        r = super().post(*args, **kwargs)
        if not r.from_cache:
            print(
                f"{args[0]}, code={r.status_code}, from_cache={r.from_cache}"
            )
        return r


def mock_requests_session(*args, **kwargs):
    return MockedSession(*args, **kwargs)


SESSION = MockedSession()


def mock_requests_get(*args, **kwargs):
    return SESSION.get(*args, **kwargs)


def mock_requests_post(*args, **kwargs):
    return SESSION.post(*args, **kwargs)


_get_credentials()

insee_key = pynsee._config["insee_key"]
insee_secret = pynsee._config["insee_secret"]
token = _get_token(insee_key, insee_secret)

pynsee._config["hide_progress"] = True

proxies = {
    "http": os.environ.get("http_proxy", pynsee._config["http_proxy"]),
    "https": os.environ.get("https_proxy", pynsee._config["https_proxy"]),
}


def mock_request_insee(
    api_url=None, sdmx_url=None, file_format="application/xml", *args, **kwargs
):
    # print("mocked !")
    # print("=" * 50)
    with warnings.catch_warnings():
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # force sdmx use with a system variable
        try:
            pynsee_use_sdmx = os.environ["pynsee_use_sdmx"]
            if pynsee_use_sdmx == "True":
                api_url = None
        except Exception:
            pass

        # if api_url is provided, it is used first,
        # and the sdmx url is used as a backup in two cases
        # 1- when the token is missing
        # 2- if the api request fails

        # if api url is missing sdmx url is used

        if api_url is not None:
            headers = {
                "Accept": file_format,
                "Authorization": "Bearer " + token,
            }

            results = requests.get(
                api_url, proxies=proxies, headers=headers, verify=False
            )
            if not results.from_cache:
                # avoid reaching the limit of 30 queries/minute from insee api
                _wait_api_query_limit(api_url)

            success = True

            code = results.status_code

            if code == 429:
                time.sleep(10)

                request_again = mock_request_insee(
                    api_url=api_url, sdmx_url=sdmx_url, file_format=file_format
                )

                return request_again

            elif code in pynsee.utils._request_insee.CODES:
                msg = (
                    f"Error {code} - {pynsee.utils._request_insee.CODES[code]}"
                    f"\nQuery:\n{api_url}"
                )
                raise requests.exceptions.RequestException(msg)
            elif code != 200:
                success = False

            if success is True:
                return results
            else:
                msg = (
                    "An error occurred !\n"
                    "Query : {api_url}\n"
                    f"{results.text}\n"
                    "Make sure you have subscribed to all APIs !\n"
                    "Click on all APIs' icons one by one, select your "
                    "application, and click on Subscribe"
                )
                raise requests.exceptions.RequestException(msg)

        else:
            # api_url is None
            if sdmx_url is not None:
                results = requests.get(sdmx_url, proxies=proxies, verify=False)

                if results.status_code == 200:
                    return results
                else:
                    raise ValueError(results.text + "\n" + sdmx_url)

            else:
                raise ValueError("!!! Error : urls are missing")


def module_patch(*args, **kwargs):
    """
    Patch allowing to call function from module with same name.
    To be used instead of @mock.patch(...) : @module_patch(...)
    Original source:
        https://stackoverflow.com/questions/52324568/#answer-52350820
    """
    target = args[0]
    components = target.split(".")
    for i in range(len(components), 0, -1):
        try:
            # attempt to import the module
            imported = importlib.import_module(".".join(components[:i]))

            # module was imported, let's use it in the patch
            patch = mock.patch(*args, **kwargs)
            patch.getter = lambda: imported
            patch.attribute = ".".join(components[i:])
            return patch
        except Exception:
            pass

    # did not find a module, just return the default mock
    return mock.patch(*args, **kwargs)
