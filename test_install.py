# -*- coding: utf-8 -*-
import requests
import sys

from insight_reloaded.insight_settings import CROP_SIZE


def main():
    args = {}
    args['crop'] = CROP_SIZE
    args['url'] = 'http://www.novapost.fr/emploi/ruby.pdf'

    if len(sys.argv) > 1:
        args['url'] = sys.argv[1]
    if len(sys.argv) > 2:
        args['callback'] = sys.argv[2]
    if len(sys.argv) > 3:
        args['crop'] = sys.argv[3]

    print "Running test on: %s" % args
    try:
        raw_input('Continue?')
    except KeyboardInterrupt:
        print
        print "USAGE: %s [url] [callback] [crop]" % sys.argv[0]
        sys.exit(0)

    # On lance un job
    response = requests.get('http://localhost:8888/', params=args)
    # On vérifie que les logs on compris.
    if 'Job added to queue' not in response.text:
        print "Error: %s - %s" % (response.status_code,
                                  response.text)
        sys.exit(1)

    response = requests.get('http://localhost:8888/status')
    if 'There is' not in response.text:
        print "Error: %s - %s" % (response.status_code,
                                  response.text)
        sys.exit(2)

    # On vérifie que le fichier existe au bon endroit
    print "The API works. Check the log file or the callback response"


if __name__ == '__main__':
    main()
