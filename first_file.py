import wx

app = wx.App(False)
wx.SystemOptions.SetOption("msw.remap", "0")

frame = wx.Frame(None, title="Modern wxPython", size=(800, 600))
frame.SetBackgroundColour(wx.Colour("#fafaf8"))

panel = wx.Panel(frame)
panel.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL,
                     wx.FONTWEIGHT_NORMAL, faceName="Inter"))

btn = wx.Button(panel, label="Click Me", pos=(20,20), size=(140,40))
btn.SetBackgroundColour(wx.Colour("#0d6efd"))
btn.SetForegroundColour(wx.WHITE)
btn.SetFont(wx.Font(11, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))

frame.Show()
app.MainLoop()
