import pytest

from srmlf import exceptions


def test_srmlf_exception():
    with pytest.raises(exceptions.SRMLFException):
        raise exceptions.SRMLFException()


def test_project_not_found_exception():
    with pytest.raises(exceptions.ProjectNotFoundException):
        raise exceptions.ProjectNotFoundException()

    with pytest.raises(exceptions.SRMLFException):
        raise exceptions.SRMLFException()


def test_project_duplicate_exception():
    with pytest.raises(exceptions.ProjectDuplicateException):
        raise exceptions.ProjectDuplicateException()

    with pytest.raises(exceptions.SRMLFException):
        raise exceptions.SRMLFException()


def test_project_file_unreadable_exception():
    with pytest.raises(exceptions.ProjectFileUnreadableException):
        raise exceptions.ProjectFileUnreadableException()

    with pytest.raises(exceptions.SRMLFException):
        raise exceptions.SRMLFException()


def test_corrupted_project_exception():
    with pytest.raises(exceptions.CorruptedProjectException):
        raise exceptions.CorruptedProjectException()

    with pytest.raises(exceptions.SRMLFException):
        raise exceptions.SRMLFException()
