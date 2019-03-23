import re
import os
import stat
import bin.utils as utils
import pwd, grp
path = '${HOME}/.update/$HOME/${HOME}.abc'

result = re.findall(r"(\$\{?(\w+)\}?)",path)
print(result)
print(os.path.basename(path))
print(utils.sanitize_path(path))
obj = {}
path = '/home/huskypig/.update/dest/sample_binary'
if os.path.isfile(path):
    st = os.stat(path)
    print(st.st_mode)
    obj['permission'] = oct(st.st_mode)[-3:]
    obj['user'] = pwd.getpwuid(st.st_uid)[0]
    obj['group'] = grp.getgrgid(st.st_gid)[0]
    obj['src'] = os.path.basename(path)
print(obj)
