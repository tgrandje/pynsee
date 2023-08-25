from pynsee.sirene import *
from pynsee.macrodata import *
from pynsee.localdata import *
from pynsee.geodata import *
from pynsee.metadata import *
from pynsee.utils import *
from pynsee.download import *

from dotenv import load_dotenv

load_dotenv(override=True)

# configuration
_config = {
    "http_proxy": "",
    "https_proxy": "",
    "hide_progress": False,
    "insee_key": None,
    "insee_secret": None,
}
