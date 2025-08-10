import json
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend

class savedata:
	def __init__(self, filename, password=""):
		self.__filename=filename
		self.__password=password
		if self.__password:
			self.__password=self.__password.encode()
			salt=b"u\\1\xa6)\xb6\x89\xcf\xc6`\x89(\x95\x10\xf4\xdc"
			kdf=PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=100000, backend=default_backend())
			self.__password=base64.urlsafe_b64encode(kdf.derive(self.__password))
			self.__decrypter=Fernet(self.__password)
		self.__dict={}

	def load(self):
		with open(self.__filename, "rb") as file:
			if not self.__password:
				self.__dict=json.load(file)
			else:
				self.__dict=json.loads(self.__decrypter.decrypt(file.read()).decode())

	def save(self):
		with open(self.__filename, "wb") as file:
			if not self.__password:
				json.dump(self.__dict, file)
			else:
				file.write(self.__decrypter.encrypt(json.dumps(self.__dict).encode()))

	def add(self, name, value):
		self.__dict[name]=value

	def read(self, name):
		return self.__dict.get(name, None)
