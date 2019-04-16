from listUpdate import UpdateLister
import functions
from logger import logger
import os
import json
import time

logger.info("loading settings...")    
cur_dir = os.path.dirname(__file__)
with open(os.path.join(cur_dir, 'settings.json'), 'r') as f:
    content = f.read()
settings = json.loads(content)
logger.info("settings loaded.")

changelog = functions.load_change_log(os.path.join(cur_dir, '../log/changelog.json'))
while(True):
    patch_info = functions.get_patch_info(cur_dir)
    ul = UpdateLister(patch_info=patch_info, changelog=changelog)
    packages = ul.list_all()
    for package in packages:
        functions.install_update(package["update_id"], settings, patch_info, changelog)
    time.sleep(24*60*60)
