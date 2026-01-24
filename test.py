import wx
import oracledb
import wx.lib.agw.aui as aui
import os

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

        self.CreateMenu()
        self.CreateTools()



          #UNDER CONSTRUCTION

        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)

        self.left_panel = wx.Panel(self.splitter, style=wx.BORDER_RAISED)
        left_sizer = wx.BoxSizer(wx.VERTICAL)

        #header = wx.StaticText(self.left_panel, label="Balance Sheet", style = wx.ALIGN_LEFT)
        #header.SetFont(wx.Font(8, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
        #left_sizer.Add(header, 0, wx.ALL | wx.EXPAND, 10)
        self.left_panel.SetSizer(left_sizer)
        self.left_panel.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.right_panel = wx.Panel(self.splitter, style=wx.BORDER_RAISED)
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        right_sizer.Add(wx.StaticText(self.right_panel, label = "Right Panel"), 0, wx.ALL, 15)
        self.right_panel.SetSizer(right_sizer)
        self.right_panel.SetBackgroundColour("f5f5f5")

        self.splitter.SplitVertically(self.left_panel, self.right_panel)
        self.splitter.SetSashPosition(250, True)
        self.splitter.SetMinimumPaneSize(200)

        #adding splitter to main sizer
        self.main_sizer.Add(self.splitter, 1, wx.EXPAND)
        self.SetSizer(self.main_sizer)
        self.SetMinSize((800, 500))

        #creating tree control
        self.tree = wx.TreeCtrl(self.left_panel, style=wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_LINES_AT_ROOT)
        root = self.tree.AddRoot("Hidden Root")

        #adding independent main items
        balance_sheet = self.tree.AppendItem(root, "Balance Sheet")
        profit_loss = self.tree.AppendItem(root, "Profit and Loss")

        assets = self.tree.AppendItem(balance_sheet, "Assets")
        self.tree.AppendItem(assets, "Cash and cash equivalents")
        self.tree.AppendItem(assets, "Due from banks")
        self.tree.AppendItem(assets, "Securities")
        self.tree.AppendItem(assets, "Loans to customers")
        self.tree.AppendItem(assets, "Property, plant and equipment")
        self.tree.AppendItem(assets, "Other assets")

        liabilities = self.tree.AppendItem(balance_sheet, "Liabilities")
        self.tree.AppendItem(liabilities, "Due to banks")
        self.tree.AppendItem(liabilities, "Due to customers")

        equity = self.tree.AppendItem(balance_sheet, "Equity")
        self.tree.AppendItem(equity, "Share capital")
        self.tree.AppendItem(equity, "Capital surplus")

        income = self.tree.AppendItem(profit_loss, "Income")
        self.tree.AppendItem(income, "Interest income")
        self.tree.AppendItem(income, "Fee income")
        self.tree.AppendItem(income, "Commission income")

        expense = self.tree.AppendItem(profit_loss, "Expense")
        self.tree.AppendItem(expense, "Interest expense")


        #expanding main categories by default
        self.tree.ExpandAll()
        #self.tree.Expand(assets)
        #self.tree.Expand(liabilities)

        left_sizer.Add(self.tree, 1, wx.EXPAND | wx.ALL, 0)

        self.Centre()
        self.Show()


    def CreateMenu(self):

        menubar = wx.MenuBar()

        # --- File Menu ---
        file_menu = wx.Menu()
        file_menu.Append(wx.ID_NEW, "&New\tCtrl+N", "Create a new file")
        file_menu.Append(wx.ID_OPEN, "&Open\tCtrl+O", "Open an existing file")
        file_menu.AppendSeparator()
        exit_item = file_menu.Append(wx.ID_EXIT, "E&xit\tAlt+F4", "Exit the application")

        menubar.Append(file_menu, "&File")

        # --- Edit Menu ---
        edit_menu = wx.Menu()
        edit_menu.Append(wx.ID_EDIT, "&Edit\tCtrl+E", "Edit a report")

        menubar.Append(edit_menu, "&Edit")

        # --- View Menu ---
        view_menu = wx.Menu()
        view_menu.Append(wx.ID_VIEW_DETAILS, "&View\tCtrl+V", "View details")

        menubar.Append(view_menu, "&View")

        # --- Navigate Menu ---
        navigate_menu = wx.Menu()
        navigate_menu.Append(wx.ID_NEW, "&Accounting\tCtrl+A", "Accounting")
        navigate_menu.Append(wx.ID_NEW, "&Reports\tCtrl+R", "Reports")

        menubar.Append(navigate_menu, "&Navigate")

        # --- Tools Menu ---
        tools_menu = wx.Menu()
        tools_menu.Append(wx.ID_VIEW_DETAILS, "&Tools\tCtrl+T", "Tools")

        menubar.Append(tools_menu, "&Tools")

        # --- Window Menu ---
        window_menu = wx.Menu()
        window_menu.Append(wx.ID_VIEW_DETAILS, "&Window\tCtrl+W", "Window")

        menubar.Append(window_menu, "&Window")

        # --- Help Menu ---
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, "&About", "Show about dialog")

        menubar.Append(help_menu, "&Help")

        # Attach the menu bar to the frame
        self.SetMenuBar(menubar)

    def CreateTools(self):

        #creating toolbar
        toolbar = self.CreateToolBar(wx.TB_HORIZONTAL | wx.TB_FLAT | wx.NO_BORDER)
        accounting = toolbar.AddTool(wx.ID_ANY, 'Accounting', load_icon('1.png'), 'Accounting')
        reporting = toolbar.AddTool(wx.ID_ANY, 'Reporting', load_icon('2.png'), 'Reporting')
        excel = toolbar.AddTool(wx.ID_ANY, 'Excel', load_icon('3.png'), 'Excel')
        open = toolbar.AddTool(wx.ID_ANY, 'Open', load_icon('4.png'), 'Open')
        upload = toolbar.AddTool(wx.ID_ANY, 'Upload', load_icon('5.png'), 'Upload')
        database = toolbar.AddTool(wx.ID_ANY, 'Database', load_icon('6.png'), 'Database')
        toolbar.Realize()


def start_app():
    app = wx.App(False)

    frame = MainFrame()

    dlg = OracleConnectionDialog(frame)
    dlg.ShowModal()
    dlg.Destroy()

    app.MainLoop()


def load_icon(filename):
    path = os.path.join('icons', filename)
    bmp = wx.Bitmap(path)
    if not bmp.IsOk():
        print(f'Warning: Could not load icon: {path}')

    return bmp


if __name__ == "__main__":
    start_app()
