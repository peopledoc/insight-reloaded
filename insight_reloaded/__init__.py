# -*- coding: utf-8 -*-
"""A full async docsplit previewer server based on Tornado and Redis"""


pkg_resources = __import__('pkg_resources')
distribution = pkg_resources.get_distribution('insight_reloaded')

#: Module version, as defined in PEP-0396.
__version__ = distribution.version
