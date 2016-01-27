import shutil
import os
import csv
import locale
from unittest.mock import MagicMock, Mock, patch
from io import StringIO
from collections import OrderedDict
from datetime import datetime

import pytest

from srmlf import project
from localemock import LocaleMock


@pytest.fixture
def project_file_1_fixture():
    with open(os.path.join('tests', 'fixtures', 'project1.csv')) as fd:
        s = StringIO()
        shutil.copyfileobj(fd, s)
    s.seek(0)
    return s


@pytest.fixture
def project_1_fixture():
    fd = project_file_1_fixture()
    op = Mock()
    op.return_value = fd
    with patch('srmlf.project.open', op, create=True):
        isfile = Mock()
        isfile.return_value = True
        with patch('os.path.isfile', isfile, create=True):
            p = project.Project('test')
    return p


def raiser(exc):
    def raiser_fn(*args, **kwargs):
        raise exc()
    return raiser_fn


def test_project_not_found():
    with pytest.raises(project.ProjectNotFoundException):
        project.Project('test')


def test_multiple_project_files():
    op = Mock()
    op.return_value = project_file_1_fixture
    with patch('srmlf.project.open', op, create=True):
        isfile = Mock()
        isfile.return_value = False
        with patch('os.path.isfile', isfile, create=True):
            glob = Mock()
            glob.return_value = ['test_(1000).csv', 'test_(10000).csv']
            with patch('glob.glob', glob, create=True):
                with pytest.raises(project.ProjectDuplicateException):
                    project.Project('test')


def test_corrupt_file():
    isfile = Mock()
    isfile.return_value = True
    with patch('os.path.isfile', isfile, create=True):
        op = Mock()
        s = StringIO()
        s.write('nope')
        s.seek(0)
        op.return_value = s
        with patch('srmlf.project.open', op, create=True):
            with pytest.raises(project.CorruptedProjectException):
                project.Project('test')


def test_project_init(project_file_1_fixture):
    op = Mock()
    op.return_value = project_file_1_fixture
    with patch('srmlf.project.open', op, create=True):
        isfile = Mock()
        isfile.return_value = True
        with patch('os.path.isfile', isfile, create=True):
            try:
                consume = project.Project._consume_reader
                project.Project._consume_reader = Mock()
                p = project.Project('test')
                assert p.name == 'test'
                assert p.filename == 'test.csv'
                assert p.fieldnames == []  # consume_reader is mocked
                assert p.total is None
                assert isinstance(p.reader, csv.DictReader)
                p._consume_reader.assert_called_once_with()
            finally:
                project.Project._consume_reader = consume


def test_project_init_errors(project_file_1_fixture):
    op = Mock()
    op.side_effect = raiser(FileNotFoundError)
    op.return_value = project_file_1_fixture
    with patch('srmlf.project.open', op, create=True):
        isfile = Mock()
        isfile.return_value = True
        with patch('os.path.isfile', isfile, create=True):
            with pytest.raises(project.ProjectNotFoundException):
                project.Project('test')


def test_project_init_errors_2(project_file_1_fixture):
    op = Mock()
    op.side_effect = raiser(PermissionError)
    op.return_value = project_file_1_fixture
    with patch('srmlf.project.open', op, create=True):
        isfile = Mock()
        isfile.return_value = True
        with patch('os.path.isfile', isfile, create=True):
            with pytest.raises(project.ProjectFileUnreadableException):
                project.Project('test')


def test_project_with_total_init(project_file_1_fixture):
    op = Mock()
    op.return_value = project_file_1_fixture
    with patch('srmlf.project.open', op, create=True):
        isfile = Mock()
        isfile.return_value = False
        with patch('os.path.isfile', isfile, create=True):
            glob = Mock()
            glob.return_value = ['test_(1000).csv']
            with patch('glob.glob', glob, create=True):
                try:
                    consume = project.Project._consume_reader
                    project.Project._consume_reader = Mock()
                    p = project.Project('test')
                    assert p.name == 'test'
                    assert p.filename == 'test_(1000).csv'
                    assert p.fieldnames == []  # consume_reader is mocked
                    assert p.total == 1000
                finally:
                    project.Project._consume_reader = consume


def test_consume_reader(project_file_1_fixture):
    op = Mock()
    op.return_value = project_file_1_fixture
    with patch('srmlf.project.open', op, create=True):
        isfile = Mock()
        isfile.return_value = True
        with patch('os.path.isfile', isfile, create=True):
            p = project.Project('test')
            assert isinstance(p.data, list)
            assert len(p.data) == 2
            assert isinstance(p.data[0], OrderedDict)
            assert p.fieldnames == ['Description', 'Date', 'Alice', 'Bob']
            assert list(p.data[0].keys()) == p.fieldnames
            assert p.data[0]['Alice'] == 10.0
            assert p.data[0]['Bob'] == 0
            assert p.data[0]['Description'] == 'First contribution'
            assert p.data[0]['Date'] == datetime(2016, 1, 21)

            assert p.data[1]['Alice'] == 0
            assert p.data[1]['Bob'] == 5.0
            assert p.data[1]['Description'] == 'Second contribution'
            assert p.data[1]['Date'] == datetime(2016, 1, 22)


def test_consume_reader_corrupt(project_file_1_fixture):
    proj = MagicMock()
    proj.data = []
    proj.reader.fieldnames = []
    with pytest.raises(KeyError):
        project.Project._consume_reader(proj)


def test_consume_reader_direct(project_file_1_fixture):
    proj = MagicMock()
    proj.data = []
    proj.reader = csv.DictReader(project_file_1_fixture)
    project.Project._consume_reader(proj)
    assert isinstance(proj.data, list)


def test_format():
    proj = Mock()
    with patch('srmlf.project.colored',
               side_effect=lambda v, c: '{c}: {v}'.format(v=v, c=c)):
        with LocaleMock(('en_US', 'UTF-8'), [locale.LC_TIME,
                                             locale.LC_MONETARY]):
            val = project.Project._format(proj, 'Description', 'test')
            assert val == 'blue: test'

            with pytest.raises(ValueError):
                val = project.Project._format(proj, 'Date', 'test')

            val = project.Project._format(proj, 'Date',
                                          datetime(2016, 1, 22))
            assert val == 'cyan: {}'.format(datetime(2016, 1, 22).strftime(
                locale.nl_langinfo(locale.D_FMT)))
            val = project.Project._format(proj, 'Alice', 10.0)
            assert val == locale.currency(10.0)
            val = project.Project._format(proj, 'Alice', 0.0)
            assert val == ''


def test_add_user(project_1_fixture):
    project_1_fixture.add_user('Régis')
    assert len(project_1_fixture.fieldnames) == 5
    assert 'Régis' in project_1_fixture.fieldnames
    assert len(project_1_fixture.data) > 0
    assert 'Régis' in project_1_fixture.data[0].keys()

    project_1_fixture.add_user('Date')
    assert len(project_1_fixture.fieldnames) == 5


def test_add_contribs(project_1_fixture):
    project_1_fixture.add_contribs('test', [('Alice', 30)],
                                   datetime(2016, 1, 22))
    assert len(project_1_fixture.data) == 3
    assert 'Alice' in project_1_fixture.data[2]
    assert project_1_fixture.data[2]['Alice'] == 30.0
    assert project_1_fixture.data[2]['Bob'] == 0.0
    assert project_1_fixture.data[2]['Date'] == '2016-01-22'


def test_add_contrib_today(project_1_fixture):
    project_1_fixture.add_contribs('test', [('Alice', 30)])

    assert project_1_fixture.data[2]['Date'] ==\
        datetime.now().strftime('%Y-%m-%d')


def test_add_contrib_new_user(project_1_fixture):
    project_1_fixture.add_contribs('test', [('John Doe', 1)])
    assert 'John Doe' in project_1_fixture.data[2]
    assert project_1_fixture.data[2]['John Doe'] == 1.0


def test_add_contrib_multiple_user(project_1_fixture):
    project_1_fixture.add_contribs('test', [('John Doe', 1), ('Alice', 20.1)])
    assert 'John Doe' in project_1_fixture.data[2]
    assert project_1_fixture.data[2]['John Doe'] == 1.0
    assert 'Alice' in project_1_fixture.data[2]
    assert project_1_fixture.data[2]['Alice'] == 20.1
