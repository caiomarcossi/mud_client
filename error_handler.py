import sys
import wx
import threading
from traceback import format_exception

def trataExceptPrograma(type, description, traceback):
	tipoErro=type
	erroDesc=description
	erroTraceback=traceback
	erroFormatado=format_exception(tipoErro, erroDesc, erroTraceback)
	dialog=wx.Dialog(None, title="erro do programa")
	textoErro=wx.TextCtrl(dialog, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP, value="")
	for linha in erroFormatado:
		textoErro.AppendText(linha)
	dialog.ShowModal()
sys.excepthook=trataExceptPrograma
def trataExceptThread(info):
	nomeErro=info.exc_type.__name__
	descErro=info.exc_value
	tb=info.exc_traceback
	erro=format_exception(nomeErro, descErro, tb)
	dialogErro=wx.Dialog(None, title="erro do programa em uma Thread")
	mostraErro=wx.TextCtrl(dialogErro, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP, value="")
	for linhaErro in erro:
		mostraErro.AppendText(linhaErro)
	dialogErro.ShowModal()
	sys.exit()
threading.excepthook=trataExceptThread
