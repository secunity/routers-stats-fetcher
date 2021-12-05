import sys
from threading import RLock
import logging

from share import to_bool, SETTING

_logger = {
    'logger': None,
    'lock': RLock(),
    'init': False,
}


def _init_logger(name=None, logfile=None, verbose=None, to_stdout=None, to_stderr=None, **kwargs):
    if not name:
        name = __name__
    if to_bool(to_stdout) is None:
        to_stdout = to_bool(kwargs.get('stdout'))
        if to_stdout is None:
            to_stdout = False
    if to_bool(to_stderr) is None:
        to_stderr = to_bool(kwargs.get('stderr'))
        if to_stderr is None:
            to_stderr = False
    if to_bool(verbose) is None:
        verbose = False

    with _logger['lock']:
        logger = _logger['logger']
        if logger:
            return logger

        logger = logging.getLogger(name)

        log_level = logging.DEBUG if verbose else logging.WARNING
        logger.setLevel(log_level)

        handlers = []
        if to_stdout:
            handlers.append(logging.StreamHandler(sys.stdout))
        if to_stderr:
            handlers.append(logging.StreamHandler(sys.stderr))
        if logfile:
            handlers.append(logging.FileHandler(logfile))

        for handler in handlers:
            handler.setLevel(log_level)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(lineno)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        _logger['logger'] = logger
        return logger


class logMeta(type):

    # def __prepare__(msc, name, **kwargs):
    #     _init_logger(**SETTING.section(SETTING.TYPE.LOG))
    #     return super().__prepare__(msc, name, **kwargs)

    def __call__(cls, *args, **kwargs):
        with _logger['lock']:
            if not _logger['init']:
                _init_logger(**SETTING.section(SETTING.TYPE.LOG))
                _logger['init'] = True
        return super().__call__(*args, **kwargs)

    # def __getattr__(self, item):
    #     if item.upper() in self._methods:
    #         return getattr(self._log(), item.lower())


class log(metaclass=logMeta):

    # _methods = ('CRITICAL', 'FATAL', 'ERROR', 'WARNING', 'WARN', 'INFO', 'DEBUG', 'EXCEPTION')

    @classmethod
    def _init_(cls):
        with _logger['lock']:
            if not _logger['init']:
                cls.init()

    @classmethod
    def init(cls, update={}, **kwargs):
        with _logger['lock']:
            _update = SETTING.section(SETTING.TYPE.LOG, copy=True)
            _update.update(update)

            _init_logger(**_update)
            _logger['init'] = True

    @classmethod
    def debug(cls, *args, **kwargs):
        cls._init_()
        return cls.logger().debug(*args, **kwargs)

    @classmethod
    def error(cls, *args, **kwargs):
        cls._init_()
        return cls.logger().error(*args, **kwargs)

    @classmethod
    def exception(cls, *args, **kwargs):
        return cls.logger().exception(*args, **kwargs)

    @classmethod
    def logger(cls):
        with _logger['lock']:
            return _logger['logger']


if __name__ == '__main__':
    log.debug('aa')
    log.debug('dfdf')
