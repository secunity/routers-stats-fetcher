from threading import Lock
import copy as _copy

__BOOL_TYPES__ = (True, False)


def to_bool(x):
    if x in __BOOL_TYPES__:
        return x
    if not isinstance(x, str):
        return None
    x = x.lower()
    return True if x == 'true' else False if x == 'false' else None



class SETTING:

    class TYPE:
        LOG = 'log'


    _settings = {
        'lock': Lock(),

        TYPE.LOG: {
            'logfile': None,
            'verbose': False,
            'dump': None,
        }
    }


    @classmethod
    def get(cls, type,  key, copy=False):
        with cls._settings['lock']:
            value = cls._settings[type][key]
            return _copy.deepcopy(value) if copy else value

    @classmethod
    def section(cls, type, copy=False):
        with cls._settings['lock']:
            value = cls._settings[type]
            return _copy.deepcopy(value) if copy else value

    @classmethod
    def set(cls, type, key, value):
        with cls._settings['lock']:
            cls._settings[type][key] = value

    @classmethod
    def update(cls, updte=None, type=None, **kwargs):
        if not updte:
            updte = kwargs.get('update')
        if not updte:
            raise ValueError('updte')
        with cls._settings['lock']:
            (cls._settings if not type else cls._settings[type]).update(updte)
