# -*- coding: utf-8 -*-
# Copyright : INSEE, 2021

import os
import yaml
from pathlib2 import Path
import pandas as pd
import requests

from pynsee.utils._get_token_from_insee import _get_token_from_insee
from pynsee.utils.clear_all_cache import clear_all_cache
from pynsee.utils._get_credentials import _get_credentials
from pynsee.utils._wait_api_query_limit import _wait_api_query_limit

def init_conn(insee_key, insee_secret, proxy_server=""):
    """Save your credentials to connect to INSEE APIs, subscribe to api.insee.fr

    Args:
        insee_key (str): user's key
        insee_secret (str): user's secret
        proxy_server (str, optional): Proxy server address, e.g. 'http://my_proxy_server:port'. Defaults to "".

    Examples:
        >>> from pynsee.utils.init_conn import init_conn
        >>> init_conn(insee_key="my_insee_key", insee_secret="my_insee_secret")
    """    
    d = {'credentials':{'insee_key': insee_key,
                  'insee_secret': insee_secret,
                  'proxy_server': proxy_server}}

    #os.environ['pynsee_query_print'] = 'True'
    
    home = str(Path.home())
    
    pynsee_credentials_file = home + '/' + 'pynsee_credentials.yml'
    
    with open(pynsee_credentials_file, 'w') as yaml_file:
        yaml.dump(d, yaml_file, default_flow_style=False)
        yaml_file.close()

    clear_all_cache()

    keys = _get_credentials()

    insee_key = keys['insee_key']
    insee_secret = keys['insee_secret']

    token = _get_token_from_insee(insee_key, insee_secret)

    if token is None:
        print('!!! Token is missing, please check insee_key and insee_secret are correct !!!')
    else:
        print(f'Token has been created : {token}')
        
    try:
        proxies = {'http': os.environ['http_proxy'],
                   'https': os.environ['http_proxy']}
    except:
        proxies = {'http': '', 'https': ''}

    queries = ['https://api.insee.fr/series/BDM/V1/dataflow/FR1/all',
                'https://api.insee.fr/metadonnees/V1/codes/cj/n3/5599',
                'https://api.insee.fr/entreprises/sirene/V3/siret?q=activitePrincipaleUniteLegale:86.10*&nombre=1000', 
                'https://api.insee.fr/donnees-locales/V0.1/donnees/geo-SEXE-DIPL_19@GEO2020RP2017/FE-1.all.all']
    apis = ['BDM', 'Metadata', 'Sirene', 'Local Data']

    file_format=['application/xml','application/xml', 'application/json;charset=utf-8', 'application/xml']

    list_requests_status = []

    for q in range(len(queries)):

        headers = {'Accept': file_format[q],
                'Authorization': 'Bearer ' + token}    
        api_url = queries[q]

        _wait_api_query_limit(api_url)
        results = requests.get(api_url, proxies=proxies, headers=headers)

        if results.status_code != 200:
            print('!!! Please subscribe to {} API on api.insee.fr !!!'.format(apis[q]))
        list_requests_status += [results.status_code]

    if all([sts == 200 for sts in list_requests_status]):
        print("Subscription to all INSEE's APIs has been successfull")
            