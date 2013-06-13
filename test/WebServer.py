import os
import socket
import SocketServer
import SimpleHTTPServer


def start_web_server(port=80):

    class ParentDirHTTPRequestHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):

        PARENT_DIR_FILES = set(['wskeyboard.js'])

        def translate_path(self, path):
            dir(self)
            path = SimpleHTTPServer.SimpleHTTPRequestHandler.translate_path(self, path)
            filedir, filename = os.path.split(path)
            if filename.lower() in self.PARENT_DIR_FILES:
                return os.path.join(os.path.split(filedir)[0], filename)
            else:
                return path

    def get_addresses(address_list=socket.gethostbyname_ex(socket.gethostname())):
        for address in address_list:
            if isinstance(address, str):
                yield address
            elif isinstance(address, list):
                for sub_address in get_addresses(address):
                    yield sub_address

    httpd = SocketServer.TCPServer(('', port), ParentDirHTTPRequestHandler)

    for address in get_addresses():
        print 'http://%s:%d/' % (address, port)

    httpd.serve_forever()

if __name__ == '__main__':
    DEFAULT_PORT = 80
    try:
        port = input('Port(%d): ' % (DEFAULT_PORT,))
    except SyntaxError:
        port = DEFAULT_PORT

    start_web_server(port)
