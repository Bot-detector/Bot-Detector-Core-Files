class Error(Exception):
    pass


class NoDataAvailable(Error):
    pass


class InvalidFileType(Error):
    pass