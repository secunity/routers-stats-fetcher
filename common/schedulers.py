import datetime
import typing
from collections.abc import Iterable

from apscheduler.job import Job
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.triggers.base import BaseTrigger
from apscheduler.triggers.interval import IntervalTrigger
import pytz

from common.consts import SCHEDULER_SETTINGS
from common.logs import Log


_scheduler = None


def start_scheduler(start: bool = True,
                    threadpool_size: int = None,
                    timezone: object = None,
                    **kwargs):
    if start not in (True, False):
        start = SCHEDULER_SETTINGS['start']
    if not threadpool_size or threadpool_size <= 0:
        threadpool_size = SCHEDULER_SETTINGS['executor_threadpool_size']
    if not timezone:
        timezone = pytz.timezone(SCHEDULER_SETTINGS['timezone'])
    elif isinstance(timezone, str):
        timezone = pytz.timezone(timezone)

    global _scheduler
    _scheduler = BackgroundScheduler(executors={'default': ThreadPoolExecutor(threadpool_size)},
                                     job_defaults={'max_instances': 1},
                                     timezone=timezone)

    if start:
        _scheduler.start()
        Log.debug('scheduler initialized and started')
    else:
        Log.debug('scheduler initialized')

    return _scheduler


def shutdown_scheduler(wait: bool = True):
    _scheduler.shutdown(wait=wait)


def add_job(func: callable,
            interval: object,
            func_args: typing.Iterable = None,
            func_kwargs: dict = None,
            next_run_time: datetime.datetime = None,
            **kwargs) -> Job:

    if isinstance(interval, (int, float)):
        trigger = IntervalTrigger(seconds=interval)
    elif isinstance(interval, BaseTrigger):
        trigger = interval
    elif interval:
        error = f'invalid interval: "{interval}"'
        Log.error(error)
        raise ValueError(error)
    else:
        trigger = None

    if func_args:
        if isinstance(func_args, str) or not isinstance(func_args, Iterable):
            error = 'func_args must be Iterable'
            Log.error(error)
            raise ValueError(error)
        func_args = (_ for _ in func_args)

    if func_kwargs and not isinstance(func_kwargs, dict):
        error = 'func_kwargs must be of type dict'
        Log.error(error)
        raise ValueError(error)

    if next_run_time is not None:
        if isinstance(next_run_time, (int, float)):
            next_run_time = datetime.datetime.utcnow() + datetime.timedelta(seconds=next_run_time)
        elif isinstance(next_run_time, datetime.timedelta):
            next_run_time = datetime.datetime.utcnow() + next_run_time
        elif not isinstance(next_run_time, datetime.datetime):
            error = 'next_run_time ust be of type datetime.datetime'
            Log.error(error)
            raise ValueError(error)

    job = _scheduler.add_job(func=func,
                             trigger=trigger,
                             args=func_args,
                             kwargs=func_kwargs,
                             next_run_time=next_run_time)
    return job


def get_scheduler():
    return _scheduler
