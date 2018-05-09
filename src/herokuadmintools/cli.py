"""
cli wrapper of Mozilla specific heroku administrative tasks

Exit Codes:
    0 - everyone has 2FA enabled
    1 - bad arguments, Heroku not queried
    2 - one or more users without 2FA enabled
    3 - Heroku query failure
"""
import argparse
import logging

from herokuadmintools import (
    find_affected_apps,
    find_users_missing_2fa,
    generate_csv,
    get_status_code,
    ORG_NAME_DEFAULT,
    update_status_code,
    verify_access,
)


# boilerplate
logger = logging.getLogger(__name__)


def output_results(users_missing_2fa, affected_apps, org=ORG_NAME_DEFAULT):
    if not users_missing_2fa:
        print('All {} users have 2FA enabled :)'.format(org))
        return

    print('The following {} users do not have 2FA enabled!'.format(org))
    for role, users in users_missing_2fa.items():
        print('\n~ {} {}s:'.format(len(users), role))
        for email in sorted(users):
            print(email)

    if affected_apps:
        print('\n{} apps are affected:\n'.format(len(affected_apps)))
        for app, emails in sorted(affected_apps.items()):
            print('{} ({})'.format(app, ', '.join(sorted(emails))))


def do_task(args):
    org = args.organization
    verify_access(org)
    users_missing_2fa = find_users_missing_2fa(org)
    affected_apps = find_affected_apps(users_missing_2fa, org)

    if args.csv:
        generate_csv(users_missing_2fa, affected_apps)
    else:
        output_results(users_missing_2fa, affected_apps)

    update_status_code(0 if not users_missing_2fa else 2)


def parse_args(args=None):
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse
                                     .RawTextHelpFormatter)
    parser.add_argument('--debug', help="log at DEBUG level",
                        action='store_true')
    parser.add_argument('--csv', action='store_true',
                        help='output as csv file')
    parser.add_argument('--organization', help='Heroku Organization to query',
                        default=ORG_NAME_DEFAULT)
    args = parser.parse_args(args=args)
    if args.debug:
        logger.setLevel(logging.DEBUG)
    return args


def main(args=None):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    args = parse_args(args)
    do_task(args)
    raise SystemExit(get_status_code())
