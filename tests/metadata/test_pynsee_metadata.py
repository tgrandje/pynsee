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
    module_patch,
    mock_requests_session,
    mock_pool,
    mock_request_insee,
    mock_requests_get_from_session,
    mock_requests_post_from_session,
)


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
@module_patch(
    "pynsee.metadata.get_definition._request_insee",
    side_effect=mock_request_insee,
)
@module_patch(
    "pynsee.metadata.get_definition_list._request_insee",
    side_effect=mock_request_insee,
)
@module_patch(
    "pynsee.metadata.get_legal_entity._request_insee",
    side_effect=mock_request_insee,
)
# @module_patch(
#     "pynsee.metadata.get_operation._request_insee",
#     side_effect=mock_request_insee,
# )
class TestMetadata(TestCase):
    def test_get_legal_entity(self, *args):
        data = get_legal_entity(codes=["5599", "83"])
        self.assertTrue(isinstance(data, pd.DataFrame))

    def test_get_definition_list(self, *args):
        data = get_definition_list()
        self.assertTrue(isinstance(data, pd.DataFrame))

    def test_get_definition(self, *args):
        data = get_definition(ids=["c1020", "c1601"])
        self.assertTrue(isinstance(data, pd.DataFrame))
        data = get_definition(ids="c1020")
        self.assertTrue(isinstance(data, pd.DataFrame))

    def test_get_activity_list(self, *args):
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
