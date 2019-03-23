import re
import os
import stat
path = '${HOME}/.update/$HOME/${HOME}.abc'

result = re.findall(r"(\$\{?(\w+)\}?)",path)
print(result)
print(os.path.basename(path))
