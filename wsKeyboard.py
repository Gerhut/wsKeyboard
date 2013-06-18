from hashlib import sha1
from base64 import b64encode as base64
from ctypes import windll
from struct import unpack
from socket import gethostbyname_ex
from socket import gethostname
from SocketServer import TCPServer
from BaseHTTPServer import BaseHTTPRequestHandler

__all__ = ['WsKeyboardRequestHandler', 'start_wsKeyboard_server']

DEFAULT_PORT = 13579

'''DANGEROUS: use unpublished property: BaseHTTPRequestHandler.close_connection
'''


def key_down(code):
    windll.user32.keybd_event(code, 0, 0, 0)


def key_up(code):
    windll.user32.keybd_event(code, 0, 2, 0)


class WsKeyboardRequestHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def header_13(self):
        websocket_guid = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
        websocket_key = self.headers['Sec-WebSocket-Key']
        websocket_accept = sha1(websocket_key + websocket_guid).digest()
        websocket_accept = base64(websocket_accept)
        self.send_response(101, 'Switching Protocols')
        self.send_header('Connection', 'Upgrade')
        self.send_header('Upgrade', 'WebSocket')
        self.send_header('Sec-WebSocket-Accept', websocket_accept)
        self.end_headers()

    def handle_13(self):
        bytes = self.request.recv(2)
        if len(bytes) == 0:
            return False
        opcode = ord(bytes[0]) & 0x0F
        if opcode == 1:
            if ord(bytes[1]) >> 7 == 1:
                bytes = unpack('BBBBBB', self.request.recv(6))
                data = (bytes[0] ^ bytes[4], bytes[1] ^ bytes[5])
            else:
                data = unpack('BB', self.request.recv(2))
            if data[0] == 1:
                key_down(data[1])
            elif data[0] == 126:
                key_up(data[1])
        elif opcode == 8:
            return False
        return True

    def do_GET(self):
        if self.headers['Connection'] != 'Upgrade' \
                or self.headers['Upgrade'].lower() != 'websocket':
            self.send_error(400, 'Invalid WebSocket request.')
            return

        if self.headers['Sec-WebSocket-Version'] in ('13'):
            self.webSocket_version = self.headers['Sec-WebSocket-Version']

        if hasattr(self, 'header_' + str(self.webSocket_version)) \
                and hasattr(self, 'handle_' + str(self.webSocket_version)):
            header = getattr(self, 'header_' + str(self.webSocket_version))
            handle = getattr(self, 'handle_' + str(self.webSocket_version))
            header()
            while handle():
                pass
            self.close_connection = 1
        else:
            self.send_error(400, 'Unsupported WebSocket version.')
            return


def get_addresses(address_list=gethostbyname_ex(gethostname())):
    for address in address_list:
        if isinstance(address, str):
            yield address
        elif isinstance(address, list):
            for sub_address in get_addresses(address):
                yield sub_address


def start_wsKeyboard_server(port=DEFAULT_PORT):

    httpd = TCPServer(('', port), WsKeyboardRequestHandler)

    for address in get_addresses():
        print 'ws://%s:%d/' % (address, port)

    httpd.serve_forever()

if __name__ == '__main__':
    start_wsKeyboard_server()
