import SocketServer
import socket
import SimpleHTTPServer

def webServer(port=80):
	Handler = SimpleHTTPServer.SimpleHTTPRequestHandler
	httpd = SocketServer.TCPServer(("", port), Handler)
	
	ipList = socket.gethostbyname_ex(socket.gethostname())
	for ips in ipList:
	    if type(ips) != list:
	    	continue
	    for ip in ips:
	    	print 'http://%s:%d/' % (ip, port)
	httpd.serve_forever()

if __name__ == '__main__':
	try:
		port = input('Port: ')
	except Exception:
		port = 80

	webServer(port)