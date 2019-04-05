import sys
import logging
import logging.handlers as handlers
import os
import os.path as path
import utils
import models
import json
from listUpdate import UpdateLister
import pprint
import argparse
import shutil
from logger import logger

changelog = None
patch_info = None
settings = None


def list_updates(args):
    """
    List updates available
    """
    logger.info("Listing updates available")
    ul = UpdateLister(patch_info=patch_info, changelog=changelog)
    packages = []
    if args.file is None:
        packages = ul.list_all()
        # print()

        # pp = pprint.PrettyPrinter(width=100)
        # pp.pprint(packages)
    else:
        if args.file:
            packages = ul.list_package_by_name(args.file)
    __print_update_info(packages, 50)


def __print_update_info(packages, length):
    print("application".ljust(50), "update_id".ljust(50), "version".ljust(50))
    print((50 * 3) * "-")
    for package in packages:
        # package_name = package['package_name'][package['package_name'].rfind('/') + 1:]
        # __print_update_info(package_name, package, 50)
        print(package["application"].ljust(length), package["update_id"].ljust(
            length), package["version"].ljust(length))


def roll_back(update_id, settings, changelog):
    """
    roll back the previous change
    """
    logger.info("Rolling back updates: [{}]...".format(update_id))
    logger.info("Performing validatity check...")
    if changelog.can_roll_back(update_id):
        logger.info("The udpate id can be rollbacked.")
        logger.info("Get change from change log to rollback")
        change = changelog.get_change(update_id)
        logger.info("Change obtained from change log, performing rollback")
        roll_back_change = _roll_back(change, settings)
        logger.info("Attach change to change log")
        changelog.apply_change(roll_back_change)
    else:
        logger.info("Cannot rollback the change.")


def _roll_back(change, settings):        
    udpate_id = change['update_id']
    tmp_dir = path.join('/tmp', udpate_id)
    logger.info("Sanitizing [{}]".format(tmp_dir))
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.mkdir(tmp_dir)    
    origin_zip = path.join(utils.sanitize_path(
        settings['backup_dir']), change['change_id'] + '.zip')
    
    logger.info("Start unzip...")
    utils.unzip_file(tmp_dir, origin_zip)
    logger.info("Unzip finished.")
    
    pack_file = path.join(tmp_dir, "package-info.json")
    logger.info("reading package-info.json from [{}]".format(pack_file))

    with open(pack_file, 'r') as f:
        content = f.read()
    package = json.loads(content)

    logger.info("creating rollback change...")
    roll_back_change = create_roll_back_change(change, package)
    logger.info("creation of rollback change finished")

    logger.info("start backing up files...")
    backup_location = utils.backup_file(roll_back_change, settings)
    logger.info("back up files finished")
    for file in roll_back_change['files_to_update']:
        logger.info("Performing rollback for file [{}]...".format(file))
        utils.do_single_file_move(tmp_dir, file, backup_location)
        logger.info("Performing rollback for file finished. [{}]".format(file))

    return roll_back_change


def create_roll_back_change(change, package_info):    
    package_info_dir = {key['src']: key for key in package_info}
    roll_back_change = {key: change[key] for key in change}
    roll_back_change['action'] = 'rollback'
    roll_back_change['change_id'] = utils.get_change_id(roll_back_change, settings)    
    roll_back_change['package_name'] = change['change_id']
    files_to_update = []
    for up in change['files_to_update']:
        file = {}
        file['src'] = os.path.basename(up['dst'])
        file['dst'] = up['dst']
        if file['src'] in package_info_dir:
            info = package_info_dir[file['src']]
            file['permission'] = info['permission']
            file['user'] = info['user']
            file['group'] = info['group']
        else:
            # set src to '' means delete dst file
            file['src'] = ''
            file['dst'] = up['dst']
        files_to_update.append(file)
    roll_back_change['files_to_update'] = files_to_update
    logger.info("Rollback change created:")
    logger.info(json.dumps(roll_back_change))
    return roll_back_change


def install_update(update_id, settings, patch_info):
    """
    install updates
    """
    logger.info("Install update::start...")
    logger.info("getting change from udpate_id: [{}]".format(update_id))
    potential = [
        change for change in patch_info.patch if change['update_id'] == update_id]
    if len(potential) <= 0:
        print_manual()
        logger.info("Change id does not exist in patch_info")
        return
    change = potential[0]    
    change = {key: val for key, val in change.items()}
    change['action'] = 'apply'
    change['change_id'] = utils.get_change_id(change, settings)
    
    logger.info("checking if change is appliable")
    if changelog.appliable(change):
        dir_to_down = path.join('/tmp', change['update_id'])
        logger.info("downloading files to [{}]".format(dir_to_down))
        utils.download_file(dir_to_down, settings, change)
        logger.info("downloading files finished")
        logger.info("instsalling...")
        __install_udpate(change, settings)
        logger.info("add change to change log.")
        changelog.apply_change(change)
        logger.info("doing test")
        success = utils.do_test(change, settings)        
        if not success:
            logger.info("Test failed, rollback change")
            roll_back(update_id, settings, changelog)
        logger.info("Test success, end")
    else:
        logger.info("Change is not appliable")
    logger.info("Install update::end")

def __install_udpate(change, settings):
    logger.info("Backing up files for change [{}]".format(change['change_id']))
    backup_tmp_dir = utils.backup_file(change, settings)
    logger.info("backed up file is in [{}]".format(backup_tmp_dir))    
    tmp_loc = '/tmp/' + change['change_id']
    logger.info("sanitizing [{}]".format(tmp_loc))
    if os.path.exists(tmp_loc):
        shutil.rmtree(tmp_loc)
    os.mkdir(tmp_loc)
    logger.info("Unziping file...")
    utils.unzip_file(tmp_loc, os.path.join(
        utils.sanitize_path(settings['download_dir']), change['update_id'], change['package_name']))
    logger.info("Unzip finished.")
    for file in change['files_to_update']:
        logger.info("Apply change for file [{}]".format(file))
        utils.do_single_file_move(tmp_loc, file, backup_tmp_dir)
    logger.info("cleaning [{}]".format(tmp_loc))
    shutil.rmtree(tmp_loc)
    logger.info("cleaning [{}]".format(backup_tmp_dir))
    shutil.rmtree(backup_tmp_dir)


def print_manual():
    print("This is print manual")
    print(changelog.can_roll_back(patch_info.patch[0]))


def load_change_log(file):
    logger.info("loading change log...")
    changelog = models.ChangeLog(file)
    logger.info("change log loaded.")
    return changelog


# TODO: To be changed to S3 Later
def get_patch_info(cur_dir):
    logger.info("getting patch info...")    
    path_file = os.path.join(
        cur_dir, '../samples/sample-for-patch-info.json')
    with open(path_file, 'r') as f:
        content = f.read()
    data = json.loads(content)
    patch_info = models.PatchInfo(data)
    logger.info("patch info got.")    
    return patch_info


if __name__ == "__main__":
    logger.info("loading settings...")    
    cur_dir = os.path.dirname(__file__)
    with open(os.path.join(cur_dir, 'settings.json'), 'r') as f:
        content = f.read()
    settings = json.loads(content)
    logger.info("setings loaded.")

    changelog = load_change_log(os.path.join(cur_dir, '../log/changelog.json'))
    patch_info = get_patch_info(cur_dir)

    parser = argparse.ArgumentParser(description='Rollback updater')
    sub_parser_list = parser.add_subparsers(dest='command')
    parser_l = sub_parser_list.add_parser('list',
                                          help='list files can be updated')
    parser_l.add_argument('--file', dest='file', help='file name')
    parser.add_argument('-r', '--rollback',
                        help='roll back files')
    parser.add_argument('-i', '--install',
                        help='install files files')
    parser.add_argument('-m', '--manual',
                        help='print manual')

    arguments = parser.parse_args()

    if len(sys.argv) < 2 or arguments.manual:
        print_manual()
    elif arguments.command == 'list':
        list_updates(arguments)
    elif arguments.rollback:
        roll_back(arguments.rollback, settings, changelog)
    elif arguments.install:
        install_update(arguments.install, settings, patch_info)
    else:
        print_manual()
