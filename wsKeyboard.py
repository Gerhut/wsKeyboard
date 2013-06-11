import socket
import struct
import base64, hashlib
import win32api, win32con

cache = ''
def wsKeyboardServer(port):
	
	version = 0

	def handshake(client):
		data = client.recv(1024)
		
		if len(data) == 0:
			return False
		
		header, cache = data.split('\r\n\r\n', 1)
		header = header.split('\r\n')

		path = header[0].split(' ')[1]

		headers = dict()
		for line in header[1:]:
			key, value = line.split(': ', 1)
			headers[key] = value
		if headers['Upgrade'].lower() != 'websocket':
			return False

		res_headers = {
			'Connection': headers['Connection'],
			'Upgrade': headers['Upgrade']
		}

		location = 'ws://' + headers['Host'] + path
		
		if 'Sec-WebSocket-Key' in headers:
			version = 2
			key = headers['Sec-WebSocket-Key'].strip()
			guid = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'
			res_headers['Sec-WebSocket-Accept'] = \
				base64.b64encode(hashlib.sha1(key + guid).digest())
			res_content = ''
		elif 'Sec-WebSocket-Key1' in headers \
			and 'Sec-WebSocket-Key2' in headers:
			version = 1
			res_headers.update({
				'Sec-WebSocket-Origin': headers['Origin'],
				'Sec-WebSocket-Location': location
			})

			def number_space(key):
				number = 0
				space = 0
				for c in key:
					if c.isdigit():
						number = number * 10 + int(c)
					elif c == ' ':
						space += 1
				return number / space

			key1 = number_space(headers["Sec-WebSocket-Key1"])
			key2 = number_space(headers["Sec-WebSocket-Key2"])
			content = cache[:8]
			cache = cache[8:]
			key = struct.pack(">ii", key1, key2) + content
			res_content = hashlib.md5(key).digest()
		else:
			version = 0
			res_headers.update({
				'WebSocket-Origin': headers['Origin'],
				'WebSocket-Location': location
			})

		res_data = 'HTTP/1.1 101 Web Socket Protocol Handshake\r\n'
		for item in res_headers.items():
			res_data += '%s: %s\r\n' % item

		res_data += '\r\n' + res_content
		client.send(res_data)
		return True

	def recieve(client):
		while True:
			if version < 2:
				in_data = False
				data = ''
				while True:
					cache = client.recv(1)
					if len(cache) == 0:
						break
					if in_data:
						if cache == '\xFF':
							if len(data) == 0:
								break
							press(int(data))
							in_data = False
							data = ''
						else:
							data += cache[0]
					elif cache == '\x00':
						in_data = True
				break
			else:
				try:
					pData = client.recv(1024)
					if len(pData) == 0:
						break
				except:
					break
				else:
					code_length = ord(pData[1]) & 127
					if code_length == 126:
						masks = pData[4:8]
						data = pData[8:]
					elif code_length == 127:
						masks = pData[10:14]
						data = pData[14:]
					else:
						masks = pData[2:6]
						data = pData[6:]
					
					raw_str = ""
					i = 0
					for d in data:
						raw_str += chr(ord(d) ^ ord(masks[i%4]))
						i += 1

					press(int(raw_str))

	def press(code):
		print 'press', code
		win32api.keybd_event(code, 0, 0, 0)
		win32api.Sleep(20)
		win32api.keybd_event(code, 0, win32con.KEYEVENTF_KEYUP, 0)

	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.bind(("", port))
	sock.listen(1)

	while True:
		print 'Listening on port %d' % (port,)
		connection, address = sock.accept()
		print address, ' connected.'
		if(not handshake(connection)):
			print address, 'Invalid WebSocket.'
			continue
		recieve(connection)
		print address, ' disconnected.'
		connection.close()

if __name__ == '__main__':
	try:
		port = input('Port: ')
	except Exception:
		port = 13579

	wsKeyboardServer(port)