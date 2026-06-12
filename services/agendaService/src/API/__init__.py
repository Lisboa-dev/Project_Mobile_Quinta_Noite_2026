import sys

from . import controllers as _controllers

sys.modules[f"{__name__}.Controllers"] = _controllers
