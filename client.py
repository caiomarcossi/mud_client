import wx
from telnetlib import Telnet
import threading
from threading import Thread
from sound_lib import stream, output
from accessible_output2 import outputs
import sys
import re

class Program(wx.Frame):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.output=output.Output()
		self.soundStyle=r"\((.*?)\)"
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
		Thread(target=self.connect, daemon=True).start()
		self.Show()

	def connect(self):
		try:
			self.telnet=Telnet(self.host, self.port)
			self.outputBox.AppendText("Conectado")
			while True:
				message=self.telnet.read_very_eager()
				wx.CallAfter(self.parseMessage, message)
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
					volume=100
					volume=int(params[1].split("=")[1])
					self.playSound(file)
				else:
					speak(line)
					position=self.outputBox.GetInsertionPoint()
					self.outputBox.AppendText("\r\n"+line)
					self.outputBox.SetInsertionPoint(position)

	def sendMessage(self, event):
		message=self.inputBox.GetValue()+"\n"
		message=message.encode("iso-8859-1")
		self.telnet.write(message)
		self.inputBox.Clear()

	def playSound(self, file):
		if not file=="off":
			self.stream=stream.FileStream(file="sounds/"+file)
			self.stream.play()
		else:
			self.stream.stop()

if __name__=="__main__":
	app=wx.App(False)
	speak=outputs.auto.Auto().speak
	program=Program(None, title="Mud Client")
	app.MainLoop()
