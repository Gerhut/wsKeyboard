import os
from socket import gethostbyname_ex
from socket import gethostname
from BaseHTTPServer import HTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler

__all__ = ['start_web_server']

DEFAULT_PORT = 80
PARENT_DIR_FILES = set(['wskeyboard.js'])


class ParentDirHTTPRequestHandler(SimpleHTTPRequestHandler):

    def translate_path(self, path):
        dir(self)
        path = SimpleHTTPRequestHandler.translate_path(self, path)
        filedir, filename = os.path.split(path)
        if filename.lower() in PARENT_DIR_FILES:
            return os.path.join(os.path.split(filedir)[0], filename)
        else:
            return path


def get_addresses(address_list=gethostbyname_ex(gethostname())):
    for address in address_list:
        if isinstance(address, str):
            yield address
        elif isinstance(address, list):
            for sub_address in get_addresses(address):
                yield sub_address


def start_web_server(port=DEFAULT_PORT):

    httpd = HTTPServer(('', port), ParentDirHTTPRequestHandler)

    for address in get_addresses():
        print 'http://%s:%d/' % (address, port)

    httpd.serve_forever()

if __name__ == '__main__':
    try:
        port = input('Port(%d): ' % (DEFAULT_PORT,))
    except SyntaxError:
        port = DEFAULT_PORT

    start_web_server(port)
