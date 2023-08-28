# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import time
import unittest
from unittest import TestCase
from unittest import mock
import pandas as pd
from requests.exceptions import RequestException
from functools import partial

from pynsee.localdata._get_geo_relation import _get_geo_relation
from pynsee.localdata._get_insee_one_area import _get_insee_one_area

from pynsee.localdata.get_area_list import get_area_list
from pynsee.localdata.get_geo_list import get_geo_list

from pynsee.localdata.get_local_data import get_local_data
from pynsee.localdata.get_included_area import get_included_area
from pynsee.localdata.get_nivgeo_list import get_nivgeo_list
from pynsee.localdata.get_local_metadata import get_local_metadata
from pynsee.localdata.get_population import get_population
from pynsee.localdata.get_old_city import get_old_city
from pynsee.localdata.get_new_city import get_new_city
from pynsee.localdata.get_ascending_area import get_ascending_area
from pynsee.localdata.get_descending_area import get_descending_area

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
class TestLocaldata(TestCase):
    def test_get_population(self, patch1, patch2, patch3, patch4):
        df = get_population(update=True)
        test = isinstance(df, pd.DataFrame)
        self.assertTrue(test)

    def test_get_insee_one_area_1(self, patch1, patch2, patch3, patch4):
        def get_insee_one_area_test(area_type="derf", codearea="c"):
            _get_insee_one_area(area_type=area_type, codearea=codearea)

        self.assertRaises(ValueError, get_insee_one_area_test)

    def test_get_insee_one_area_2(self, patch1, patch2, patch3, patch4):
        def get_insee_one_area_test(area_type="ZoneDEmploi2020", codearea="c"):
            _get_insee_one_area(area_type=area_type, codearea=codearea)

        self.assertRaises(ValueError, get_insee_one_area_test)

    def test_get_new_city(self, patch1, patch2, patch3, patch4):
        test = True
        df = get_new_city(code="24431", date="2018-01-01")
        test = test & isinstance(df, pd.DataFrame)
        df = get_new_city(code="24431")
        test = test & isinstance(df, pd.DataFrame)
        self.assertTrue(isinstance(df, pd.DataFrame))

    def test_get_old_city(self, patch1, patch2, patch3, patch4):
        test = True
        df = get_old_city(code="24259")
        test = test & isinstance(df, pd.DataFrame)
        self.assertTrue(isinstance(df, pd.DataFrame))

    def test_get_geo_list_1(self, patch1, patch2, patch3, patch4):
        list_available_geo = [
            "communes",
            "regions",
            "departements",
            "communesDeleguees",
            "communesAssociees",
            "arrondissements",
            "arrondissementsMunicipaux",
        ]

        list_geo_data = []
        for geo in list_available_geo:
            time.sleep(10)
            list_geo_data.append(get_geo_list(geo))

        df = pd.concat(list_geo_data)
        self.assertTrue(isinstance(df, pd.DataFrame))

        # repeat test to check locally saved data use
        self.assertTrue(isinstance(get_geo_list("regions"), pd.DataFrame))

    def test_get_geo_list_2(self, patch1, patch2, patch3, patch4):
        self.assertRaises(ValueError, get_geo_list, "a")

    def test_get_geo_relation_1(self, patch1, patch2, patch3, patch4):
        df1 = _get_geo_relation("region", "11", "descendants")
        time.sleep(10)
        df2 = _get_geo_relation("departement", "91", "ascendants")
        test = isinstance(df1, pd.DataFrame) & isinstance(df2, pd.DataFrame)
        self.assertTrue(test)

    def test_get_nivgeo_list(self, patch1, patch2, patch3, patch4):
        data = get_nivgeo_list()
        self.assertTrue(isinstance(data, pd.DataFrame))

    def test_get_local_metadata(self, patch1, patch2, patch3, patch4):
        data = get_local_metadata()
        self.assertTrue(isinstance(data, pd.DataFrame))

    def test_get_local_data_1(self, patch1, patch2, patch3, patch4):
        dep = get_geo_list("departements")

        variables = "AGESCOL-SEXE-ETUD"
        dataset = "GEO2019RP2011"
        # codegeo = ['91', '976']
        codegeos = list(dep.CODE)
        codegeos = dep.CODE.to_list()
        geo = "DEP"
        data = get_local_data(
            variables=variables,
            dataset_version=dataset,
            nivgeo=geo,
            geocodes=codegeos,
        )

        self.assertTrue(isinstance(data, pd.DataFrame))

    def test_get_local_data_all(self, patch1, patch2, patch3, patch4):
        test = True

        data = get_local_data(
            dataset_version="GEO2020RP2017",
            variables="SEXE-DIPL_19",
            nivgeo="DEP",
            geocodes=["91", "92", "976"],
        )
        test = test & isinstance(data, pd.DataFrame)

        data = get_local_data(
            dataset_version="GEO2020FILO2018",
            variables="INDICS_FILO_DISP_DET-TRAGERF",
            nivgeo="REG",
            geocodes=["11", "01"],
        )
        test = test & isinstance(data, pd.DataFrame)

        data = get_local_data(
            dataset_version="BDCOM2017",
            variables="INDICS_BDCOM",
            nivgeo="REG",
            geocodes=["11"],
        )
        test = test & isinstance(data, pd.DataFrame)

        data = get_local_data(
            dataset_version="GEO2019RFD2011",
            variables="INDICS_ETATCIVIL",
            nivgeo="REG",
            geocodes=["11"],
        )
        test = test & isinstance(data, pd.DataFrame)

        data = get_local_data(
            dataset_version="TOUR2019",
            variables="ETOILE",
            nivgeo="REG",
            geocodes=["11"],
        )
        test = test & isinstance(data, pd.DataFrame)

        # repeat same query to test locally saved data use
        data = get_local_data(
            dataset_version="TOUR2019",
            variables="ETOILE",
            nivgeo="REG",
            geocodes=["11"],
        )
        test = test & isinstance(data, pd.DataFrame)

        data = get_local_data(
            dataset_version="GEO2020FLORES2017",
            variables="EFFECSAL5T_1_100P",
            nivgeo="REG",
            geocodes="11",
        )
        test = test & isinstance(data, pd.DataFrame)

        data = get_local_data(
            dataset_version="GEO2019REE2018",
            variables="NA5_B",
            nivgeo="REG",
            geocodes=["11"],
        )
        test = test & isinstance(data, pd.DataFrame)

        data = get_local_data(
            dataset_version="POPLEG2018",
            variables="IND_POPLEGALES",
            nivgeo="COM",
            geocodes=["91477"],
        )
        test = test & isinstance(data, pd.DataFrame)

        data = get_local_data(
            dataset_version="GEOlatestRPlatest", variables="CS1_6"
        )
        test = test & isinstance(data, pd.DataFrame)

        # test data cached
        data = get_local_data(
            dataset_version="GEOlatestRPlatest", variables="TYPMR"
        )
        test = test & isinstance(data, pd.DataFrame)

        data = get_local_data(
            dataset_version="GEOlatestRPlatest",
            variables="TF4",
            nivgeo="COM",
            geocodes=["75056"],
        )
        test = test & isinstance(data, pd.DataFrame)

        data = get_local_data(
            dataset_version="GEOlatestFILOlatest",
            variables="INDICS_FILO_DISP",
            nivgeo="COM",
            update=True,
            geocodes="75056",
        )
        test = test & isinstance(data, pd.DataFrame)

        data = get_local_data(
            dataset_version="POPLEGlatest",
            variables="IND_POPLEGALES",
            nivgeo="COM",
            update=True,
            geocodes="75056",
        )
        test = test & isinstance(data, pd.DataFrame)

        data = get_local_data(
            dataset_version="GEOlatestRFDlatest",
            variables="INDICS_ETATCIVIL",
            nivgeo="COM",
            update=True,
            geocodes="75056",
        )
        test = test & isinstance(data, pd.DataFrame)

        data = get_local_data(
            dataset_version="BDCOMlatest",
            variables="INDICS_BDCOM",
            nivgeo="COM",
            update=True,
            geocodes="75056",
        )
        test = test & isinstance(data, pd.DataFrame)

        data = get_local_data(
            dataset_version="GEOlatestREElatest",
            variables="NA10_HORS_AZ-ENTR_INDIVIDUELLE",
            nivgeo="COM",
            update=True,
            geocodes="75056",
        )
        test = test & isinstance(data, pd.DataFrame)

        for geo in ["DEP", "REG", "FE", "METRODOM"]:
            data = get_local_data(
                dataset_version="GEO2020FLORES2017",
                variables="NA17",
                nivgeo=geo,
            )
            test = test & isinstance(data, pd.DataFrame)

        test = test & isinstance(data, pd.DataFrame)

        #
        # test get_descending_area and get_ascending_are
        #

        df = get_descending_area("commune", code="59350", date="2018-01-01")
        test = test & isinstance(df, pd.DataFrame)

        df = get_descending_area("departement", code="59")
        test = test & isinstance(df, pd.DataFrame)

        df = get_descending_area("zoneDEmploi2020", code="1109")
        test = test & isinstance(df, pd.DataFrame)

        df = get_ascending_area("commune", code="59350", date="2018-01-01")
        test = test & isinstance(df, pd.DataFrame)

        df = get_ascending_area("departement", code="59")
        test = test & isinstance(df, pd.DataFrame)

        self.assertTrue(test)

    def test_get_local_data_latest_error(self, patch1, patch2, patch3, patch4):
        def getlocaldataTestError():
            data = get_local_data(
                dataset_version="GEOlatestTESTlatest", variables="CS1_6"
            )
            return data

        self.assertRaises(ValueError, getlocaldataTestError)

    def test_get_area_list_1(self, patch1, patch2, patch3, patch4):
        test = True

        df = get_area_list(update=True)
        test = test & isinstance(df, pd.DataFrame)

        df = get_area_list(update=False)
        test = test & isinstance(df, pd.DataFrame)

        df = get_area_list(area="communes")
        test = test & isinstance(df, pd.DataFrame)

        df = get_area_list(area="collectivitesDOutreMer", update=True)
        test = test & isinstance(df, pd.DataFrame)

        df = get_area_list(area="UU2020", update=True)
        test = test & isinstance(df, pd.DataFrame)

        df = get_area_list(area="regions", date="2023-01-01", update=True)
        test = test & isinstance(df, pd.DataFrame)

        self.assertTrue(test)

    def test_get_area_list_2(self, patch1, patch2, patch3, patch4):
        def get_area_list_test():
            get_area_list("a")

        self.assertRaises(ValueError, get_area_list_test)

    def test_get_area_list_3(self, patch1, patch2, patch3, patch4):
        def get_area_list_test():
            get_area_list(area="regions", date="1900-01-01", update=True)

        self.assertRaises(RequestException, get_area_list_test)

    def test_get_included_area(self, patch1, patch2, patch3, patch4):
        list_available_area = [
            "zonesDEmploi2020",
            "airesDAttractionDesVilles2020",
            "unitesUrbaines2020",
        ]
        list_data = []

        for a in list_available_area:
            time.sleep(10)
            df_list = get_area_list(a)
            code = df_list.CODE[:3].to_list()
            data = get_included_area(area_type=a, codeareas=code)
            list_data.append(data)

        data_final = pd.concat(list_data)

        test = isinstance(data_final, pd.DataFrame)

        self.assertTrue(test)


if __name__ == "__main__":
    unittest.main()
