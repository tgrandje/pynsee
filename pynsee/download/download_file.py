import os

from pynsee.download._download_store_file2 import _download_store_file2
from pynsee.download._load_data_from_schema import _load_data_from_schema

def download_file(id):
    """
    User level function to download files from insee.fr

    Args:
        id (str): file id, check get_file_list to have a full list of available files
        update (bool, optional): Trigger an update, otherwise locally saved data is used. Defaults to False.

    Returns:
        Returns the request dataframe as a pandas object

    """
    
    try:
        df = _load_data_from_schema(
                _download_store_file2(id)
            )
        
        return df
    except:
        raise ValueError("Download failed")
        
    """
    try:
        if (not os.path.exists(filename)) | (update is True):
            
            df = _load_data_from_schema(
                _download_store_file2(id, filename)
            )
            
            df.to_pickle(filename)
            print('\nData saved : {}'.format(filename))
        else:
            try:
                print("Loading of locally-stored data ...")
                df = pd.read_pickle(filename)
            except:
                os.remove(filename)
                df = download_file(id)
            else:
                _warning_cached_data(filename)
    
        return df
    except:
        raise ValueError("Download failed")
        
    """