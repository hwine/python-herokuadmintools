__version__ = '0.1.1'

# code to move to modules
from collections import defaultdict
import logging
from functools import lru_cache

import requests
from requests.utils import get_netrc_auth


# boilerplate
logger = logging.getLogger(__name__)
status_code = 0


def get_status_code():
    return status_code


def update_status_code(new_code):
    """ Update global status_code, following rules.

        Current rule is only update if the new value signifies a
        "more severe" error (higher integer value)
    """
    global status_code
    status_code = max(status_code, new_code)


def verify_access():
    if not get_netrc_auth(ORG_USERS_URL):
        logger.fatal('Heroku API credentials not found in `~/.netrc`'
                     'or `~/_netrc`.\n'
                     'Log in using the Heroku CLI to generate them.')
        update_status_code(1)
        return


def find_users_missing_2fa():
    users_missing_2fa = {}
    try:
        org_users = fetch_api_json(ORG_USERS_URL)
        users_missing_2fa = defaultdict(set)
        for user in org_users:
            if not user['two_factor_authentication']:
                users_missing_2fa[user['role']].add(user['email'])
    except Exception:
        logger.critical("Failure communicating with Heroku", exc_info=True)
        update_status_code(3)
    return users_missing_2fa


def find_affected_apps(users_missing_2fa):
    affected_apps = defaultdict(set)
    for role, users in users_missing_2fa.items():
        for email in sorted(users):
            for app in apps_accessible_by_user(email, role):
                affected_apps[app].add(email)
    return affected_apps


def generate_csv(users_missing_2fa, affected_apps):
    if affected_apps:
        print('"{}","{}"'.format("Application", "User without 2FA"))
        for app, emails in sorted(affected_apps.items()):
            for email in emails:
                print('"{}","{}"'.format(app, email))
    return


@lru_cache(maxsize=32)
def fetch_api_json(url):
    # The requests library will automatically use credentials found in netrc.
    response = session.get(url, headers=REQUEST_HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def apps_accessible_by_user(email, role):
    if role == 'admin':
        return ['ALL']
    users_apps_url = '{}/{}/apps'.format(ORG_USERS_URL, email)
    return [app['name'] for app in fetch_api_json(users_apps_url)]


# Mozilla defaults
ORG_NAME = 'mozillacorporation'
# https://devcenter.heroku.com/articles/platform-api-reference#organization-member
ORG_USERS_URL = \
    'https://api.heroku.com/organizations/{}/members'.format(ORG_NAME)
# https://devcenter.heroku.com/articles/platform-api-reference#clients
REQUEST_HEADERS = {
    'Accept': 'application/vnd.heroku+json; version=3',
    'User-Agent': 'build-stats',
}

session = requests.session()

# end of code to move
