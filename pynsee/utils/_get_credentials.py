# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

from pathlib import Path
import os
import pandas as pd
from functools import lru_cache
import numpy as np

import logging
logger = logging.getLogger(__name__)

def _get_credentials():

    envir_var_used = False
    try:
        home = str(Path.home())
        pynsee_credentials_file = home + "/" + "pynsee_credentials.csv"
        cred = pd.read_csv(pynsee_credentials_file)
        os.environ["insee_key"] = str(cred.loc[0, "insee_key"])
        os.environ["insee_secret"] = str(cred.loc[0, "insee_secret"])
        http_proxy = cred.loc[0, "http_proxy"]
        https_proxy = cred.loc[0, "https_proxy"]
        if (http_proxy is None) or (not isinstance(http_proxy, str)):
            http_proxy = ""
        if (https_proxy is None) or (not isinstance(https_proxy, str)):
            https_proxy = ""
        os.environ["http_proxy"] = str(http_proxy)
        os.environ["https_proxy"] = str(https_proxy)
    except:
        envir_var_used = True

    try:
        key_dict = {
            "insee_key": os.environ["insee_key"],
            "insee_secret": os.environ["insee_secret"],
        }
    except:
        try:
            key_dict = {
                "insee_key": os.environ["INSEE_KEY"],
                "insee_secret": os.environ["INSEE_SECRET"],
            }
        except:
            key_dict = None

    if (envir_var_used is True) & (key_dict is not None):
        _warning_credentials("envir_var_used")
    elif key_dict is None:
        _warning_credentials("key_dict_none")

    return key_dict


@lru_cache(maxsize=None)
def _warning_credentials(string):
    if string == "envir_var_used":
        logger.debug(
            "Existing environment variables used, instead of locally "
            "saved credentials"
        )
    if string == "key_dict_none":
        logger.critical(
            "INSEE API credentials have not been found: please try to reuse "
            "pynsee.utils.init_conn to save them locally.\n"
            "Otherwise, you can still use environment variables as follow:\n"
            "import os\n"
            "os.environ['insee_key'] = 'my_insee_key'\n"
            "os.environ['insee_secret'] = 'my_insee_secret'"
            )
