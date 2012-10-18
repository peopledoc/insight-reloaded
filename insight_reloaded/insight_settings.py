# -*- coding: utf-8 -*-
import os.path
try:
    import settings
except ImportError:
    settings = None

REDIS_HOST = getattr(settings, 'REDIS_HOST', 'localhost')
REDIS_PORT = getattr(settings, 'REDIS_PORT', 6379)
REDIS_DB = getattr(settings, 'REDIS_DB', 0)
REDIS_QUEUE_KEY = getattr(settings, 'REDIS_QUEUE_KEY', 'insight_reloaded')

ALLOWED_EXTENSIONS = getattr(settings, 'ALLOWED_EXTENSIONS', 
                             ['.pdf', '.jpeg', '.jpg', '.doc', '.docx', '.xls',
                              '.xlsx', '.odt', '.ods', '.ppt', '.pptx', '.odp',
                              '.png', '.gif'])

PREVIEW_SIZES = getattr(settings, 'PREVIEW_SIZES', {'150': 'small', '750': 'normal', '1000': 'large'})
CROP_SIZE = 12 # %

PREFIX_URL = getattr(settings, 'PREFIX_URL', 'http://localhost/viewer_cache')
DOCVIEWER_SUFFIX = getattr(settings, 'DOCVIEWER_SUFFIX', 'document_{size}_p{page}.png')
TEMP_DIRECTORY = getattr(settings, 'TEMP_DIRECTORY', '/tmp')
DESTINATION_ROOT = getattr(settings, 'DESTINATION_ROOT', os.path.join(TEMP_DIRECTORY, 'previews'))
