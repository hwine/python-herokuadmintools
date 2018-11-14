__version__ = '0.1.2'

from collections import defaultdict
import logging
from functools import lru_cache

import requests
from requests.utils import get_netrc_auth


# boilerplate
logger = logging.getLogger(__name__)
status_code = 0

# Mozilla defaults
ORG_NAME_DEFAULT = 'mozillacorporation'
# https://devcenter.heroku.com/articles/platform-api-reference#organization
ORG_URL_TEMPLATE = 'https://api.heroku.com/organizations/{}'
# https://devcenter.heroku.com/articles/platform-api-reference#organization-member
ORG_USERS_URL_TEMPLATE = \
    'https://api.heroku.com/organizations/{}/members'
# https://devcenter.heroku.com/articles/platform-api-reference#clients
REQUEST_HEADERS = {
    'Accept': 'application/vnd.heroku+json; version=3',
    'User-Agent': 'build-stats',
}


def get_status_code():
    return status_code


def update_status_code(new_code):
    """ Update global status_code, following rules.

        Current rule is only update if the new value signifies a
        "more severe" error (higher integer value)
    """
    global status_code
    status_code = max(status_code, new_code)


def get_org_url(org=ORG_NAME_DEFAULT):
    return ORG_URL_TEMPLATE.format(org)


def get_org_member_url(org=ORG_NAME_DEFAULT):
    return ORG_USERS_URL_TEMPLATE.format(org)


def verify_access(org=ORG_NAME_DEFAULT):
    if not get_netrc_auth(get_org_member_url(org)):
        logger.fatal('Heroku API credentials not found in `~/.netrc`'
                     ' or `~/_netrc`.'
                     ' Log in using the Heroku CLI to generate them,'
                     ' or decrypt your ~/.netrc.gpg file')
        update_status_code(1)
        raise SystemExit(get_status_code())
    try:
        org_perms = fetch_api_json(get_org_url(org))
        role = org_perms.get("role", "public")
        if role not in ["admin"]:
            logger.warn("You only have {} perms for {}".format(role, org))
    except requests.exceptions.HTTPError:
        logger.fatal("You don't have access to {}".format(org))
        update_status_code(3)
        raise SystemExit(get_status_code())
    return


def get_users(org=ORG_NAME_DEFAULT):
    try:
        org_users = fetch_api_json(get_org_member_url(org))
        for user in org_users:
            yield user
    except Exception:
        logger.critical("Failure communicating with Heroku", exc_info=True)
        update_status_code(3)


def find_users_missing_2fa(org=ORG_NAME_DEFAULT):
    users_missing_2fa = defaultdict(set)
    for user in get_users():
        if not user['two_factor_authentication']:
            users_missing_2fa[user['role']].add(user['email'])
    return users_missing_2fa


def find_affected_apps(users_missing_2fa, org=ORG_NAME_DEFAULT):
    affected_apps = defaultdict(set)
    for role, users in users_missing_2fa.items():
        for email in sorted(users):
            for app in apps_accessible_by_user(email, role, org):
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


def apps_accessible_by_user(email, role, org=ORG_NAME_DEFAULT):
    if role == 'admin':
        return ['ALL']
    users_apps_url = '{}/{}/apps'.format(get_org_member_url(org), email)
    return [app['name'] for app in fetch_api_json(users_apps_url)]


session = requests.session()
