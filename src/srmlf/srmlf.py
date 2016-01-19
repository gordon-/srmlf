import argparse
import logging
import os
from datetime import datetime

import coloredlogs

from project import Project, SRMLFException, DATA_DIR


def valid_date(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError:
        msg = "Not a valid date: '{}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


def valid_user_contrib(s):
    try:
        name, amount = s.split(':')
        amount = float(amount)
        return name, amount
    except ValueError:
        msg = "Invalid format: '{}'.".format(s)
        raise argparse.ArgumentTypeError(msg)


def main():

    logger = logging.getLogger('srmlf')
    coloredlogs.install(fmt='%(message)s',
                        level=logging.INFO)
    try:

        parser = argparse.ArgumentParser(description='SRMLF is a lightweight '
                                         'accountability tracker')
        parser.add_argument('-v', '--verbose', help='Show debug info',
                            action='store_true', dest='verbose')

        commands = parser.add_subparsers(help='Commands help', dest='command')
        init = commands.add_parser('init', aliases=['i'])
        init.add_argument('project_name', help='Project to use',
                          action='store')
        init.add_argument('-t', '--total', help='Total amount to reach',
                          type=int,
                          action='store')
        init.add_argument('users', help='Names of users', type=str,
                          action='store', nargs='+')

        add = commands.add_parser('add', aliases=['a'])
        add.add_argument('project_name', help='Project to use',
                         action='store')
        add.add_argument('-d', '--date', help='International-formatted date of'
                         ' the contribution you want to create',
                         default=datetime.now(),
                         type=valid_date)
        add.add_argument('label', help='Label of the contribution',
                         type=str)
        add.add_argument('contribs', type=valid_user_contrib,
                         help='User names and amounts',
                         action='store', nargs='+')

        view = commands.add_parser('view', aliases=['v'])
        view.add_argument('project_name', help='Project to use',
                          action='store')

        args = parser.parse_args()

        if args.verbose:
            coloredlogs.increase_verbosity()

        if not os.path.isdir(DATA_DIR):
            logger.debug('Creating inexistant data directory (%s)', DATA_DIR)
            os.mkdir(DATA_DIR)

        if args.command == 'init':
            logger.info('Creating project %s…', args.project_name)
            Project.create(args.project_name, args.users, args.total)

        elif args.command == 'add':
            logger.info('Adding %d contribution%s…',
                        len(args.contribs),
                        's' if len(args.contribs) > 1 else '')
            project = Project(args.project_name)
            project.add_contribs(args.label, args.date, args.contribs)
            project.save()

        else:
            project = Project(args.project_name)
            print(project)

    except SRMLFException as e:
        logger.error(e)
    except Exception as e:
        logger.error(e)
        raise

if __name__ == '__main__':
    main()
