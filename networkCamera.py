import socket
import mycam
from threading import Thread
import time
import io
import socket

class networkCamera(picamera.PiCamera):

	def __init__(self):
		self.client_socket = socket.socket()
	def _thStreamCapture(self,total,nbr):
		start = time.time()
		stream = io.BytesIO()
		connection = self.client_socket.makefile('wb')
		self.lockCam.acquire()
		try:
			for i in range(nbr):
				self.lockCam.acquire()
				try:
					self.cam.capture(stream, 'jpeg')
				finally:
					self.cam.release()
				#Write the length of the capture to the stream and flush to ensure it acutally gets send
				connection.write(struct.pack('<L',stream.tell()))
				connection.flush()
				stream.seek(0)
				connection.write(stream.read())
				if time.time() - start > total:
					break
				stream.seek(0)
				stream.truncate()
			connection.write(struct.pack('<L',0))
		finally:
			self.lockCam.release()
			connection.close()
			self.client_socket.close()
	def _thStreamVideo(self,formatVideo,time):
		connection = self.client_socket.makefile('wb')
		self.lockCam.acquire()
		try:
			self.cam.start_preview()
			time.sleep(1)
			self.cam.start_recording(connection,formatVideo=format)
			self.cam.wait_recording(time)
		finally:
			self.cam.stop_recording()
			connection.close()
			self.client_socket.close()
			self.lockCam.release()
			
	def Connect(self,hostname,port):
		self.client_socket.connect((hostname,port))
	def Stream_Capture(self,nbr=30,totaltime=30):
		Thread(target=self._thStreamCapture,args=(total,nbr)).start()
	def Stream_Recording(self,formatVideo="h264",time=60):
		assert formatVideo in ("h264",)
		assert 0<time

		Thread(target=self._thStreamVideo,args=())
