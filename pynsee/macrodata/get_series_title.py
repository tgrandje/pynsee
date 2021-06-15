# -*- coding: utf-8 -*-

from pynsee.macrodata.get_series import get_series

def get_series_title(series):
    """Get French and English titles of a list of series (idbanks)

    Args:
        series (list): a list of series (idbanks)

    Examples:
        >>> from pynsee import *
        >>> series = get_series_list("CLIMAT-AFFAIRES")
        >>> series = series.loc[:3, "IDBANK"].to_list()
        >>> titles = get_series_title(series)
    """        
    data = get_series(series, firstNObservations=1, metadata=False)
    
    data = data[["IDBANK", "TITLE_FR", "TITLE_EN"]]
    
    return(data)
    