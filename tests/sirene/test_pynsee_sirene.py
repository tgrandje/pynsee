# Copyright : INSEE, 2021

from unittest import mock
from unittest import TestCase
from pandas import pandas as pd
from functools import partial

from shapely.geometry import (
    Point,
    Polygon,
    MultiPolygon,
    LineString,
    MultiLineString,
    MultiPoint,
)

from pynsee.sirene.get_sirene_data import get_sirene_data
from pynsee.sirene.search_sirene import search_sirene
from pynsee.sirene._request_sirene import _request_sirene
from pynsee.sirene.get_dimension_list import get_dimension_list
from pynsee.sirene.SireneDataFrame import SireneDataFrame
from pynsee.geodata.GeoFrDataFrame import GeoFrDataFrame
from pynsee.sirene.get_sirene_relatives import get_sirene_relatives


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
    "pynsee.utils._request_insee._request_insee",
    side_effect=mock_request_insee,
)
class TestSirene(TestCase):
    def test_get_sirene_relatives(self, *args):
        test = True
        df = get_sirene_relatives("00555008200027")
        test = test & isinstance(df, SireneDataFrame)

        df = get_sirene_relatives(["39860733300059", "00555008200027"])
        test = test & isinstance(df, SireneDataFrame)

        df = get_sirene_relatives(["39860733300059", "1"])
        test = test & isinstance(df, SireneDataFrame)

        self.assertTrue(test)

    def test_error_get_relatives1(self, *args):
        with self.assertRaises(ValueError):
            get_sirene_relatives(1)

    def test_error_get_relatives2(self, *args):
        with self.assertRaises(ValueError):
            get_sirene_relatives("0")

    def test_error_get_relatives3(self, *args):
        with self.assertRaises(ValueError):
            get_sirene_relatives("0")

    def test_get_sirene_relatives4(self, *args):
        df = get_sirene_relatives(["39860733300059", "00555008200027"])
        test = isinstance(df, pd.DataFrame)
        self.assertTrue(test)

    def test_get_dimension_list(self, *args):
        test = True

        df = get_dimension_list()
        test = test & isinstance(df, pd.DataFrame)

        df = get_dimension_list("siren")
        test = test & isinstance(df, pd.DataFrame)

        self.assertTrue(test)

    def test_error_get_dimension_list(self, *args):
        with self.assertRaises(ValueError):
            get_dimension_list("sirène")

    def test_get_location(self, *args):
        df = search_sirene(
            variable=["activitePrincipaleEtablissement"],
            pattern=["29.10Z"],
            kind="siret",
        )

        test = True
        test = test & isinstance(df, SireneDataFrame)

        df = search_sirene(
            variable="activitePrincipaleEtablissement",
            pattern="29.10Z",
            kind="siret",
        )
        df = df.loc[df["effectifsMinEtablissement"] > 100]
        df = df.reset_index(drop=True)

        sirdf = df.get_location()
        test = test & isinstance(sirdf, GeoFrDataFrame)

        geo = sirdf.get_geom()
        test = test & (
            type(geo)
            in [
                Point,
                Polygon,
                MultiPolygon,
                LineString,
                MultiLineString,
                MultiPoint,
            ]
        )

        self.assertTrue(test)

    def test_get_sirene_data(self, *args):
        df1 = get_sirene_data(["32227167700021", "26930124800077"])
        df2 = get_sirene_data("552081317")
        test = isinstance(df1, pd.DataFrame) & isinstance(df2, pd.DataFrame)
        self.assertTrue(test)

    def test_error_get_sirene_data(self, *args):
        with self.assertRaises(ValueError):
            get_sirene_data("1")

    def test_search_sirene_error(self, *args):
        def search_sirene_error():
            df = search_sirene(
                kind="test",
                variable=["activitePrincipaleUniteLegale"],
                pattern=["86.10Z", "75*"],
            )
            return df

        self.assertRaises(ValueError, search_sirene_error)

    def test_search_sirene(self, *args):
        test = True

        df = search_sirene(
            variable=[
                "activitePrincipaleUniteLegale",
                "codePostalEtablissement",
            ],
            pattern=["86.10Z", "75*|91*"],
            kind="siret",
        )
        test = test & isinstance(df, pd.DataFrame)

        # Test only alive businesses are provided
        test = test & all(df["etatAdministratifEtablissement"] == "A")

        test = test & isinstance(df, pd.DataFrame)

        df = search_sirene(
            variable=[
                "libelleCommuneEtablissement",
                "denominationUniteLegale",
            ],
            pattern=["igny", "pizza"],
            phonetic_search=True,
            kind="siret",
        )
        test = test & isinstance(df, pd.DataFrame)

        # mix of variable with and without history on siren
        df = search_sirene(
            variable=[
                "denominationUniteLegale",
                "categorieJuridiqueUniteLegale",
                "categorieEntreprise",
            ],
            closed=True,
            pattern=["sncf", "9220", "PME"],
            kind="siren",
        )
        test = test & isinstance(df, pd.DataFrame)

        # Test not only alive businesses are provided
        test = test & (all(df["etatAdministratifUniteLegale"] == "A") is False)

        # input as string and not list
        df = search_sirene(
            variable="libelleCommuneEtablissement",
            pattern="montrouge",
            kind="siret",
        )
        test = test & isinstance(df, pd.DataFrame)

        df = search_sirene(
            variable=["denominationUniteLegale", "categorieEntreprise"],
            pattern=["Pernod Ricard", "GE"],
            phonetic_search=[True, False],
            kind="siren",
        )
        test = test & isinstance(df, pd.DataFrame)

        df = search_sirene(
            variable=[
                "denominationUniteLegale",
                "categorieEntreprise",
                "categorieJuridiqueUniteLegale",
            ],
            pattern=["Pernod Ricard", "GE", "5710"],
            kind="siren",
        )
        test = test & isinstance(df, pd.DataFrame)

        df = search_sirene(
            variable=["denominationUniteLegale"],
            pattern=["Pernod Ricard"],
            kind="siret",
        )
        test = test & isinstance(df, pd.DataFrame)

        df = search_sirene(
            variable=["denominationUniteLegale"],
            pattern=["tabac"],
            number=2500,
            kind="siret",
        )
        test = test & isinstance(df, pd.DataFrame)

        df = search_sirene(
            variable=[
                "activitePrincipaleEtablissement",
                "codePostalEtablissement",
            ],
            pattern=["56.30Z", "83*"],
            number=5000,
        )
        test = test & isinstance(df, pd.DataFrame)

        self.assertTrue(test)

    def test_request_sirene(self, *args):
        list_query_siren = [
            "?q=periode(denominationUniteLegale.phonetisation:sncf)&nombre=20",
            "?q=sigleUniteLegale:???",
            "?q=periode(activitePrincipaleUniteLegale:86.10Z)&nombre=1000000",
        ]

        test = True
        for q in list_query_siren:
            df = _request_sirene(q, kind="siren")
            test = test & isinstance(df, pd.DataFrame)

        list_query_siret = [
            "?q=denominationUniteLegale.phonetisation:oto&champs=denominationUniteLegale",
            "?q=prenom1UniteLegale:hadrien AND nomUniteLegale:leclerc",
            "?q=prenom1UniteLegale.phonetisation:hadrien AND nomUniteLegale.phonetisation:leclerc",
            "?q=activitePrincipaleUniteLegale:8*",
            "?q=activitePrincipaleUniteLegale:86.10Z AND codePostalEtablissement:75*",
        ]

        for q in range(len(list_query_siret)):
            query = list_query_siret[q]
            df = _request_sirene(query, kind="siret")
            test = test & isinstance(df, pd.DataFrame)

        q = "?q=denominationUniteLegale.phonetisation:Pernod OR denominationUniteLegale.phonetisation:Ricard"
        df = _request_sirene(q, kind="siret")
        test = test & isinstance(df, pd.DataFrame)

        q = "?q=periode(denominationUniteLegale.phonetisation:Dassault) OR periode(denominationUniteLegale.phonetisation:Système) AND categorieEntreprise:GE"
        df = _request_sirene(q, kind="siren")
        test = test & isinstance(df, pd.DataFrame)

        self.assertTrue(test)
