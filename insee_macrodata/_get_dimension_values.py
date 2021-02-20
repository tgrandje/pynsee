# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 18:42:01 2020

@author: eurhope
"""
# from functools import lru_cache

# @lru_cache(maxsize=None)
def _get_dimension_values(cl_dimension):    
    
    import requests
    import tempfile
    import xml.etree.ElementTree as ET
    import pandas as pd
    import os
    from datetime import datetime 
    
    from ._create_insee_folder import _create_insee_folder
    from ._hash import _hash
    
    INSEE_sdmx_link_codelist = "https://www.bdm.insee.fr/series/sdmx/codelist/FR1"
        
    INSEE_sdmx_link_codelist_dimension = INSEE_sdmx_link_codelist + '/' + cl_dimension
        
    insee_folder = _create_insee_folder()
    file = insee_folder + "/" + _hash(INSEE_sdmx_link_codelist_dimension)
        
    trigger_update = False
        
    # if the data is not saved locally, or if it is too old (>90 days)
    # then an update is triggered
    
    if not os.path.exists(file): 
        trigger_update = True
    else:       
        # from datetime import timedelta 
        # insee_date_time_now = datetime.now() + timedelta(days=91)
        insee_date_time_now = datetime.now()
         
        # file date creation
        file_date_last_modif =  datetime.fromtimestamp(os.path.getmtime(file))
        day_lapse = (insee_date_time_now - file_date_last_modif).days
        
        if day_lapse > 90:
            trigger_update = True           
    
    if trigger_update:    
    
        proxies = {'http': os.environ.get('http'),
                   'https': os.environ.get('https')}
        
        results = requests.get(INSEE_sdmx_link_codelist_dimension, proxies = proxies)
        
        # create temporary directory
        dirpath = tempfile.mkdtemp()
        
        dimension_file = dirpath + '\\dimension_file'
        
        with open(dimension_file, 'wb') as f:
            f.write(results.content)
        
        root = ET.parse(dimension_file).getroot()
               
        list_values = []
        
        id = next(iter(root[1][0][0].attrib.values()))
        name_fr = root[1][0][0][0].text
        name_en = root[1][0][0][1].text
            
        dataset = {'id': [id],
                   'name_fr': [name_fr],
                   'name_en': [name_en]}
        
        dt = pd.DataFrame(dataset, columns = ['id', 'name_fr', 'name_en'])
            
        list_values.append(dt)
        
        data = root[1][0][0]
        
        n_values = len(data)
        
        def extract_name_fr(data, i):
          try:
              name_fr = data[i][0].text            
          except:
              name_fr = None
          finally:
              return(name_fr)
          
        def extract_name_en(data, i):
          try:
              name_en = data[i][1].text            
          except:
              name_en = None
          finally:
              return(name_en)
          
        def extract_id(data, i):
          try:
              id = data[i].attrib.values()          
          except:
              id = None
          finally:
              return(id)
        
        for i in range(2, n_values):
            
            id = next(iter(extract_id(data, i)))
            name_fr = extract_name_fr(data, i)
            name_en = extract_name_en(data, i)
            
            dataset = {'id': [id],
                       'name_fr': [name_fr],
                       'name_en': [name_en]}
        
            dt = pd.DataFrame(dataset, columns = ['id', 'name_fr', 'name_en'])
            
            list_values.append(dt)
        
        df_dimension_values = pd.concat(list_values) 
        
        #save data
        df_dimension_values.to_pickle(file)
    else:
        df_dimension_values = pd.read_pickle(file)
    
    return df_dimension_values