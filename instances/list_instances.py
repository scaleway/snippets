#!/usr/bin/env python

"""This Python snippet uses the Scaleway API to list instances. If you have more than 50 instances, the response is
paginated. This script consumes pagination.

Run the script with --help to get usage.

The environment variable SCW_TOKEN must be set. To get your API token, visit the credentials page of the web console. It
is absolutely essential that you keep your token private as it gives access to everything in your Scaleway account.

Dependencies:

    - requests ; install with
        `pip install requests`
        or (Ubuntu / Python 2) `apt-get install -y python-requests`
        or (Ubuntu / Python 3) `apt-get install -y python3-requests`
"""

from __future__ import print_function

import argparse
import logging
import os
import sys

import requests


COMPUTE_REGIONS = (
    'ams1',
    'par1',
)


def list_instances(region, auth_token):
    base_url = 'https://cp-%s.scaleway.com' % region
    path = '/servers'

    while True:
        resp = requests.get(
            base_url + path,
            headers={'X-Auth-Token': auth_token},
        )
        resp.raise_for_status()

        for server in resp.json()['servers']:
            print ('%s %-10s %-30s state=%-10s public IP=%-15s private IP=%-15s' % (
                server['id'],
                server['commercial_type'],
                server['name'],
                server['state'],
                (server['public_ip'] or {}).get('address', ''),
                server['private_ip'] or ''
            ))

        if 'next' not in resp.links:
            break

        path = resp.links['next']['url']


def main():
    logging.basicConfig(format='[%(levelname)s] %(message)s')

    auth_token = os.getenv('SCW_TOKEN')
    if not auth_token:
        logging.error('Environment variable SCW_TOKEN required')
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--region', choices=COMPUTE_REGIONS, help='Region to list servers from')
    args = parser.parse_args()

    list_instances(args.region, auth_token)


if __name__ == '__main__':
    main()
