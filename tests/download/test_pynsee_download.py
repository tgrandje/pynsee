import unittest
from unittest import mock
from unittest import TestCase
import os
import pandas as pd
from functools import partial


from pynsee.download._check_url import _check_url
from pynsee.download import download_file
from pynsee.download import get_file_list
from pynsee.download import get_column_metadata
from pynsee.utils.clear_all_cache import clear_all_cache

from tests.mockups import (
    # module_patch,
    mock_requests_session,
    mock_pool,
    # mock_request_insee,
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
class TestsDownload(TestCase):
    def test_check_url(self, *args):
        url = "https://www.insee.fr/fr/statistiques/fichier/2540004/nat2020_csv.zip"
        url2 = _check_url(url)
        self.assertTrue(isinstance(url2, str))

    def test_get_file_list_error(self, *args):
        os.environ["pynsee_file_list"] = (
            "https://raw.githubusercontent.com/"
            + "InseeFrLab/DoReMIFaSol/master/data-raw/test.json"
        )

        clear_all_cache()
        df = get_file_list()
        clear_all_cache()

        self.assertTrue(isinstance(df, pd.DataFrame))

    def test_download_big_file(self, *args):
        df = download_file(
            "RP_LOGEMENT_2017",
            variables=["COMMUNE", "IRIS", "ACHL", "IPONDL"],
        )
        self.assertTrue(isinstance(df, pd.DataFrame))

    def test_download_file_all(self, *args):
        meta = get_file_list()
        self.assertTrue(isinstance(meta, pd.DataFrame))

        meta["size"] = pd.to_numeric(meta["size"])
        meta = meta[meta["size"] < 300000000].reset_index(drop=True)

        list_file = list(meta.id)
        list_file_check = list_file[:20] + list_file[-20:]
        list_file_check = [
            "COG_COMMUNE_2018",
            "AIRE_URBAINE",
            "FILOSOFI_COM_2015",
            "DECES_2020",
            "PRENOM_NAT",
            "ESTEL_T201_ENS_T",
            "FILOSOFI_DISP_IRIS_2017",
            "BPE_ENS",
            "RP_MOBSCO_2016",
        ]

        for i, f in enumerate(list_file_check):
            print(f"{i} : {f}")

            df = download_file(f)
            label = get_column_metadata(id=f)

            if label is None:
                checkLabel = True
            elif isinstance(label, pd.DataFrame):
                checkLabel = True
            else:
                checkLabel = False

            self.assertTrue(checkLabel)
            self.assertTrue(isinstance(df, pd.DataFrame))
            self.assertTrue((len(df.columns) > 2))

            df = download_file(list_file_check[0])
            self.assertTrue(isinstance(df, pd.DataFrame))


if __name__ == "__main__":
    unittest.main()

"""
import unittest

class KnownGood(unittest.TestCase):
    def __init__(self, input):
        super(KnownGood, self).__init__()
        self.input = input
    def runTest(self, *args):
        self.assertEqual(type(download_file(self.input)), pd.DataFrame)

def suite():
    suite = unittest.TestSuite()
    list_file = ["COG_COMMUNE_2018", "AIRE_URBAINE", "FILOSOFI_COM_2015", "DECES_2020",
                   "PRENOM_NAT", "ESTEL_T201_ENS_T", "FILOSOFI_DISP_IRIS_2017",
                   "BPE_ENS", "RP_MOBSCO_2016"]
    suite.addTests(KnownGood(input) for input in list_file)
    return suite

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite())
"""
