class InvalidError(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        else:
            status_code = 400
        self.status_code_str = '0{}'.format(status_code)
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['result'] = self.status_code_str
        rv['resultMessage'] = 'Fail'
        rv['resultData'] = self.message
        return rv

class InvalidException(Exception):
    status_code = 500

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        else:
            status_code = 500
        self.status_code_str = '0{}'.format(status_code)
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['result'] = self.status_code_str
        rv['resultMessage'] = 'Fail'
        rv['resultData'] = self.message
        return rv