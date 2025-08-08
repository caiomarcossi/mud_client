import wx
from telnetlib import Telnet
import threading
from threading import Thread
from sound_lib import stream, output
from accessible_output2 import outputs
import sys

class Program(wx.Frame):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
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
			while True:
				message=self.telnet.read_very_eager()
				wx.CallAfter(self.parseMessage, message)
		except Exception as e:
			wx.MessageBox(f"Erro: {e}", "erro", wx.ICON_ERROR)

	def parseMessage(self, message):
		message=message.decode("iso-8859-1")
		message=message.strip()
		if not message=="":
			speak(message)
			self.outputBox.AppendText(message)

	def sendMessage(self, event):
		message=self.inputBox.GetValue()+"\n"
		message=message.encode("iso-8859-1")
		self.telnet.write(message)
		self.inputBox.Clear()

if __name__=="__main__":
	app=wx.App(False)
	speak=outputs.auto.Auto().speak
	program=Program(None, title="Mud Client")
	app.MainLoop()
