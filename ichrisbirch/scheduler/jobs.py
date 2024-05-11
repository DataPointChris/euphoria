"""Jobs that run on the scheduler.

Jobs have to have the session created in this file,
since the session is not serializable and cannot be passed in as a parameter.
`SessionLocal` must be used instead of `get_sqlalchemy_session` because the generator produced
by the yield in `get_sqlalchemy_session` cannot be used as a context manager.
"""

import functools
import logging
import subprocess  # nosec
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Callable

import pendulum
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy import and_
from sqlalchemy import select

from ichrisbirch import models
from ichrisbirch.config import get_settings
from ichrisbirch.database.sqlalchemy.session import SessionLocal
from ichrisbirch.scheduler.postgres_backup_restore import PostgresBackupRestore
from ichrisbirch.scheduler.postgres_snapshot_to_s3 import AwsRdsSnapshotS3

settings = get_settings()
logger = logging.getLogger('scheduler.jobs')


daily_1am_trigger = CronTrigger(day='*', hour=1)
daily_115am_trigger = CronTrigger(day='*', hour=1, minute=15)
daily_3pm_trigger = CronTrigger(day='*', hour=15)
every_6_hour_18_minute = IntervalTrigger(hours=6, minutes=18)


@dataclass
class JobToAdd:
    """Dataclass for packaging jobs to add to the scheduler This class is really only necessary to make main.py more
    clean in adding jobs.
    """

    func: Callable
    trigger: Any
    id: str
    jobstore: str = 'ichrisbirch'
    replace_existing: bool = True

    def as_dict(self):
        return asdict(self)


def job_logger(func: Callable) -> Callable:
    """Decorator to log job start and completion."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f'started: {func.__name__}')
        start = pendulum.now()
        func(*args, **kwargs)
        elapsed = (pendulum.now() - start).in_words()
        logger.info(f'completed: {func.__name__} - {elapsed}')

    return wrapper


def find_git_root(path: Path = Path.cwd()) -> Path:
    command = ['git', 'rev-parse', '--show-toplevel']
    logger.debug(f'finding git root: {path}')
    try:
        git_root = subprocess.check_output(command, cwd=path)  # nosec
    except subprocess.CalledProcessError as e:
        logger.debug(e)
        logger.debug('exiting program')
        raise SystemExit(1)
    return Path(git_root.decode().strip())


@job_logger
def make_logs():
    logger.debug(f'The time is: {pendulum.now()}')
    logger.info(f'The current working directory is: {Path.cwd()}')
    logger.info(f'Git root is: {find_git_root()}')
    logger.warning('This is a warning')
    logger.error('PAUSE this job to stop the logs')


@job_logger
def decrease_task_priority() -> None:
    """Decrease priority of all tasks by 1."""
    with SessionLocal() as session:
        query = select(models.Task).filter(and_(models.Task.priority > 1, models.Task.complete_date.is_(None)))
        for task in session.scalars(query).all():
            task.priority -= 1
        session.commit()


@job_logger
def check_and_run_autotasks() -> None:
    """Check if any autotasks should run today and create tasks if so."""
    with SessionLocal() as session:
        for autotask in session.scalars(select(models.AutoTask)).all():
            if autotask.should_run_today:
                session.add(
                    models.Task(
                        name=autotask.name,
                        category=autotask.category,
                        priority=autotask.priority,
                        notes=autotask.notes,
                    )
                )
                autotask.last_run_date = datetime.now()
                autotask.run_count += 1
        session.commit()


@job_logger
def aws_postgres_snapshot_to_s3():
    """Wrapper to get the job logging and to be consistent because the function is too complex to reimplement.

    This function is an alternative to the postgres_backup for testing but it is difficult to restore from a snapshot.
    """
    rds_snap = AwsRdsSnapshotS3(bucket_prefix='postgres/snapshots', settings=settings)
    rds_snap.snapshot()


@job_logger
def postgres_backup():
    pbr = PostgresBackupRestore(
        environment=settings.ENVIRONMENT,
        backup_bucket=settings.aws.s3_backup_bucket,
        source_host=settings.postgres.host,
        source_port=settings.postgres.port,
        source_username=settings.postgres.username,
        source_password=settings.postgres.password,
    )
    pbr.backup()


jobs_to_add = [
    JobToAdd(
        func=make_logs,
        trigger=CronTrigger(minute='*'),
        id='make_logs',
    ),
    JobToAdd(
        func=decrease_task_priority,
        trigger=daily_1am_trigger,
        id='decrease_task_priority_daily',
    ),
    JobToAdd(
        func=check_and_run_autotasks,
        trigger=daily_115am_trigger,
        id='check_and_run_autotasks_daily',
    ),
    JobToAdd(
        func=aws_postgres_snapshot_to_s3,
        trigger=daily_3pm_trigger,
        id='aws_postgres_snapshot_to_s3_daily',
    ),
    JobToAdd(
        func=postgres_backup,
        trigger=every_6_hour_18_minute,
        id='postgres_backup_every_6_hour_18_minute',
    ),
]
