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
    if changelog.can_roll_back(update_id):
        change = changelog.get_change(update_id)
        roll_back_change = _roll_back(change, settings)
        changelog.apply_change(roll_back_change)
    else:
        print("Cannot rollback")


def _roll_back(change, settings):
    udpate_id = change['update_id']
    tmp_dir = path.join('/tmp', udpate_id)
    if os.path.exists(tmp_dir):
        shutil.rmtree(tmp_dir)
    os.mkdir(tmp_dir)
    origin_zip = path.join(utils.sanitize_path(
        settings['backup_dir']), change['change_id'] + '.zip')
    utils.unzip_file(tmp_dir, origin_zip)
    pack_file = path.join(tmp_dir, "package-info.json")
    with open(pack_file, 'r') as f:
        content = f.read()
    package = json.loads(content)

    roll_back_change = create_roll_back_change(change, package)
    backup_location = utils.backup_file(roll_back_change, settings)
    for file in roll_back_change['files_to_update']:
        utils.do_single_file_move(tmp_dir, file, backup_location)

    return roll_back_change


def create_roll_back_change(change, package_info):
    package_info_dir = {key['src']: key for key in package_info}
    roll_back_change = {key: change[key] for key in change}
    roll_back_change['action'] = 'rollback'
    roll_back_change['change_id'] = utils.get_change_id(change, settings)    
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

    return roll_back_change


def install_update(update_id, settings, patch_info):
    """
    install updates
    """
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
    
    dir_to_down = path.join('/tmp', change['update_id'])

    utils.download_file(dir_to_down, settings, change)
    
    if changelog.appliable(change):
        __install_udpate(change, settings)
        changelog.apply_change(change)
        success = utils.do_test(change, settings)
        if not success:
            roll_back(update_id, settings, changelog)
    else:
        logger.info("Change is not appliable")


def __install_udpate(change, settings):
    backup_tmp_dir = utils.backup_file(change, settings)
    tmp_loc = '/tmp/' + change['change_id']
    if os.path.exists(tmp_loc):
        shutil.rmtree(tmp_loc)
    os.mkdir(tmp_loc)
    utils.unzip_file(tmp_loc, os.path.join(
        utils.sanitize_path(settings['download_dir']), change['update_id'], change['package_name']))
    for file in change['files_to_update']:
        utils.do_single_file_move(tmp_loc, file, backup_tmp_dir)
    shutil.rmtree(tmp_loc)
    shutil.rmtree(backup_tmp_dir)


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
    logger.info("Hello world")
    cur_dir = os.path.dirname(__file__)
    with open(os.path.join(cur_dir, 'settings.json'), 'r') as f:
        content = f.read()
    settings = json.loads(content)

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
