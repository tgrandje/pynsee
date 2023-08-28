# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from unittest import mock
from unittest import TestCase
from pandas import pandas as pd
from functools import partial

from pynsee.metadata.get_definition_list import get_definition_list
from pynsee.metadata.get_definition import get_definition
from pynsee.metadata.get_activity_list import get_activity_list
from pynsee.metadata.get_legal_entity import get_legal_entity

from tests.mockups import (
    mock_requests_session,
    mock_pool,
    # mock_wait_api_query_limit,
)


mock_request_session_local = partial(
    mock_requests_session, cache_name=__name__
)

SESSION = mock_request_session_local()


def mock_requests_get(*args, **kwargs):
    return SESSION.get(*args, **kwargs)


def mock_requests_post(*args, **kwargs):
    return SESSION.post(*args, **kwargs)


# @mock.patch("pynsee.utils._wait_api_query_limit", side_effect=mock_wait_api_query_limit)
@mock.patch("multiprocessing.Pool", side_effect=mock_pool)
@mock.patch("requests.Session", side_effect=mock_request_session_local)
@mock.patch("requests.get", side_effect=mock_requests_get)
@mock.patch("requests.post", side_effect=mock_requests_post)
class TestMetadata(TestCase):
    def test_get_legal_entity(self, patch1, patch2, patch3, patch4):
        data = get_legal_entity(codes=["5599", "83"])
        self.assertTrue(isinstance(data, pd.DataFrame))

    def test_get_definition_list(self, patch1, patch2, patch3, patch4):
        data = get_definition_list()
        self.assertTrue(isinstance(data, pd.DataFrame))

    def test_get_definition(self, patch1, patch2, patch3, patch4):
        data = get_definition(ids=["c1020", "c1601"])
        self.assertTrue(isinstance(data, pd.DataFrame))
        data = get_definition(ids="c1020")
        self.assertTrue(isinstance(data, pd.DataFrame))

    def test_get_activity_list(self, patch1, patch2, patch3, patch4):
        test = True
        level_available = [
            "A10",
            "A21",
            "A38",
            "A64",
            "A88",
            "A129",
            "A138",
            "NAF1",
            "NAF2",
            "NAF3",
            "NAF4",
            "NAF5",
            "A5",
            "A17",
        ]
        for nomencl in level_available:
            data = get_activity_list(nomencl)
            test = test & isinstance(data, pd.DataFrame)
        self.assertTrue(test)
