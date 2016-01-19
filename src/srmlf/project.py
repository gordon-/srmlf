import csv
import os
from glob import glob

DATA_DIR = os.path.join(os.getcwd(), 'data')


class SRMLFException(Exception):
    pass


class ProjectNotFoundException(SRMLFException):
    pass


class ProjectDuplicateException(SRMLFException):
    pass


class ProjectFileUnreadable(SRMLFException, PermissionError):
    pass


class Project:

    def __init__(self, project_name):
        self.data = []
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
            with open(os.path.join(DATA_DIR, self.filename), 'r') as fd:
                self.data = csv.DictReader(fd)
        except FileNotFoundError:
            raise ProjectNotFoundException('Project {} is not found.'
                                           .format(project_name))
        except PermissionError:
            raise ProjectNotFoundException('Project {} is not found.'
                                           .format(project_name))

    def add_user(self, user):
        pass

    @staticmethod
    def create(project_name, users, total=None):
        base_filename = project_name.replace('/', '-').replace(' ', '_')
        filename = '{}.csv'.format(base_filename)
        if os.path.isfile(os.path.join(DATA_DIR, filename)):
            raise ProjectDuplicateException('Project {} already exists'
                                            .format(project_name))
        g = glob(os.path.join(DATA_DIR, '{}(*).csv'.format(base_filename)))
        if len(g) > 1:
            raise ProjectDuplicateException(('Project {} has been '
                                             'found in many files')
                                            .format(project_name))
        if total is not None:
            filename = '{}_({}).csv'.format(project_name, total)
        with open(os.path.join(DATA_DIR, filename), 'w') as fd:
            writer = csv.DictWriter(fd, ['Description', 'Date'] + users)
            writer.writeheader()
        return Project(project_name)
