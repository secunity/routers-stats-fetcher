import sys
import logging

from common.consts import DEFAULTS


class LogMeta(type):

    def __getattr__(cls, item):
        if item.upper() in cls._methods:
            func = getattr(cls.logger(), item.lower())
            return func


class Log(metaclass=LogMeta):

    _logger = None

    _methods = ('CRITICAL', 'FATAL', 'ERROR', 'WARNING', 'WARN', 'INFO', 'DEBUG', 'EXCEPTION')

    @classmethod
    def initialize(cls, **kwargs) -> logging.Logger:
        return cls.logger(**kwargs)

    @classmethod
    def logger(cls,
               logfile_path: str = False,
               module: str = None,
               verbose: bool = True,
               to_stdout: bool = True,
               to_stderr: bool = False,
               **kwargs) -> logging.Logger:
        if cls._logger:
            return cls._logger

        logger = logging.getLogger(__name__)
        log_level = logging.DEBUG if verbose else logging.WARNING
        logger.setLevel(log_level)

        handlers = []
        if to_stdout:
            handlers.append(logging.StreamHandler(sys.stdout))
        if to_stderr:
            handlers.append(logging.StreamHandler(sys.stderr))

        if logfile_path:
            logfile = module if module else DEFAULTS["logfile_module"]
            logfile = f'{logfile_path}{logfile}.log'
            handlers.append(logging.FileHandler(logfile))

        for handler in handlers:
            handler.setLevel(log_level)
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(lineno)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        cls._logger = logger
        return logger
def a():
    Log.warning('bla blafsdsfada ')


if __name__ == '__main__':
    Log.initialize()
    a()
    Log.warning('bla bla ')
    Log.debug('bla bla ')
    Log.exception('sdfsdfsdfsdf')
