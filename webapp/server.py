#!/usr/bin/python
# Sets up an HTTPS server that serves directory contents
import sys
import ssl

"""
Very useful link: https://www.devdungeon.com/content/creating-self-signed-ssl-certificates-openssl
https://askubuntu.com/questions/893155/simple-way-of-enabling-sslv2-and-sslv3-in-openssl
"""

# Settings
listen_target = ('localhost', 9999)  # https://localhost:9999/
certificate_file = './certificate.pem'
private_key_file = './privkey.pem'

# Python 3 version
if sys.version_info[0] == 3:
    import http.server
    httpd = http.server.HTTPServer(listen_target, http.server.SimpleHTTPRequestHandler)

# Wrap the socket with SSL
httpd.socket = ssl.wrap_socket(httpd.socket,
               certfile=certificate_file, keyfile=private_key_file, server_side=True,
               ssl_version=ssl.PROTOCOL_TLSv1)

# Start listening
httpd.serve_forever()