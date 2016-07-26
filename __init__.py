"""This is a shim that allows the repo top level to act as a package,
and delegates to the actual package subdirectory.""" 

from __future__ import absolute_import

import os

__path__ = [os.path.dirname(__file__) + "/cpylmnl"]
