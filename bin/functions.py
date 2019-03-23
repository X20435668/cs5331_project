import sys
import logging
import logging.handlers as handlers
import os
import os.path as path
import utils
import models
import json
from bin.listUpdate.listUpdate import UpdateLister
import pprint
import argparse

logger = None
changelog = None
patch_info = None
settings = None


def setup_log():
    logger = logging.getLogger('updater')
    logger.setLevel(logging.DEBUG)
    log_dir = "../log"
    if (not path.exists(log_dir)) or (not path.isdir(log_dir)):
        os.mkdir(log_dir)
    # create file handler that logs debug and higher level messages
    fh = handlers.RotatingFileHandler(
        path.join(log_dir, 'activity.log'), maxBytes=20 * 1024 * 1024, backupCount=5)
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = handlers.RotatingFileHandler(
        path.join(log_dir, 'error.log'), maxBytes=20 * 1024 * 1024, backupCount=5)
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
    ul = UpdateLister()
    if len(args) == 0:
        packages = ul.list_all()
        pp = pprint.PrettyPrinter(width=1)
        pp.pprint(packages)
    else:
        if args.filename:
            ul.list_package_by_name(args.filename)



def roll_back(change):
    """
    roll back the previous change
    """
    if changelog.can_roll_back(change):
        _roll_back(change)
        changelog.apply_change(change)


def _roll_back(change):
    files_to_zip = []
    for up in change['files_to_update']:
        files_to_zip.append(up['dst'])
    utils.zip_files(change['change_id'], settings['backup_dir'], files_to_zip)

    pass


def install_update(change):
    """
    install updates
    """
    change['action'] = 'apply'
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
    with open(os.path.join(cur_dir, 'settings.json'), 'r') as f:
        content = f.read()
    settings = json.loads(content)
    logger = setup_log()
    changelog = load_change_log(os.path.join(cur_dir, '../log/changelog.json'))
    patch_info = get_patch_info(cur_dir)

    parser = argparse.ArgumentParser(description='Rollback updater')
    parser.add_argument('-l', '--list',
                        help='list files can be updated')
    parser.add_argument('-r', '--rollback',
                        help='roll back files')
    parser.add_argument('-i', '--install',
                        help='install files files')
    parser.add_argument('-m', '--manual',
                        help='print manual')

    arguments = parser.parse_args()

    if len(sys.argv) < 2 or arguments.manual:
        print_manual()
    elif arguments.list:
        list_updates(arguments.list)
    elif arguments.rollback:
        roll_back(arguments.rollback)
    elif arguments.install:
        install_update(arguments.install)
    else:
        print_manual()
