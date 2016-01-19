import csv
import os
import logging
from collections import OrderedDict
from glob import glob

from prettytable import PrettyTable
from termcolor import colored

DATA_DIR = os.path.join(os.getcwd(), 'srmlf_data')


class SRMLFException(Exception):
    pass


class ProjectNotFoundException(SRMLFException):
    pass


class ProjectDuplicateException(SRMLFException):
    pass


class ProjectFileUnreadable(SRMLFException, PermissionError):
    pass


class CorruptedProjectException(SRMLFException):
    pass


class Project:

    def __init__(self, project_name):
        self.data = []
        self.fieldnames = []
        self.logger = logging.getLogger('srmlf')
        self.name = project_name
        base_filename = project_name.replace('/', '-').replace(' ', '_')
        self.filename = '{}.csv'.format(base_filename)
        self.total = None
        if not os.path.isfile(os.path.join(DATA_DIR, self.filename)):
            g = glob(os.path.join(DATA_DIR,
                                  '{}_(*).csv'.format(base_filename)))
            if len(g) != 1:
                if len(g) == 0:
                    raise ProjectNotFoundException('Project {} is not found.'
                                                   .format(project_name))
                else:
                    raise ProjectDuplicateException(('Project {} has been '
                                                     'found in many files')
                                                    .format(project_name))
            self.filename = g[0]

        try:
            self.logger.debug('Opening %s',
                              os.path.join(DATA_DIR, self.filename))
            with open(os.path.join(DATA_DIR, self.filename), 'r') as fd:
                self.reader = csv.DictReader(fd)
                try:
                    self._consume_reader()
                except (KeyError, ValueError) as e:
                    raise CorruptedProjectException(e)
        except FileNotFoundError:
            raise ProjectNotFoundException('Project {} is not found.'
                                           .format(project_name))
        except PermissionError:
            raise ProjectNotFoundException('Project {} is not found.'
                                           .format(project_name))

    def _consume_reader(self):
        self.fieldnames = self.reader.fieldnames
        for item in self.reader:
            ordered_item = OrderedDict()
            for field in self.fieldnames:
                ordered_item[field] = item.get(field, None)
            self.data.append(ordered_item)

    def _color(self, k, v):
        if k == 'Description':
            return colored(v, 'blue')
        elif k == 'Date':
            return colored(v, 'cyan')
        else:
            return v

    def add_user(self, user):
        self.fieldnames.append(user)

    def add_contribs(self, name, date, contribs):
        line = OrderedDict()
        line['Description'] = name
        line['Date'] = date.strftime('%Y-%m-%d')
        for user, amount in contribs:
            if user not in self.fieldnames:
                self.add_user(user)
            line[user] = amount
        self.data.append(line)

    def save(self):
        with open(os.path.join(DATA_DIR, self.filename), 'w') as fd:
            writer = csv.DictWriter(fd, self.fieldnames)
            writer.writeheader()
            for line in self.data:
                writer.writerow(line)

    def prettify(self):
        p = PrettyTable([colored(f, 'red') for f in self.fieldnames])
        for line in self.data:
            p.add_row([self._color(k, v) for k, v in line.items()])
        return p

    def __str__(self):
        return self.prettify().__str__()

    @staticmethod
    def create(project_name, users, total=None):
        base_filename = project_name.replace('/', '-').replace(' ', '_')
        filename = '{}.csv'.format(base_filename)
        if os.path.isfile(os.path.join(DATA_DIR, filename)):
            raise ProjectDuplicateException('Project {} already exists'
                                            .format(project_name))
        g = glob(os.path.join(DATA_DIR, '{}_(*).csv'.format(base_filename)))
        if len(g) > 1:
            raise ProjectDuplicateException(('Project {} has been '
                                             'found in many files')
                                            .format(project_name))
        if total is not None:
            filename = '{}_({}).csv'.format(base_filename, total)
        with open(os.path.join(DATA_DIR, filename), 'w') as fd:
            writer = csv.DictWriter(fd, ['Description', 'Date'] + users)
            writer.writeheader()
        return Project(project_name)
