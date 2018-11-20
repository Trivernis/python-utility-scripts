import logging
from logging.config import fileConfig

from lib import fsutils


def get_logger(name=None):
    fsutils.dir_exist_guarantee('logs')
    fileConfig('./conf/logging.config')
    if name:
        return logging.getLogger(name)
    else:
        return logging.getLogger()
