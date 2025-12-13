import wx

#creating mainframe using class
class MainFrame(wx.Frame):
    def __init__(self, parent=None, title="Financial Reporter"):
        super(MainFrame, self).__init__(parent, title=title, size=(1000, 700))

        self.Center()
        self.Show(True)

if __name__ == "__main__":
    app = wx.App(False)

    frame = MainFrame()

    app.MainLoop()
