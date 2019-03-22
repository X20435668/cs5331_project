import sys
import logging
import logging.handlers as handlers
import os
import os.path as path
from . import utils
from . import models

logger = None
changelog = None
patch_info = None


def setup_log():
    logger = logging.getLogger('telegram-bot')
    logger.setLevel(logging.DEBUG)
    log_dir = "../log"
    if (not path.exists(log_dir)) or (not path.isdir(log_dir)):
        os.mkdir(log_dir)
    # create file handler that logs debug and higher level messages
    fh = handlers.RotatingFileHandler(
        path.join(log_dir, 'activity.log'), maxBytes=20*1024*1024, backupCount=5)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = handlers.RotatingFileHandler(
        path.join(log_dir, 'error.log'), maxBytes=20*1024*1024, backupCount=5)
    ch.setLevel(logging.ERROR)
    # create formatter and add it to the handlers
    ih = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)
    ih.setFormatter(formatter)
    # add the handlers to logger
    logger.addHandler(ch)
    logger.addHandler(fh)
    logger.addHandler(ih)
    return logger


def list_updates(args):
    """
    List updates available
    """
    pass


def roll_back(change):
    """
    roll back the previous change
    """
    can_perform_change = changelog.can_roll_back(change)
    if not can_perform_change:
        return
    _roll_back(change)


def _roll_back(update_id):
    
    pass


def install_update(args):
    """
    install updates
    """
    pass


def print_manual():
    print("This is print manual")
    pass


def load_change_log():
    pass


def get_patch_info():
    pass


if __name__ == "__main__":
    logger = setup_log()
    load_change_log()
    get_patch_info()
    if len(sys.argv) < 2:
        print_manual()
    elif sys.argv[1] == 'list':
        list_updates(sys.argv[2:])
    elif sys.argv[1] == 'rollback':
        roll_back(sys.argv[2:])
    elif sys.argv[1] == 'install':
        install_update(sys.argv[2:])
    else:
        print_manual()
