import wx
import wx.adv

class AccessibleFrame(wx.Accessible):
	def GetRole(self, childId):
		return (wx.ACC_OK, wx.ROLE_SYSTEM_WINDOW)

class AccessibleMenuButton(wx.Accessible):
	def GetRole(self, childId):
		return wx.ACC_OK, wx.ROLE_SYSTEM_BUTTONMENU

class CommandLinkButton(wx.adv.CommandLinkButton):
	def __init__(self, parent, label="", note="", isMenu=False):
		super().__init__(parent=parent, note=note, mainLabel=label)
		if isMenu==True:
			self.SetAccessible(AccessibleMenuButton())

class AccessibleEsc(wx.Accessible):
	def GetKeyboardShortcut(self, childId):
		return (wx.ACC_OK, "Esc")

class AccessibleExit(wx.Accessible):
	def GetKeyboardShortcut(self, childId):
		return (wx.ACC_OK, "Alt+f4")
