class ValueNotFound(BaseException):
    pass

class Configuration:
    def __init__(self, **kwargs):
        '''
        :param kwargs:
          py2 : iteritems()
          py3 : items()
        '''
        for k, v in kwargs.items():
            setattr(self, k, v)


    def update_configuration(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, item):
        if item not in self.__dict__.keys():
            raise ValueNotFound("Config flag \"%s\""%item)
        else:
            return self.__dict__[item]

    def __getitem__(self, item):
        try:
            return self.__dict__[item]
        except KeyError:
            raise ValueNotFound("Config flag \"%s\"" % item)

    def __repr__(self):
        return str("{!r}").format(self.__dict__)