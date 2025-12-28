import wx
import oracledb

#oracledb.init_oracle_client(lib_dir=r"C:\\")

#oracle connection dialog window
class OracleConnectionDialog(wx.Dialog):
    def __init__(self, parent=None):
        super().__init__(parent, title="Oracle Database Connection Tester (Thick Mode)", size=(450, 420))

        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Username
        main_sizer.Add(wx.StaticText(panel, label="Username:"), flag=wx.LEFT | wx.TOP | wx.RIGHT, border=10)
        self.txt_user = wx.TextCtrl(panel)
        self.txt_user.SetValue('gerov_evgeniy[LAB_BUH]')
        main_sizer.Add(self.txt_user, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        # Password
        main_sizer.Add(wx.StaticText(panel, label="Password:"), flag=wx.LEFT | wx.TOP | wx.RIGHT, border=10)
        self.txt_pass = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        main_sizer.Add(self.txt_pass, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        # Host
        main_sizer.Add(wx.StaticText(panel, label="Host:"), flag=wx.LEFT | wx.TOP | wx.RIGHT, border=10)
        self.txt_host = wx.TextCtrl(panel)
        self.txt_host.SetValue("udwh.base.roscap.com")
        main_sizer.Add(self.txt_host, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        # Port
        main_sizer.Add(wx.StaticText(panel, label="Port:"), flag=wx.LEFT | wx.TOP | wx.RIGHT, border=10)
        self.txt_port = wx.TextCtrl(panel)
        self.txt_port.SetValue("1521")
        main_sizer.Add(self.txt_port, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        # Service Name
        main_sizer.Add(wx.StaticText(panel, label="Service Name:"), flag=wx.LEFT | wx.TOP | wx.RIGHT, border=10)
        self.txt_service = wx.TextCtrl(panel)
        self.txt_service.SetValue("udwh")
        main_sizer.Add(self.txt_service, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btn_test = wx.Button(panel, label="Test Connection")
        self.btn_test.Bind(wx.EVT_BUTTON, self.on_test_connection)
        btn_sizer.Add(self.btn_test, flag=wx.RIGHT, border=10)

        btn_close = wx.Button(panel, label="Close")
        btn_close.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_CANCEL))
        btn_sizer.Add(btn_close)

        main_sizer.Add(btn_sizer, flag=wx.ALIGN_CENTER | wx.ALL, border=20)

        # Status area
        self.status_text = wx.StaticText(panel, label="Thick mode enabled (using Oracle Client libraries)", style=wx.ALIGN_CENTER)
        self.status_text.SetForegroundColour((0, 100, 200))  # Blue-ish for info
        main_sizer.Add(self.status_text, flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        panel.SetSizer(main_sizer)
        self.Layout()
        self.Centre()

    def on_test_connection(self, event):
        user = self.txt_user.GetValue().strip()
        password = self.txt_pass.GetValue()
        host = self.txt_host.GetValue().strip()
        port = self.txt_port.GetValue().strip()
        service = self.txt_service.GetValue().strip()

        if not all([user, password, host, port, service]):
            self.status_text.SetLabel("Please fill in all fields.")
            self.status_text.SetForegroundColour(wx.RED)
            self.Layout()
            return

        # Disable button during test
        self.btn_test.Enable(False)
        wx.Yield()  # Update UI

        dsn = f"{host}:{port}/{service}"

        try:
            # Connection now uses Thick mode
            with oracledb.connect(user=user, password=password, dsn=dsn) as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT SYSDATE FROM DUAL")
                    result = cursor.fetchone()
            self.status_text.SetLabel(f"Success! Database time: {result[0]} (Thick mode)")
            self.status_text.SetForegroundColour((0, 128, 0))  # Dark green
        except oracledb.DatabaseError as e:
            error, = e.args
            self.status_text.SetLabel(f"Connection failed: {error.message}")
            self.status_text.SetForegroundColour(wx.RED)
        finally:
            self.btn_test.Enable(True)
            self.Layout()

#creating main window
class MainFrame(wx.Frame):
    def __init__(self, parent=None, title="Financial Reporter"):
        super(MainFrame, self).__init__(parent, title=title, size=(1000, 700))

        self.Center()
        self.Show(True)

        menubar = wx.MenuBar()

        # --- File Menu ---
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_NEW, "&New\tCtrl+N", "Create a new file")
        file_menu.Append(wx.ID_OPEN, "&Open\tCtrl+O", "Open an existing file")
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT, "E&xit\tAlt+F4", "Exit the application")

        menubar.Append(file_menu, "&File")

        # --- Help Menu ---
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, "&About", "Show about dialog")

        menubar.Append(help_menu, "&Help")

        # Attach the menu bar to the frame
        self.SetMenuBar(menubar)

def start_app():
    app = wx.App(False)

    frame = MainFrame()

    dlg = OracleConnectionDialog(frame)
    dlg.ShowModal()
    dlg.Destroy()

    app.MainLoop()

if __name__ == "__main__":
    start_app()
