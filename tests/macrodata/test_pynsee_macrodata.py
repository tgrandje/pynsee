# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import unittest
from unittest import mock
from unittest import TestCase
from pandas import pandas as pd
import os
from datetime import datetime
from datetime import timedelta
from functools import partial

from pynsee.macrodata._get_insee import _get_insee
from pynsee.macrodata._get_date import _get_date
from pynsee.macrodata._get_idbank_internal_data_harmonized import (
    _get_idbank_internal_data_harmonized,
)
from pynsee.macrodata._get_idbank_internal_data import (
    _get_idbank_internal_data,
)
from pynsee.macrodata._get_dataset_metadata import _get_dataset_metadata
from pynsee.macrodata._get_dataset_dimension import _get_dataset_dimension
from pynsee.macrodata._get_dimension_values import _get_dimension_values
from pynsee.macrodata._download_idbank_list import _download_idbank_list
from pynsee.macrodata._get_dataset_list_internal import (
    _get_dataset_list_internal,
)

from pynsee.macrodata.get_series_list import get_series_list
from pynsee.macrodata.get_dataset_list import get_dataset_list
from pynsee.macrodata.get_last_release import get_last_release

from pynsee.macrodata.get_series import get_series
from pynsee.macrodata.get_dataset import get_dataset

from pynsee.macrodata.get_column_title import get_column_title
from pynsee.macrodata.get_series_title import get_series_title
from pynsee.macrodata.search_macrodata import search_macrodata

from pynsee.utils._clean_insee_folder import _clean_insee_folder

from tests.mockups import (
    mock_requests_session,
    mock_pool,
    # mock_wait_api_query_limit,
)


test_SDMX = True


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
class TestMacrodata(TestCase):
    def test_get_dataset_list_internal(self, patch1, patch2, patch3, patch4):
        df = _get_dataset_list_internal()
        self.assertTrue(isinstance(df, pd.DataFrame))

    def test_download_series_list(self, patch1, patch2, patch3, patch4):
        # _clean_insee_folder()
        df = _download_idbank_list()
        self.assertTrue(isinstance(df, pd.DataFrame))

    def test_get_series_title(self, patch1, patch2, patch3, patch4):
        series = search_macrodata()
        series = series.loc[:420, "IDBANK"].to_list()
        titles = get_series_title(series)
        self.assertTrue(isinstance(titles, pd.DataFrame))

    def test_get_dataset_list(self, patch1, patch2, patch3, patch4):
        data = get_dataset_list()
        self.assertTrue(isinstance(data, pd.DataFrame))

    def test_get_column_title_1(self, patch1, patch2, patch3, patch4):
        _clean_insee_folder()
        data1 = get_column_title()
        test1 = isinstance(data1, pd.DataFrame)

        data2 = get_column_title(["CLIMAT-AFFAIRES", "IPC-2015"])
        test2 = isinstance(data2, pd.DataFrame)
        self.assertTrue(test1 & test2)

    def test_get_column_title_2(self, patch1, patch2, patch3, patch4):
        self.assertRaises(ValueError, get_column_title, dataset=["a"])

    def test_get_series_list_1(self, patch1, patch2, patch3, patch4):
        test = True
        data = get_series_list("CLIMAT-AFFAIRES")
        test = test & isinstance(data, pd.DataFrame)

        data = get_series_list("IPPI-2015", update=True)
        test = test & isinstance(data, pd.DataFrame)

        data = get_series_list("CHOMAGE-TRIM-NATIONAL", update=True)
        test = test & isinstance(data, pd.DataFrame)

        self.assertTrue(test)

    def test_get_series_list_2(self, patch1, patch2, patch3, patch4):
        self.assertRaises(ValueError, get_series_list, "a")

    def test_get_series_1(self, patch1, patch2, patch3, patch4):
        idbank_list = get_series_list("IPC-2015").iloc[:900]
        data = get_series(idbank_list.IDBANK)
        self.assertTrue(isinstance(data, pd.DataFrame))

    def test_get_series_2(self, patch1, patch2, patch3, patch4):
        data = get_series("001769682", "001769683")
        self.assertTrue(isinstance(data, pd.DataFrame))

    def test_get_series_3(self, patch1, patch2, patch3, patch4):
        data = get_series(["001769683", "001769682"], lastNObservations=1)
        self.assertTrue(isinstance(data, pd.DataFrame))

    def test_get_date(self, patch1, patch2, patch3, patch4):
        data = get_series(
            "001694056",
            "001691912",
            "001580062",
            "001688370",
            "010565692",
            "001580394",
        )
        test1 = isinstance(data, pd.DataFrame)
        test2 = _get_date(freq="TEST", time_period=3) == 3
        self.assertTrue(test1 & test2)

    def test_get_dataset_metadata_1(self, patch1, patch2, patch3, patch4):
        # test automatic update of metadata, when older than 3 months
        df = _get_dataset_metadata("CLIMAT-AFFAIRES")
        os.environ["insee_date_test"] = str(
            datetime.now() + timedelta(days=91)
        )
        df = _get_dataset_metadata("CLIMAT-AFFAIRES")
        test1 = isinstance(df, pd.DataFrame)

        # test manual update of metadata
        df = _get_dataset_metadata("CLIMAT-AFFAIRES", update=True)
        test2 = isinstance(df, pd.DataFrame)

        # test date provided manually error and switch to today
        os.environ["insee_date_test"] = "a"
        df = _get_dataset_metadata("CLIMAT-AFFAIRES")
        test3 = isinstance(df, pd.DataFrame)

        # test idbank file download crash and backup internal data
        os.environ["pynsee_idbank_file"] = "test"
        os.environ["pynsee_idbank_loop_url"] = "False"
        df = _get_dataset_metadata("CLIMAT-AFFAIRES", update=True)
        test3 = test3 & isinstance(df, pd.DataFrame)
        os.environ["pynsee_idbank_loop_url"] = "True"

        self.assertTrue(test1 & test2 & test3)

    def test_get_dataset_metadata_2(self, patch1, patch2, patch3, patch4):
        # crash download_idbank_list and test the result on get_dataset_metadata
        _clean_insee_folder()
        df = _get_dataset_metadata("CLIMAT-AFFAIRES")
        test1 = isinstance(df, pd.DataFrame)
        self.assertTrue(test1)

    def test_get_insee(self, patch1, patch2, patch3, patch4):
        data = _get_insee(
            api_query="https://api.insee.fr/series/BDM/V1/data/SERIES_BDM/001769682",
            sdmx_query="https://bdm.insee.fr/series/sdmx/data/SERIES_BDM/001769682",
        )
        test1 = isinstance(data, pd.DataFrame)

        data = _get_insee(
            api_query="https://api.insee.fr/series/BDM/V1/data/BALANCE-PAIEMENTS",
            sdmx_query="https://bdm.insee.fr/series/sdmx/data/BALANCE-PAIEMENTS",
        )
        test2 = isinstance(data, pd.DataFrame)

        self.assertTrue(test1 & test2)

    def test_get_dataset_1(self, patch1, patch2, patch3, patch4):
        data = get_dataset("BALANCE-PAIEMENTS")
        self.assertTrue(isinstance(data, pd.DataFrame))

    def test_get_dataset_2(self, patch1, patch2, patch3, patch4):
        data = get_dataset(
            "CNA-2014-CPEB",
            filter="A.CNA_CPEB.A38-CB.VAL.D39.VALEUR_ABSOLUE.FE.EUROS_COURANTS.BRUT",
            lastNObservations=1,
        )
        self.assertTrue(isinstance(data, pd.DataFrame))

    def test_get_dataset_3(self, patch1, patch2, patch3, patch4):
        data1 = get_dataset("IPC-2015", filter="M......ENSEMBLE...CVS.2015.")
        data2 = get_dataset(
            "IPC-2015",
            filter="M......ENSEMBLE...CVS.2015.",
            includeHistory=True,
            updatedAfter="2017-07-11T08:45:00",
        )
        self.assertTrue(len(data1.index) < len(data2.index))

    def test_get_dataset_4(self, patch1, patch2, patch3, patch4):
        self.assertRaises(ValueError, get_dataset, "a")

    def test_search_macrodata(self, patch1, patch2, patch3, patch4):
        search_all = search_macrodata()
        search_paris = search_macrodata("PARIS")
        search_paper = search_macrodata("pâte à papier")
        test1 = isinstance(search_all, pd.DataFrame)
        test2 = isinstance(search_paris, pd.DataFrame)
        test3 = isinstance(search_paper, pd.DataFrame)
        self.assertTrue(test1 & test2 & test3)

    def test_get_idbank_internal_data(self, patch1, patch2, patch3, patch4):
        df = _get_idbank_internal_data()
        test = isinstance(df, pd.DataFrame)
        self.assertTrue(test)

    def test_get_idbank_internal_data_harmonized(
        self, patch1, patch2, patch3, patch4
    ):
        df = _get_idbank_internal_data_harmonized()
        test = isinstance(df, pd.DataFrame)
        self.assertTrue(test)

    def test_get_dataset_dimension(self, patch1, patch2, patch3, patch4):
        df = _get_dataset_dimension("CLIMAT-AFFAIRES")
        os.environ["insee_date_test"] = str(
            datetime.now() + timedelta(days=91)
        )
        df = _get_dataset_dimension("CLIMAT-AFFAIRES")
        test1 = isinstance(df, pd.DataFrame)

        _clean_insee_folder()
        os.environ["insee_date_test"] = ""
        df = _get_dataset_dimension("CLIMAT-AFFAIRES")
        test2 = isinstance(df, pd.DataFrame)

        self.assertTrue(test1 & test2)

    def test_get_dimension_values(self, patch1, patch2, patch3, patch4):
        df = _get_dimension_values("CL_PERIODICITE")
        os.environ["insee_date_test"] = str(
            datetime.now() + timedelta(days=91)
        )
        df = _get_dimension_values("CL_PERIODICITE")

        test1 = isinstance(df, pd.DataFrame)
        self.assertTrue(test1)

    def test_download_idbank_list_1(self, patch1, patch2, patch3, patch4):
        # try:
        df = _download_idbank_list()
        os.environ["insee_date_test"] = str(
            datetime.now() + timedelta(days=91)
        )
        df = _download_idbank_list()
        # except Exception:
        #     df = pd.DataFrame({"test_backup": ["test_backup"]})

        test1 = isinstance(df, pd.DataFrame)
        self.assertTrue(test1)

    if test_SDMX:

        def test_get_last_release(self, patch1, patch2, patch3, patch4):
            data = get_last_release()
            self.assertTrue(isinstance(data, pd.DataFrame))

        # def test_build_series_list(self, patch1, patch2, patch3, patch4):
        #     df = _build_series_list()
        #     test = isinstance(df, pd.DataFrame)
        #     os.environ['pynsee_use_sdmx'] = "False"
        #     self.assertTrue(test)


if __name__ == "__main__":
    unittest.main()
    # python test_pynsee_macrodata.py TestFunction.test_get_series_2
    # python test_pynsee_macrodata.py TestFunction.test_get_column_title_1
