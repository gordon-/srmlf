import csv
import os
import logging
import locale
from collections import OrderedDict
from glob import glob
from datetime import datetime

import prettytable
from termcolor import colored

from .exceptions import \
    (ProjectNotFoundException, ProjectDuplicateException,
     ProjectFileUnreadableException, CorruptedProjectException)

DATA_DIR = os.path.join(os.getcwd(), 'srmlf_data')


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
            self.total = float(os.path.basename(self.filename)
                               .replace('{}_('.format(base_filename), '')
                               .replace(').csv', ''))

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
            raise ProjectFileUnreadableException('Project {} is not found.'
                                                 .format(project_name))

    def _consume_reader(self):
        self.fieldnames = self.reader.fieldnames
        for item in self.reader:
            ordered_item = OrderedDict()
            for field in self.fieldnames:
                ordered_item[field] = item.get(field, None)
            self.data.append(ordered_item)

    def _format(self, k, v):
        if k == 'Description':
            return colored(v, 'blue')
        elif k == 'Date':
            date = datetime.strptime(v, '%Y-%m-%d')\
                .strftime(locale.nl_langinfo(locale.D_FMT))
            return colored(date, 'cyan')
        else:
            if v != '':
                return locale.currency(float(v))
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

    def get_total_contribs(self):
        contribs = OrderedDict()
        for item in self.data:
            for k, v in item.items():
                if k not in ['Description', 'Date'] and v != '':
                    contribs[k] = contribs.get(k, 0) + float(v)
        return list(contribs.values())

    def save(self):
        with open(os.path.join(DATA_DIR, self.filename), 'w') as fd:
            writer = csv.DictWriter(fd, self.fieldnames)
            writer.writeheader()
            for line in self.data:
                writer.writerow(line)

    def prettify(self):
        p = prettytable.PrettyTable([colored(f, 'red')
                                     for f in self.fieldnames])
        for line in self.data:
            p.add_row([self._format(k, v) for k, v in line.items()])

        # sum up the total
        # p.hrules = prettytable.ALL
        contribs = self.get_total_contribs()
        total1 = [locale.currency(float(v)) for v in contribs]
        total2 = []
        for i, amount in enumerate(contribs):
            if self.total:
                total2.append('{:.2f}%'.format((contribs[i] / self.total)*100))
            else:
                total2.append('{:.2f}%'
                              .format((contribs[i] / sum(contribs))*100))
        p.add_row(['', colored('TOTAL', attrs=['bold'])] +
                  [colored(str(c), attrs=['bold']) for c in total1])
        p.add_row(['', colored('({})'.format(locale.currency(self.total)),
                               attrs=['bold'])
                   if self.total is not None else ''] +
                  [colored(str(c), attrs=['bold']) for c in total2])
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
