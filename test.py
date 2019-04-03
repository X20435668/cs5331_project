import re
import os
import stat
import pwd, grp
import uuid
import requests
# path = '${HOME}/.update/$HOME/${HOME}.abc'

# result = re.findall(r"(\$\{?(\w+)\}?)",path)
# print(result)
# print(os.path.basename(path))
# print(utils.sanitize_path(path))
# obj = {}
# path = '/home/huskypig/.update/dest/sample_binary'
# if os.path.isfile(path):
#     st = os.stat(path)
#     print(st.st_mode)
#     obj['permission'] = oct(st.st_mode)[-3:]
#     obj['user'] = pwd.getpwuid(st.st_uid)[0]
#     obj['group'] = grp.getgrgid(st.st_gid)[0]
#     obj['src'] = os.path.basename(path)
# print(obj)


# print(uuid.uuid4())
# joined = ' '.join(["abc", "cdfds", 'sdfsdf'])
# print("__{}__".format(joined))
# openssl x509 -in /etc/ssl/certs/apache-selfsigned.crt -out /etc/ssl/certs/apache-selfsigned.pem -outform PEM

import socket
import ssl
# import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager

# class Tls12HttpAdapter(HTTPAdapter):
#     """Transport adapter that forces use of TLSv1.2."""

#     def init_poolmanager(self, connections, maxsize, block=False):
#         """Create and initialize the urllib3 PoolManager."""
#         self.poolmanager = PoolManager(
#             num_pools=connections, maxsize=maxsize,
#             block=block, ssl_version=ssl.PROTOCOL_TLSv1_2) 
#         #ssl.PROTOCOL_TLSv1_2)


# url = 'https://116.15.140.189:5333'

# s = requests.Session()
# s.mount(url, Tls12HttpAdapter())
# r = s.get(url, verify=False)
# print(r.text)
# print(r.status_code)

# import ssl
# from urllib3.poolmanager import PoolManager

# from requests.adapters import HTTPAdapter



# class Ssl3HttpAdapter(HTTPAdapter):
#     """"Transport adapter" that allows us to use SSLv3."""

#     def init_poolmanager(self, connections, maxsize, block=False):
#         self.poolmanager = PoolManager(
#             num_pools=connections, maxsize=maxsize,
#             block=block, ssl_version=ssl.PROTOCOL_SSLv3)

# url = "https://116.15.140.189:5333"
# cafile = '/usr/share/ca-certificates/apache-selfsigned.crt' # http://curl.haxx.se/ca/cacert.pem
# r = requests.get(url, verify=False)
# print(r.status_code)
# print(r.text)

ssl._create_default_https_context = ssl._create_unverified_context
hostname = '116.15.140.189'
context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT) #ssl.create_default_context()
context.check_hostname = False
context.verify_mode = ssl.CERT_NONE
context.options &= ssl.OP_NO_TLSv1_2
context.options &= ssl.OP_NO_TLSv1_1
context.options &= ssl.OP_NO_TLSv1_3
# context.load_verify_locations("/etc/ssl/certs/apache-selfsigned.crt")
# context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
# context.load_cert_chain('/etc/ssl/certs/apache-selfsigned.pem', keyfile='/etc/ssl/private/apache-selfsigned.key')
# context.load_dh_params("/etc/ssl/certs/dhparam.pem")


with socket.socket(socket.AF_INET) as sock:
    print(sock)
    with context.wrap_socket(sock, server_hostname=hostname, ssl_version=ssl.PROTOCOL_TLS) as ssock:
        ssock.connect(('116.15.140.189',5333))
        print(ssock)
        print(ssock.version())
