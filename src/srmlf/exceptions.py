class SRMLFException(Exception):
    pass


class ProjectNotFoundException(SRMLFException):
    pass


class ProjectDuplicateException(SRMLFException):
    pass


class ProjectFileUnreadableException(SRMLFException, PermissionError):
    pass


class CorruptedProjectException(SRMLFException):
    pass
