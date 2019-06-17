#!/usr/bin/env python

"""This Python snippet uses the Scaleway API to list, add or edit SSH keys from a Scaleway account.

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


def get_user_id_from_token(auth_token):
    """Return the user id of :param auth_token:'s owner."""
    resp = requests.get('https://account.scaleway.com/tokens/%s' % auth_token)
    resp.raise_for_status()
    return resp.json()['token']['user_id']


def ssh_keys(auth_token, user_id, new_pubkey=None, remove_pubkey=None, display_list=False):
    """ List, add or remove public keys.
    """
    resp = requests.get(
        'https://account.scaleway.com/users/%s' % user_id,
        headers={'X-Auth-Token': auth_token}
    )
    resp.raise_for_status()

    ssh_public_keys = resp.json()['user']['ssh_public_keys']

    if display_list:
        for key in ssh_public_keys:
            print(key['fingerprint'])

    if not new_pubkey and not remove_pubkey:
        return

    payload = {
        'ssh_public_keys': []
    }

    for key in resp.json()['user']['ssh_public_keys']:
        if remove_pubkey and remove_pubkey in key['fingerprint']:
            continue

        payload['ssh_public_keys'].append({
            'key': key['key']
        })

    # Append the new key to payload
    if new_pubkey:
        payload['ssh_public_keys'].append({
            'key': new_pubkey
        })

    resp = requests.patch(
        'https://account.scaleway.com/users/%s' % user_id,
        json=payload,
        headers={'X-Auth-Token': auth_token}
    )
    resp.raise_for_status()


def main():
    logging.basicConfig(format='[%(levelname)s] %(message)s')

    auth_token = os.getenv('SCW_TOKEN')
    if not auth_token:
        logging.error('Environment variable SCW_TOKEN required')
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--list', action='store_true', default=False, help='List SSH keys')
    parser.add_argument('-a', '--add', type=argparse.FileType('r'), help='Add new SSH key')
    parser.add_argument('-r', '--remove', help='Remove a keyfile by fingerprint')
    args = parser.parse_args()

    user_id = get_user_id_from_token(auth_token)
    if not user_id:
        sys.exit(1)

    if args.add:
        new_pubkey = args.add.read().strip()
        args.add.close()
        ssh_keys(auth_token, user_id, new_pubkey=new_pubkey)

    if args.remove:
        ssh_keys(auth_token, user_id, remove_pubkey=args.remove)

    if args.list:
        ssh_keys(auth_token, user_id, display_list=True)


if __name__ == '__main__':
    main()
