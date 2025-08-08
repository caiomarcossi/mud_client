import wx
import telnetlib3
import threading
from threading import Thread
import asyncio
from sound_lib import stream, output
from accessible_output2 import outputs
import sys

class Program(wx.Frame):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.reader=None
		self.writer=None
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
		Thread(target=self.startConnection, daemon=True).start()
		self.Show()

	def startConnection(self):
		asyncio.run(self.connect())

	async def connect(self):
		try:
			self.reader, self.writer=await telnetlib3.open_connection(host=self.host, port=self.port, encoding=None)
			buffer=b""
			while True:
				message=await self.reader.read(1024)
				buffer+=message
				while b"\n" in buffer:
					line, buffer=buffer.split(b"\n", 1)
					text=line.decode("iso-8859-1")+"\n"
					wx.CallAfter(self.parseMessage, text)
				if buffer:
					text=buffer.decode("iso-8859-1")
					wx.CallAfter(self.parseMessage, text)
					buffer=b""

		except Exception as e:
			wx.MessageBox(f"Erro: {e}", "erro", wx.ICON_ERROR)

	def parseMessage(self, message):
		if not message=="":
			speak(message)
			self.outputBox.AppendText(message)

	def sendMessage(self, event):
		message=self.inputBox.GetValue()+"\n"
		message=message.encode("iso-8859-1")
		self.writer.write(message)
		self.inputBox.Clear()

if __name__=="__main__":
	app=wx.App(False)
	speak=outputs.auto.Auto().speak
	program=Program(None, title="Mud Client")
	app.MainLoop()
