# -*- coding: utf-8 -*-
from redis import StrictRedis
import json
import requests
import os
from tempfile import NamedTemporaryFile
from urlparse import urljoin
import mimetypes

from insight_reloaded.preview import (DocumentPreview, create_destination_folder, 
                                      PreviewException)

from insight_reloaded.insight_settings import *

redis = StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

class InsightWorkerException(Exception):
    pass

def abort(exception, requested_ressource, callback_url=None):
    """Raise an error but send it first to the callback"""
    if callback_url:
        try:
            r = requests.post(callback_url, 
                              data={'success': False, 
                                    'error_message': exception.message,
                                    'requested_ressource': requested_ressource})
        except requests.exceptions.ConnectionError:
            pass
    raise requests.exceptions.ConnectionError('%s : %s' % (requested_ressource, 
                                                           exception.message))

def main():
    print "Launch insight worker"
    while 1:
        msg = redis.blpop(REDIS_QUEUE_KEY) # BLPOP is blocking for the next entry
        params = json.loads(msg[1])
        print u"Consuming task for doc %s" % params['url']

        # Getting callback url
        if 'callback' in params:
            callback = params['callback']
        else:
            callback = None

        # Downloading file
        try:
            r = requests.get(params['url'])
        except requests.exceptions.ConnectionError, e:
            abort(e, params['url'], callback)

        extensions = []
        if 'content-type' in r.headers:
            extensions += mimetypes.guess_all_extensions(r.headers['content-type'])

        if 'content-disposition' in r.headers:
            filename = r.headers['content-disposition'].split('filename=')[-1].strip('"').strip("'")
            extensions.append(os.path.splitext(filename)[1:])
                
        # Verify if the file is accepted
        accepted_extensions = list(set([ext for ext in extensions if ext in ALLOWED_EXTENSIONS]))
        if len(accepted_extensions) > 0:
            extension = accepted_extensions[0]
        else:
            abort(InsightWorkerException('%s not allowed' % r.headers['content-type']), 
                  params['url'], callback)

        # Creating temporary file
        file_obj = NamedTemporaryFile(suffix=extension, dir=TEMP_DIRECTORY)
        file_obj.write(r.content)
        file_obj.seek(0)
        
        # Settings parameters
        max_previews = params['max_previews']
        if 'crop' in params and params['crop']:
            crop = True
        else:
            crop = False

        # Here comes the document preview engine
        destination_folder = create_destination_folder(DESTINATION_ROOT)
        preview = DocumentPreview(file_obj, callback, PREVIEW_SIZES,
                                  max_previews, TEMP_DIRECTORY, destination_folder, crop)
        try:
            preview.create_previews()
        except PreviewException, e:
            abort(e, params['url'], callback)
        finally:
            preview.cleanup()

        file_obj.close()
        
        url = destination_folder.replace(DESTINATION_ROOT, PREFIX_URL)
        docviewer_url = os.path.join(url, DOCVIEWER_SUFFIX)
        print u"Document previewed in %s" % docviewer_url.replace('{size}', 'normal').replace('{page}', '1')

        if callback:
            req = requests.post(params['callback'], 
                                data={'success': True, 'num_pages': preview.pages,
                                      'docviewer_url': docviewer_url})

if __name__ == "__main__":
    main()
