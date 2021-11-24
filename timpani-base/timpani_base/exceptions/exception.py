import datetime

class SSHCommandException(Exception):
    pass

class SSHConnetException(Exception):

    def __init__(self, message):
        Exception.__init__(message)
        self.when = datetime.now()
        self.message = message