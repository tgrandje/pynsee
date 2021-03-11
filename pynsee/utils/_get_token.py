from functools import lru_cache

@lru_cache(maxsize=None)
def _get_token():
    import os
    from api_insee import ApiInsee
    
    from ._get_envir_token import _get_envir_token

    token_envir = _get_envir_token()

    if token_envir is None:
        try:       
            api = ApiInsee(
                key = os.environ.get('insee_key'),
                secret = os.environ.get('insee_secret')
            )
            token = api.auth.token.access_token
        except:
            token = None
    else:
        token = token_envir

    return(token)

