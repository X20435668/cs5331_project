import zipfile, shutil
import os, uuid, re, pwd, grp, json


def zip_files(zip_file_name, saved_dir, files_to_zip):
    with zipfile.ZipFile(os.path.join(saved_dir,zip_file_name), 'w') as zipMe:        
        for file in files_to_zip:
            zipMe.write(file, compress_type=zipfile.ZIP_DEFLATED)
def unzip_file(tmp_dir_to_unzip, zip_file):
    with zipfile.ZipFile(zip_file, 'r') as zipFile:
        zipFile.extractall(tmp_dir_to_unzip)
def backup_file(change, settings):
    files_to_backup = [sanitize_path(x['dst'])
                       for x in change['files_to_update'] if os.path.isfile(x['dst'])]
    conf_dir = os.path.join("/tmp", str(uuid.uuid4()))
    os.mkdir(conf_dir)
    file_list = []
    for file in change['files_to_update']:
        obj = {}
        path = sanitize_path(file['dst'])
        st = os.stat(path)
        obj['permission'] = oct(st.st_mode)[2:]
        obj['user'] = pwd.getpwuid(st.st_uid)[0]
        obj['group'] = grp.getgrgid(st.st_gid)[0]
        obj['src'] = os.path.basename(path)
        file_list.append(obj)
    conf_file = os.path.join(conf_dir, "package-info.json")
    with open(conf_file, 'w') as f:
        json.dump(file_list, f)
    files_to_backup.append(conf_dir)
    zip_files(change['change_id'],
                    settings['backup_dir'], files_to_backup)
def sanitize_path(path):
    result = re.findall(r'(\$\{(\w+)\})', path)
    for group in result:
        if group[1] in os.environ:
            path = path.replace(group[0], os.environ[group[0]])
    return path
def do_single_file_move(base_dir, file):
    dest_file = sanitize_path(file['dst'])
    shutil.copy(os.path.join(base_dir, file['src']), dest_file)
    os.chmod(dest_file, int(file['permission'], 8))
    uid = pwd.getpwnam(file['user']).pw_uid
    gid = grp.getgrnam(file['group']).gr_gid
    os.chown(dest_file, uid, gid)

def download_file(dir_to_down, settings, change):
    pass
