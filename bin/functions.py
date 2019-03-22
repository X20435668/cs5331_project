import sys
import logging
import logging.handlers as handlers
import os
import os.path as path
import utils
import models
import json

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
    if changelog.can_roll_back(change):     
        _roll_back(change)
        changelog.apply_change(change)

def _roll_back(change):

    pass


def install_update(change):
    """
    install updates
    """
    change['action']='apply'
    if changelog.appliable(change):
        __install_udpate(change)
        changelog.apply_change(change)
    

def __install_udpate(change):
    pass

def print_manual():
    print("This is print manual")
    print(changelog.can_roll_back(patch_info.patch[0]))


def load_change_log(file):
    changelog = models.ChangeLog(file)
    return changelog


# TODO: To be changed to S3 Later
def get_patch_info(cur_dir):
    path_file = os.path.join(
        cur_dir, '../samples/sample-for-patch-info.json')
    with open(path_file, 'r') as f:
        content = f.read()
    data = json.loads(content)
    patch_info = models.PatchInfo(data)
    return patch_info

if __name__ == "__main__":
    cur_dir = os.path.dirname(__file__)
    logger = setup_log()
    changelog = load_change_log(os.path.join(cur_dir, '../log/changelog.json'))
    patch_info = get_patch_info(cur_dir)

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
