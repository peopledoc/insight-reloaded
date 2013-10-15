# -*- coding: utf-8 -*-
from __future__ import print_function
try:
    from insight.insight_settings import DEFAULT_REDIS_QUEUE_KEY
except ImportError:
    DEFAULT_REDIS_QUEUE_KEY = 'insight-reloaded'

import requests
import time
import sys

API_URL = 'http://localhost:8888/'
QUEUE = 'insight-reloaded'


def main():
    # Init the system
    resp = requests.get('%s%s/status' % (API_URL, QUEUE))
    stats = resp.json()
    STARTING = {'number_in_queue': stats["number_in_queue"],
                'time': time.time()}

    while True:
        resp = requests.get('%s%s/status' % (API_URL, QUEUE))
        stats = resp.json()["number_in_queue"]
        deltaQ = stats - STARTING['number_in_queue']
        deltaT = time.time() - STARTING['time']
        avg = deltaQ * -3600 / deltaT

        print(
            '\r%s — current: %d — avg: %.2f per hour' % (QUEUE, stats, avg),
            end=''
        )
        sys.stdout.flush()

        time.sleep(2)

if __name__ == '__main__':
    main()
