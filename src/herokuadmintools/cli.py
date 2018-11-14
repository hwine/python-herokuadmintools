"""
cli wrapper of Mozilla specific heroku administrative tasks

Exit Codes:
    0 - everyone okay
    1 - bad arguments, Heroku not queried
    2 - one or more users with improper account setup
    3 - Heroku query failure
"""

import argparse
from collections import defaultdict
import csv
import logging
import re
import sys

from herokuadmintools import (
    find_affected_apps,
    generate_csv,
    get_status_code,
    get_users,
    ORG_NAME_DEFAULT,
    update_status_code,
    verify_access,
)

_epilog = """
Mozilla defines proper account as the following:
    - account is federated (i.e. using SSO), or
    - account is not federated, and
        - 2FA must be enabled, and
        - if role is 'member' or 'admin',
          email must match regex '^heroku-.*@mozilla.com$'
"""


# boilerplate
logger = logging.getLogger(__name__)


def output_results(users_missing_2fa, affected_apps, org=ORG_NAME_DEFAULT):
    if not users_missing_2fa:
        print("All {} users have 2FA enabled :)".format(org))
        return

    print("The following {} users do not have 2FA enabled!".format(org))
    for role, users in users_missing_2fa.items():
        print("\n~ {} {}s:".format(len(users), role))
        for email in sorted(users):
            print(email)

    if affected_apps:
        print("\n{} apps are affected:\n".format(len(affected_apps)))
        for app, emails in sorted(affected_apps.items()):
            print("{} ({})".format(app, ", ".join(sorted(emails))))


def generate_membership_email_csv(users, cc_addr=None):
    if len(users) == 0:
        # nothing to do
        return
    headers = list(users[0].keys())
    if cc_addr:
        headers.append("CC")
    writer = csv.DictWriter(sys.stdout, headers, extrasaction="ignore")
    writer.writeheader()
    for user in users:
        if len(user) != 8:
            raise ValueError
        user.update(CC=cc_addr)
        writer.writerow(user)


def generate_2fa_email_csv(users_missing_2fa, affected_apps, cc_addr=None):
    # flip app: users to user: apps
    user_apps = defaultdict(list)
    for app, users in affected_apps.items():
        for user in users:
            user_apps[user].append(app)
    if cc_addr:
        print('"CC",', end="")
    print('"{}","{}"'.format("Email Address", "Apps"))
    for user, apps in user_apps.items():
        if cc_addr:
            print('"{}",'.format(cc_addr), end="")
        print('"{}","{}"'.format(user, ",".join(apps)))


def find_unsafe_users(org=ORG_NAME_DEFAULT):
    unsafe_users = defaultdict(set)
    # Follow the rules described in _epilog
    pat = re.compile(r'''^heroku-.*@mozilla.com$''', re.RegexFlag.IGNORECASE)
    ok = False
    for user in get_users():
        if user['federated']:
            ok = True
        elif user['two_factor_authentication']:
            if user['role'] in ['member', 'admin']:
                ok = bool(pat.match(user['email']))
            else:
                ok = True

        if not ok:
            unsafe_users[user['role']].add(user['email'])
    return unsafe_users


def do_task(args):
    org = args.organization
    verify_access(org)
    if args.membership:
        users_of_interest = list(get_users(org))
        affected_apps = {}
        generate_membership_email_csv(users_of_interest, args.cc)
    else:
        users_of_interest = find_unsafe_users(org)
        affected_apps = find_affected_apps(users_of_interest, org)
        update_status_code(0 if not users_of_interest else 2)

        if args.csv:
            generate_csv(users_of_interest, affected_apps)
        elif args.email:
            generate_2fa_email_csv(users_of_interest, affected_apps, args.cc)
        else:
            output_results(users_of_interest, affected_apps)


def parse_args(args=None):
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawTextHelpFormatter,
        epilog=_epilog
    )
    parser.add_argument("--debug", help="log at DEBUG level", action="store_true")
    parser.add_argument("--csv", action="store_true", help="output as csv file")
    parser.add_argument(
        "--email", action="store_true", help="output as csv file, email order"
    )
    parser.add_argument(
        "--cc", help="Specify CC column for --email output", default=None
    )
    parser.add_argument(
        "--organization", help="Heroku Organization to query", default=ORG_NAME_DEFAULT
    )
    parser.add_argument(
        "--membership", action="store_true", help="Only output members list"
    )
    args = parser.parse_args(args=args)
    # handle args which imply others
    if args.cc or args.membership:
        args.email = True
    if args.email and args.csv:
        parser.error("Only one of --email and --csv can be specified")
    if args.debug:
        logger.setLevel(logging.DEBUG)
    return args


def main(args=None):
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
    args = parse_args(args)
    do_task(args)
    raise SystemExit(get_status_code())
