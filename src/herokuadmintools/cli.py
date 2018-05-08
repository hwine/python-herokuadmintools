"""
cli wrapper of Mozilla specific heroku administrative tasks
"""
import argparse
import logging

from herokuadmintools import (
    find_affected_apps,
    find_users_missing_2fa,
    generate_csv,
    get_status_code,
    ORG_NAME,
    update_status_code,
    verify_access,
)


# boilerplate
logger = logging.getLogger(__name__)


def output_results(users_missing_2fa, affected_apps):
    if not users_missing_2fa:
        print('All {} users have 2FA enabled :)'.format(ORG_NAME))
        return

    print('The following {} users do not have 2FA enabled!'.format(ORG_NAME))
    for role, users in users_missing_2fa.items():
        print('\n~ {} {}s:'.format(len(users), role))
        for email in sorted(users):
            print(email)

    if affected_apps:
        print('\n{} apps are affected:\n'.format(len(affected_apps)))
        for app, emails in sorted(affected_apps.items()):
            print('{} ({})'.format(app, ', '.join(sorted(emails))))


def do_task(args):
    verify_access()
    users_missing_2fa = find_users_missing_2fa()
    affected_apps = find_affected_apps(users_missing_2fa)

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
    args = parser.parse_args(args=args)
    if args.debug:
        logger.setLevel(logging.DEBUG)
    return args


def main(args=None):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
    args = parse_args(args)
    do_task(args)
    raise SystemExit(get_status_code())
