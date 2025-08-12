import wx
from telnetlib import Telnet
from threading import Thread
from sound_lib import stream, output
from accessible_output2 import outputs
import sys
import re
import os
from time import sleep
import math
import textwrap
import accessibility as ACC
from savedata import savedata
import error_handler

class Program(wx.Frame):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.output=output.Output()
		self.soundStyle=r"\((.*?)\)"
		self.streams=[]
		self.history=[]
		self.historyIndex=0
		self.host=wx.GetTextFromUser("Digite o endereço do MUD", "client", "mud.fantasticmud.com")
		try:
			self.port=int(wx.GetTextFromUser("Digite a porta do mud", "Client", "4000"))
		except:
			wx.MessageBox("Porta inválida", "Erro", wx.ICON_ERROR)
			sys.exit()
		self.initUI()

	def initUI(self):
		panel=wx.Panel(self)
		mainSizer=wx.BoxSizer(wx.VERTICAL)
		labelInputBox=wx.StaticText(panel, label="&Entrada")
		self.inputBox=wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.TE_DONTWRAP|wx.TE_PROCESS_ENTER)
		box1=wx.BoxSizer(wx.HORIZONTAL)
		box1.Add(labelInputBox, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
		box1.Add(self.inputBox, 1, wx.EXPAND)
		labelOutputBox=wx.StaticText(panel, label="&Saída")
		self.outputBox=wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP)
		box2=wx.BoxSizer(wx.HORIZONTAL)
		box2.Add(labelOutputBox, 0, wx.ALIGN_CENTER_VERTICAL|wx.RIGHT, 5)
		box2.Add(self.outputBox, 1, wx.EXPAND)
		mainSizer.Add(box1, 1, wx.ALL|wx.EXPAND, 5)
		mainSizer.Add(box2, 1, wx.ALL|wx.EXPAND, 5)
		panel.SetSizer(mainSizer)
		self.Fit()
		self.inputBox.Bind(wx.EVT_TEXT_ENTER, self.sendMessage)
		self.inputBox.Bind(wx.EVT_KEY_DOWN, self.verifyInputBoxKeys)
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

	def verifyInputBoxKeys(self, event):
		keymod=event.GetModifiers()
		code=event.GetKeyCode()
		shiftDown=keymod and wx.MOD_SHIFT
		ctrlDown=keymod and wx.MOD_CONTROL
		altDown=keymod and wx.MOD_ALT
		if code==wx.WXK_UP:
			if self.historyIndex>0:
				self.historyIndex-=1
				self.inputBox.Clear()
				self.inputBox.WriteText(self.history[self.historyIndex])
				self.inputBox.SetSelection(-1, -1)
		elif code==wx.WXK_DOWN:
			if self.historyIndex<len(self.history)-1:
				self.historyIndex+=1
				self.inputBox.Clear()
				self.inputBox.WriteText(self.history[self.historyIndex])
				self.inputBox.SetSelection(-1, -1)
			else:
				self.inputBox.Clear()
				self.historyIndex=len(self.history)
		elif shiftDown and code==wx.WXK_RETURN:
			self.sendMessage(addToHistory=False)
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
		lines=[wrappedLine for line in lines for wrappedLine in textwrap.wrap(line, width=256, break_long_words=False)]
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

	def sendMessage(self, event=None, addToHistory=True):
		entireMessage=self.inputBox.GetValue()
		messages=entireMessage.split(";")
		for message in messages:
			if addToHistory and self.historyIndex==len(self.history):
				self.history.append(message)
			self.historyIndex=len(self.history)
			message=message+"\n"
			message=message.encode("iso-8859-1")
			self.telnet.write(message)
		if addToHistory:
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
