# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import unittest
from unittest import mock
from unittest import TestCase
import requests
from functools import partial

import os

import pynsee
from pynsee.utils._get_token import _get_token
from pynsee.utils._get_envir_token import _get_envir_token
from pynsee.utils._get_credentials import _get_credentials
from pynsee.utils._request_insee import _request_insee
from pynsee.utils.clear_all_cache import clear_all_cache
from pynsee.utils.init_conn import init_conn

from tests.mockups import (
    mock_requests_session,
    mock_pool,
    mock_request_insee,
    mock_requests_get_from_session,
    mock_requests_post_from_session,
)


test_SDMX = True


mock_request_session_local = partial(
    mock_requests_session, cache_name=__name__
)

SESSION = mock_request_session_local()
mock_requests_get = partial(mock_requests_get_from_session, session=SESSION)
mock_requests_post = partial(mock_requests_post_from_session, session=SESSION)


@mock.patch("multiprocessing.Pool", side_effect=mock_pool)
@mock.patch("requests.Session", side_effect=mock_request_session_local)
@mock.patch("requests.get", side_effect=mock_requests_get)
@mock.patch("requests.post", side_effect=mock_requests_post)
class TestUtils(TestCase):
    _get_credentials()
    StartKeys = pynsee._config

    def test_get_token(
        self, patch1, patch2, patch3, patch4, StartKeys=StartKeys
    ):
        insee_key = StartKeys["insee_key"]
        insee_secret = StartKeys["insee_secret"]

        init_conn(insee_key=insee_key, insee_secret=insee_secret)
        _get_credentials()

        token = _get_token(insee_key, insee_secret)
        self.assertTrue((token is not None))

    def test_request_insee_1(self, *args):
        # test both api and sdmx queries fail but token is not none
        sdmx_url = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/test"
        api_url = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/test"

        def request_insee_test(sdmx_url=sdmx_url, api_url=api_url):
            _request_insee(sdmx_url=sdmx_url, api_url=api_url)

        self.assertRaises(
            requests.exceptions.RequestException, request_insee_test
        )

    if test_SDMX:

        def test_request_insee_2(self, *args):
            # if credentials are not well provided but sdmx url works
            clear_all_cache()

            os.environ["insee_token"] = "test"
            os.environ["insee_key"] = "key"
            os.environ["insee_secret"] = "secret"
            sdmx_url = (
                "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/001688370"
            )
            api_url = (
                "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/001688370"
            )

            results = _request_insee(api_url=api_url, sdmx_url=sdmx_url)
            test = results.status_code == 200
            self.assertTrue(test)

    def test_request_insee_3(self, *args):
        # token is none and sdmx query fails
        def init_conn_foo():
            init_conn(insee_key="test", insee_secret="test")

        self.assertRaises(ValueError, init_conn_foo)

        _get_token.cache_clear()
        _get_envir_token.cache_clear()

        os.environ["insee_token"] = "test"
        os.environ["insee_key"] = "key"
        os.environ["insee_secret"] = "secret"
        sdmx_url = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/test"
        api_url = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/test"

        def request_insee_test(sdmx_url=sdmx_url, api_url=api_url):
            _request_insee(sdmx_url=sdmx_url, api_url=api_url)

        self.assertRaises(ValueError, request_insee_test)

    def test_request_insee_4(self, *args):
        # token is none and sdmx query is None
        # _get_token.cache_clear()
        # _get_envir_token.cache_clear()
        clear_all_cache()

        os.environ["insee_token"] = "test"
        os.environ["insee_key"] = "key"
        os.environ["insee_secret"] = "secret"
        api_url = "https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/test"

        def request_insee_test(sdmx_url=None, api_url=api_url):
            _request_insee(sdmx_url=sdmx_url, api_url=api_url)

        self.assertRaises(ValueError, request_insee_test)

    def test_request_insee_5(self, *args):
        # api query is none and sdmx query fails
        sdmx_url = "https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/test"

        def request_insee_test(sdmx_url=sdmx_url, api_url=None):
            _request_insee(sdmx_url=sdmx_url, api_url=api_url)

        self.assertRaises(ValueError, request_insee_test)

    def test_get_envir_token(self, *args):
        _get_envir_token.cache_clear()
        os.environ["insee_token"] = "a"
        token = _get_envir_token()
        test = token is None
        self.assertTrue(test)

    def test_clear_all_cache(self, *args):
        test = True
        try:
            clear_all_cache()
        except BaseException:
            test = False
        self.assertTrue(test)


if __name__ == "__main__":
    unittest.main()
