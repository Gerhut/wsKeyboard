from hashlib import sha1
from base64 import b64encode as base64
from struct import pack
from struct import unpack
from socket import gethostbyname_ex
from socket import gethostname
from SocketServer import TCPServer
from BaseHTTPServer import BaseHTTPRequestHandler

__all__ = ['start_wsKeyboard_server']

DEFAULT_PORT = 13579

'''DANGEROUS: use unpublished property: BaseHTTPRequestHandler.close_connection
'''


class WebSocketRequestHandler(BaseHTTPRequestHandler):
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
        while True:
            data = ''
            fin = False
            while not fin:
                b = self.request.recv(1)
                if len(b) == 0:
                    return
                else:
                    b = ord(b)
                fin = bool(b >> 7)
                '''
                *  0 denotes a continuation frame
                *  1 denotes a text frame
                *  2 denotes a binary frame
                *  8 denotes a connection close
                *  9 denotes a ping
                *  A denotes a pong
                '''
                data_type = b & 0x0F
                b = ord(self.request.recv(1))
                mask = bool(b >> 7)
                payload_length = b & 0x7F
                if payload_length == 126:
                    payload_length, = unpack('H', self.request.recv(2))
                elif payload_length == 127:
                    payload_length, = unpack('Q', self.request.recv(8))
                if mask:
                    mask = unpack('BBBB', self.request.recv(4))
                frame_data = unpack('B' * payload_length, self.request.recv(payload_length))
                for index, value in enumerate(frame_data):
                    data += chr(value ^ mask[index % 4])
            if data_type == 1:
                if hasattr(self, 'do_TEXT'):
                    do_TEXT(data)
                print 'Receive text data: ' + repr(data)
            elif data_type == 2:
                if hasattr(self, 'do_BINARY'):
                    do_BINARY(data)
                print 'Receive binary data: ' + repr(data)
            elif data_type == 8:
                print 'Connection close.'
                break


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
            handle()
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

    httpd = TCPServer(('', port), WebSocketRequestHandler)

    for address in get_addresses():
        print 'ws://%s:%d/' % (address, port)

    httpd.serve_forever()

if __name__ == '__main__':
    try:
        port = input('Port(%d): ' % (DEFAULT_PORT,))
    except SyntaxError:
        port = DEFAULT_PORT

    start_wsKeyboard_server(port)
