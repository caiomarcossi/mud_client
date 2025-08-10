import wx
from telnetlib import Telnet
import threading
from threading import Thread
from sound_lib import stream, output
from accessible_output2 import outputs
import sys
import re
import os
from time import sleep
import accessibility as ACC
from savedata import savedata
import math

class Program(wx.Frame):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.output=output.Output()
		self.soundStyle=r"\((.*?)\)"
		self.streams=[]
		self.host=wx.GetTextFromUser("Digite o endereço do MUD", "client", "mud.fantasticmud.com")
		try:
			self.port=int(wx.GetTextFromUser("Digite a porta do mud", "Client", "4000"))
		except:
			wx.MessageBox("Porta inválida", "Erro", wx.ICON_ERROR)
			sys.exit()
		self.initUI()

	def initUI(self):
		panel=wx.Panel(self)
		labelInputBox=wx.StaticText(panel, label="&Entrada")
		self.inputBox=wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.TE_DONTWRAP|wx.TE_PROCESS_ENTER)
		labelOutputBox=wx.StaticText(panel, label="&Saída")
		self.outputBox=wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP)
		self.inputBox.Bind(wx.EVT_TEXT_ENTER, self.sendMessage)
		self.outputBox.Bind(wx.EVT_CHAR, self.verifyKey)
		Thread(target=self.connect, daemon=True).start()
		self.Show()

	def verifyKey(self, event):
		key=event.GetUnicodeKey()
		if not key==wx.WXK_NONE and key>31:
			char=chr(key)
			self.inputBox.SetFocus()
			self.inputBox.Clear()
			self.inputBox.WriteText(char)
		else:
			event.Skip()
	def connect(self):
		try:
			self.telnet=Telnet(self.host, self.port)
			while True:
				message=self.telnet.read_very_eager()
				if message:
					wx.CallAfter(self.parseMessage, message)
				sleep(0.005)
		except Exception as e:
			wx.MessageBox(f"Erro: {e}", "erro", wx.ICON_ERROR)

	def parseMessage(self, message):
		message=message.decode("iso-8859-1")
		lines=message.split("\n")
		for line in lines:
			line=line.strip()
			if not line=="":
				if line.lower().startswith("!!sound"):
					parsedLine=re.search(self.soundStyle, line)
					params=parsedLine.group(1).split(" ")
					file=params[0]
					try:
						volume=int(params[1].split("=")[1])
						volume=self.normalizeVolume(volume)
					except:
						volume=1.0
					self.playSound(file, volume)
				elif line.lower().startswith("!!music"):
					parsedLine=re.search(self.soundStyle, line)
					params=parsedLine.group(1).split(" ")
					file=params[0]
					try:
						volume=int(params[1].split("=")[1])
						volume=self.normalizeVolume(volume)
					except:
						volume=1.0
					self.playSound(file, volume, True)
				else:
					speak(line)
					if self.outputBox.HasFocus():
						position=self.outputBox.GetInsertionPoint()
						self.outputBox.AppendText(line+"\r\n")
						self.outputBox.SetInsertionPoint(position)
					else:
						self.outputBox.AppendText(line+"\r\n")

	def normalizeVolume(self, volume):
		if volume<=0:
			return 0.0
		elif volume>=100:
			return 1.0

		return round(math.pow(10, (volume-100)/60), 4)

	def sendMessage(self, event):
		message=self.inputBox.GetValue()+"\n"
		message=message.encode("iso-8859-1")
		self.telnet.write(message)
		self.inputBox.Clear()

	def playSound(self, file, volume=1.0, music=False):
		self.streams=[stream for stream in self.streams if stream.is_playing]
		file="sounds/"+file
		if music:
			if file=="sounds/off":
				if hasattr(self, "musicStream") and self.musicStream.is_playing:
					self.musicStream.stop()
				return
			if not file.endswith(".mp3"):
				file=file+".mp3"
			if hasattr(self, "musicStream") and self.musicStream.is_playing and self.musicStream.file==file:
				return
			try:
				self.musicStream=stream.FileStream(file=file)
				self.musicStream.volume=volume
				self.musicStream.play()
			except:
				wx.MessageBox(f"Erro ao reproduzir a música {file}.", "erro", wx.ICON_ERROR)
		else:
			if file=="sounds/off":
				if hasattr(self, "musicStream") and self.musicStream.is_playing:
					self.musicStream.stop()
					return
			if not file.endswith(".wav"):
				file=file+".wav"
			try:
				newStream=stream.FileStream(file=file)
				newStream.volume=volume
				newStream.play()
				self.streams.append(newStream)
			except:
				return

if __name__=="__main__":
	app=wx.App(False)
	speak=outputs.auto.Auto().speak
	program=Program(None, title="Mud Client")
	app.MainLoop()
