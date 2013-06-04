import sys, re, hashlib, base64
from socket import *

class HeaderHandler:
	"""
	The HeaderHandler gets the response header from the websockets, it then parses and
	re-encripts the secret that has to get sent back to the websockets client, if the
	websockets client agrees that the GUID is correct it will complete the handshake and
	then the messages are handled by the MaskHandler
	"""
	def __init__(self, header):
		self.header = header;
		self.GUID = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'

	def getValue(self, key, header):
		matched = ""
		if key == "host":
			matched = re.search(r'Host: (.*)', header)
		elif key == "connection":
			matched = re.search(r'Connection: (.*)', header)
		elif key == "origin":
			matched = re.search(r'Origin: (.*)', header)
		elif key == "key":
			matched = re.search(r'Sec-WebSocket-Key: (.*)', header)
		elif key == "upgrade":
			matched = re.search(r'Upgrade: (.*)', header)

		seperated = re.split(r': ', matched.group())
		return seperated[1].strip()

	def getAnswer(self):
		val = self.getValue("key", self.header)
		full_web_key = (val + self.GUID).encode('utf-8')
		decoded = hashlib.sha1(full_web_key)
		final = base64.standard_b64encode(decoded.digest())
		return final.decode('utf-8')

	def getResponseHeader(self):
		upgrade_header = "HTTP/1.1 101 Switching Protocols\r\n" + "Upgrade: websocket\r\n"+"Connection: Upgrade\r\n"+"Sec-WebSocket-Accept: "+ self.getAnswer() +"\r\n\r\n";
		return bytes(upgrade_header, 'utf-8')

class MaskHandler:
	"""
	This entity manages the masking and unmasking of the messages sent by the
	websockets server
	"""

	def unmask(self, hexdata):
		pass

	def mask(self):
		pass

	def __init__(self):
		pass


class Server:
	"""
	The server itself starts a connection than accepts incoming connections from web sockets, it uses the Handlers
	to translate the messages given back and forth
	"""
	def stop(self):
		self.run = False
		self.server_socket.close()

	def accept(self):
		while self.run == True:
			conn, address = self.server_socket.accept()
			header = conn.recv(1024).decode('utf-8')
			response = HeaderHandler(header)
			conn.send(response.getResponseHeader())
			
			data = conn.recv(1024)
			print(data)
			conn.close()
			self.stop()

	def start(self, queue):
		self.server_socket = socket(AF_INET, SOCK_STREAM)
		self.server_socket.bind((self.host, self.addr))
		self.server_socket.listen(queue)

	def __init__(self, host, addr):
		self.host = host
		self.addr = addr
		self.run = True

server = Server('127.0.0.1', 5001)
server.start(5)
server.accept()
