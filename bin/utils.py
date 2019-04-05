import zipfile
import shutil
import os
import uuid
import re
import pwd
import grp
import json
import os.path as path
from logger import logger
import subprocess

def zip_files(zip_file_name, saved_dir, files_to_zip):
    logger.info("zip files as [{}] to [{}]".format(zip_file_name, saved_dir))
    with zipfile.ZipFile(os.path.join(saved_dir, zip_file_name), 'x') as zipMe:
        for file in files_to_zip:
            logger.info("adding file [{}]".format(file))
            zipMe.write(file, path.basename(file),
                        compress_type=zipfile.ZIP_DEFLATED)
    logger.info("zip files finished.")

def unzip_file(tmp_dir_to_unzip, zip_file):
    logger.info("Unzipping file [{}] to [{}]".format(zip_file, tmp_dir_to_unzip))    
    with zipfile.ZipFile(zip_file, 'r') as zipFile:
        zipFile.extractall(tmp_dir_to_unzip)
    logger.info("unzip finished.")


def backup_file(change, settings):
    logger.info("getting files to backup")    
    files_to_backup = [sanitize_path(x['dst'])
                       for x in change['files_to_update'] if os.path.isfile(sanitize_path(x['dst']))]                    
    conf_dir = os.path.join("/tmp", str(uuid.uuid4()))    
    os.mkdir(conf_dir)
    logger.info("made tmp folder to copy files: [{}]".format(conf_dir))
    file_list = []
    for file in change['files_to_update']:
        obj = {}
        path = sanitize_path(file['dst'])
        if os.path.isfile(path):
            st = os.stat(path)
            obj['permission'] = oct(st.st_mode)[-3:]
            obj['user'] = pwd.getpwuid(st.st_uid)[0]
            obj['group'] = grp.getgrgid(st.st_gid)[0]
            obj['src'] = os.path.basename(path)
            file_list.append(obj)
            shutil.copy(path, conf_dir)
    conf_file = os.path.join(conf_dir, "package-info.json")
    with open(conf_file, 'w+') as f:
        json.dump(file_list, f, indent=4,
                  separators=(',', ': '), sort_keys=True)
    logger.info("Write package-info.json file as:")
    logger.info(json.dumps(file_list, indent=4,
                  separators=(',', ': '), sort_keys=True))
    files_to_backup.append(conf_file)
    zip_files(change['change_id']+'.zip',
              sanitize_path(settings['backup_dir']), files_to_backup)
    for file in change['files_to_update']:
        if os.path.isfile(path):
            os.remove(sanitize_path(file['dst']))
    return conf_dir


def sanitize_path(path):
    result = re.findall(r'(\$\{?(\w+)\}?)', path)
    for group in result:
        if group[1] in os.environ:
            path = path.replace(group[0], os.environ[group[1]])
    return path


def do_single_file_move(base_dir, file, origin_tmp_dir):
    dest_file = sanitize_path(file['dst'])
    if file['src'] == '':
        # it is done in backup files.
        logger.info("removing [{}]".format(file['dst']))
        os.remove(dest_file)
    else:
        if 'is_config' in file and file['is_config'] == True:
            logger.info("performing config file change...")
            delimeter = file['delimeter']
            config = {}
            with open(path.join(base_dir, file['src']), 'r') as f:
                content = f.readlines()
            config = {line.split(delimeter)[0].strip(): {"value":delimeter.join(
                line.split(delimeter)[1:]), "installed":False} for line in content}
            file_name = os.path.basename(dest_file)
            with open(path.join(origin_tmp_dir, file_name), 'r') as f:
                content = f.readlines()
            with open(dest_file, 'w+') as f:
                logger.info("opening file to write: [{}]".format(dest_file))
                for line in content:
                    key, value = line.split(delimeter)[0], delimeter.join(
                        line.split(delimeter)[1:])
                    print("key:value-> [{}]:[{}]".format(key,value))
                    if key.strip() in config:
                        f.write("{}{}{}\n".format(key, delimeter, config[key]['value']))
                        config[key]['installed']=True
                    else:
                        f.write("{}".format(line))
                for key, value in config.items():
                    if value['installed'] == False:
                        logger.info("appending: {}{}{}\n".format(key, delimeter, value['value']))
                        f.write("{}{}{}\n".format(key, delimeter, value['value']))
            logger.info("config file change done.")
        else:
            shutil.copy(os.path.join(base_dir, file['src']), dest_file)
            os.chmod(dest_file, int(file['permission'], 8))
            uid = pwd.getpwnam(file['user']).pw_uid
            gid = grp.getgrnam(file['group']).gr_gid
            os.chown(dest_file, uid, gid)


def download_file(dir_to_down, settings, change):
    logger.info("downloading file [{}]...".format(change['package_name']))
    if os.path.isdir(dir_to_down):
        shutil.rmtree(dir_to_down)
    os.mkdir(dir_to_down)

    shutil.copy(path.join(sanitize_path(
        settings['zip_dir']), change['package_name']), dir_to_down)
    logger.info("file downloaded to [{}]".format(dir_to_down))

def do_test(change, settings):
    setting = [s['test_script'] for s in settings['test'] if s['application']]
    try:
        test_file = sanitize_path(setting[0])
        logger.info("runing test file: [{}]".format(test_file))
        sp = subprocess.run([
            "python", test_file], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)        
        sp.check_returncode()
        logger.info(sp.stdout)
        logger.info(sp.stderr)
    except subprocess.CalledProcessError as e:
        logger.error(e)
        return False
    return True

def get_change_id(change, settings):
    logger.info("getting change id...")
    change_id = '{}-{}'.format(change['action'], change['update_id'])
    file_list = os.listdir(sanitize_path(settings['backup_dir']))
    same_name = [ f for f in file_list if change_id in f]
    if len(same_name)>0:
        change_id = change_id + "-" + str(len(same_name))
    logger.info("change id is [{}]".format(change_id))
    return change_id
