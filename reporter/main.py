import wx
import oracledb
import wx.lib.agw.aui as aui
import wx.adv
import wx.grid
import os
import pyodbc
from datetime import date

#Oracle connection dialogue window
class OracleConnectDialog(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Oracle Database Login", size=(300, 200))

        panel = wx.Panel(self)
        main_sizer = wx.BoxSizer(wx.VERTICAL)

        # Username
        main_sizer.Add(wx.StaticText(panel, label="Username:"), flag=wx.LEFT | wx.TOP | wx.RIGHT, border=10)
        self.txt_user = wx.TextCtrl(panel)
        main_sizer.Add(self.txt_user, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        # Password
        main_sizer.Add(wx.StaticText(panel, label="Password:"), flag=wx.LEFT | wx.TOP | wx.RIGHT, border=10)
        self.txt_pass = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        main_sizer.Add(self.txt_pass, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=10)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.btn_cnct = wx.Button(panel, label='Connect', id=wx.ID_OK)
        btn_sizer.Add(self.btn_cnct, flag=wx.RIGHT, border=10)

        btn_close = wx.Button(panel, label="Close")
        btn_close.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_CANCEL))
        btn_sizer.Add(btn_close)

        main_sizer.Add(btn_sizer, flag=wx.ALIGN_CENTER | wx.ALL, border=20)

        panel.SetSizer(main_sizer)
        self.Layout()
        self.Centre()

    def GetConnectionParameters(self):
        return {
            "user": self.txt_user.GetValue().strip(),
            "password": self.txt_pass.GetValue().strip(),
        }

#creating main window
class MainFrame(wx.Frame):
    def __init__(self, parent=None, title="Financial Reporter"):
        super(MainFrame, self).__init__(parent, title=title, size=(1000, 700))

        self.CreateMenu()
        self.CreateTools()
        self.CreateLayout()
        self.CreateStatusBar()
        self.SetStatusText("Not connected to Oracle Database")

        #initially only connect option enabled
        self.mnu_disconnect.Enable(False)
        self.mnu_disconnect2.Enable(False)
        self.oracle_connection = None
        self.oracle_cursor = None
        self.conn = None
        self.cursor = None

        #defining default view
        self.current_view = 'Accounting'
        self.UpdateView()
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
        self.mnu_accounting = navigate_menu.Append(wx.ID_ANY, "&Accounting\tCtrl+A", "Accounting")
        self.mnu_reports = navigate_menu.Append(wx.ID_ANY, "&Reports\tCtrl+R", "Reports")
        self.mnu_views = navigate_menu.Append(wx.ID_ANY, "&Views\tCtrl+T", "Views")

        menubar.Append(navigate_menu, "&Navigate")

        # --- Tools Menu ---
        tools_menu = wx.Menu()
        tools_menu.Append(wx.ID_VIEW_DETAILS, "&Tools\tCtrl+T", "Tools")

        menubar.Append(tools_menu, "&Tools")

        # --- Window Menu ---
        window_menu = wx.Menu()
        window_menu.Append(wx.ID_VIEW_DETAILS, "&Window\tCtrl+W", "Window")

        menubar.Append(window_menu, "&Window")

        #--- Oracle ---
        oracle = wx.Menu()
        self.mnu_connect = oracle.Append(wx.ID_ANY, 'Connect')
        self.mnu_disconnect = oracle.Append(wx.ID_ANY, 'Disconnect')

        menubar.Append(oracle, '&Oracle')

        #--- MS SQL Server ---
        ms_sql_server = wx.Menu()
        self.mnu_connect2 = ms_sql_server.Append(wx.ID_ANY, 'Connect')
        self.mnu_disconnect2 = ms_sql_server.Append(wx.ID_ANY, 'Disconnect')

        menubar.Append(ms_sql_server, "&SQL Server")

        # --- Help Menu ---
        help_menu = wx.Menu()
        about_item = help_menu.Append(wx.ID_ABOUT, "&About", "Show about dialog")

        menubar.Append(help_menu, "&Help")

        # Attach the menu bar to the frame
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.OnSwitchAccounting, self.mnu_accounting)
        self.Bind(wx.EVT_MENU, self.OnSwitchReports, self.mnu_reports)
        self.Bind(wx.EVT_MENU, self.OnSwitchViews, self.mnu_views)
        self.Bind(wx.EVT_MENU, self.OnConnectToOracle, self.mnu_connect)
        self.Bind(wx.EVT_MENU, self.ConnectWindowsAuth, self.mnu_connect2)
        self.Bind(wx.EVT_MENU, self.OnOracleDisconnect, self.mnu_disconnect)
        self.Bind(wx.EVT_MENU, self.OnDisconnect, self.mnu_disconnect2)

    def CreateTools(self):

        #creating toolbar
        toolbar = self.CreateToolBar(wx.TB_HORIZONTAL | wx.TB_FLAT | wx.NO_BORDER)
        accounting = toolbar.AddTool(wx.ID_ANY, 'Accounting', load_icon('1.png'), 'Accounting')
        reporting = toolbar.AddTool(wx.ID_ANY, 'Reporting', load_icon('2.png'), 'Reporting')
        excel = toolbar.AddTool(wx.ID_ANY, 'Excel', load_icon('3.png'), 'Export to Excel')
        open = toolbar.AddTool(wx.ID_ANY, 'Open', load_icon('4.png'), 'Open')
        upload = toolbar.AddTool(wx.ID_ANY, 'Upload', load_icon('5.png'), 'Upload')
        create_report = toolbar.AddTool(wx.ID_EXECUTE, 'Create report', load_icon('6.png'), 'Create report')
        database = toolbar.AddTool(wx.ID_ANY, 'Database', load_icon('7.png'), 'Database')
        toolbar.AddSeparator()

        date = wx.StaticText(toolbar, label='Report date: ')
        date.SetFont(wx.Font(date.GetFont()).MakeBold())
        toolbar.AddControl(date)

        #creating date picker
        self.date_ctrl = wx.adv.DatePickerCtrl(toolbar, style=wx.adv.DP_DEFAULT | wx.adv.DP_SHOWCENTURY | wx.BORDER_NONE)
        self.date_ctrl.SetValue(wx.DateTime.Today())
        toolbar.AddControl(self.date_ctrl)

        #self.Bind(wx.adv.EVT_DATE_CHANGED, self.OnDateChanged, self.date_ctrl)
        self.Bind(wx.EVT_TOOL, self.OnCreateReport, id = wx.ID_EXECUTE)

        toolbar.Realize()

    def OnSwitchAccounting(self, event):
        self.current_view = 'Accounting'
        self.UpdateView()

    def OnSwitchReports(self, event):
        self.current_view = 'Reports'
        self.UpdateView()

    def OnSwitchViews(self, event):
        self.current_view = 'Views'
        self.UpdateView()

    def OnConnectToOracle(self, event):
        dlg = OracleConnectDialog(self)

        print('opening oracle connect dialogue')

        if dlg.ShowModal() == wx.ID_OK:
            params = dlg.GetConnectionParameters()

            user = params['user']
            password = params['password']
            host = 'udwh.base.roscap.com'
            port = '1521'
            service = 'udwh'

            if not user or not password:
                wx.MessageBox(f"Please fill in all fields", "Login parameters required", wx.OK | wx.ICON_INFORMATION)
                return

            dsn = f"{host}:{port}/{service}"

            try:
                self.oracle_connection = oracledb.connect(user=user, password=password, dsn=dsn)
                self.oracle_cursor = self.oracle_connection.cursor()
                wx.MessageBox(f"Successfully connected to Oracle Database", 'Connected', wx.OK | wx.ICON_INFORMATION)

                self.SetStatusText(f"Connected to {host}")
                self.mnu_connect.Enable(False)
                self.mnu_disconnect.Enable(True)

            except oracledb.DatabaseError as e:
                error, = e.args
                error_msg = f"Connection failed!\n\n{str(e)}"
                self.SetStatusText("Connection failed")
                wx.MessageBox(error_msg, "Connection Error", wx.OK | wx.ICON_ERROR)

        dlg.Destroy()

    def __del__(self):
        if self.oracle_cursor:
            self.oracle_cursor.close()

        if self.oracle_connection:
            self.oracle_connection.close()

    def ConnectWindowsAuth(self, event):

        if self.conn is not None:
            wx.MessageBox("Already connected to SQL Server", 'Info', wx.OK | wx.ICON_INFORMATION)
            return

        SERVER_NAME = 'DESKTOP-0N58KU8'
        DATABASE_NAME = 'master'

        conn_str = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={SERVER_NAME};"
            f"DATABASE={DATABASE_NAME};"
            f"Trusted_Connection=yes;"
        )

        try:
            self.conn = pyodbc.connect(conn_str, timeout=8)
            self.cursor = self.conn.cursor()

            self.SetStatusText(f"Connected to {SERVER_NAME} {DATABASE_NAME}")
            self.mnu_connect2.Enable(False)
            self.mnu_disconnect2.Enable(True)

            wx.MessageBox(
                f"Successfully connected to SQL Server",
                'Connected',
                wx.OK | wx.ICON_INFORMATION
            )

        except pyodbc.Error as ex:
            error_msg = f"Connection failed!\n\n{str(ex)}"
            self.SetStatusText("Connection failed")
            wx.MessageBox(error_msg, "Connection Error", wx.OK | wx.ICON_ERROR)

    def __del__(self):
        if self.cursor:
            self.cursor.close()

        if self.conn:
            self.conn.close()

    def OnDisconnect(self, event):

        if self.conn is None:
            wx.MessageBox("Not connected", 'Info', wx.OK | wx.ICON_INFORMATION)
            return

        try:
            if self.cursor:
                self.cursor.close()
                self.conn.close()

            self.conn = None
            self.cursor = None

            self.SetStatusText("Disconnected from SQL Server")
            self.mnu_connect2.Enable(True)
            self.mnu_disconnect2.Enable(False)

            wx.MessageBox("Disconnected successfully", 'Info', wx.OK | wx.ICON_INFORMATION)

        except Exception as ex:
            wx.MessageBox(f"Error during disconnect:\n{str(ex)}", "Warning", wx.OK | wx.ICON_WARNING)

    def OnOracleDisconnect(self, event):

        if self.oracle_connection is None:
            wx.MessageBox("Not connected", 'Info', wx.OK | wx.ICON_INFORMATION)
            return

        try:
            if self.oracle_cursor:
                self.oracle_cursor.close()
                self.oracle_connection.close()

            self.oracle_connection = None
            self.oracle_cursor = None

            self.SetStatusText("Disconnected from Oracle Database")
            self.mnu_connect.Enable(True)
            self.mnu_disconnect.Enable(False)

            wx.MessageBox("Disconnected successfully", 'Info', wx.OK | wx.ICON_INFORMATION)

        except Exception as ex:
            wx.MessageBox(f"Error during disconnect:\n{str(ex)}", 'Warning', wx.OK | wx.ICON_INFORMATION)

    def CreateLayout(self):

        self.main_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.main_sizer)
        self.SetMinSize((800, 500))
        self.splitter = wx.SplitterWindow(self, style=wx.SP_LIVE_UPDATE)
        self.main_sizer.Add(self.splitter, 1, wx.EXPAND)

        #creating left panel
        self.left_panel = wx.Panel(self.splitter, style=wx.BORDER_RAISED)
        self.left_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        left_sizer = wx.BoxSizer(wx.VERTICAL)
        self.left_panel.SetSizer(left_sizer)

        #adding tree control to left panel
        self.tree = wx.TreeCtrl(self.left_panel, style=wx.TR_HIDE_ROOT | wx.TR_HAS_BUTTONS | wx.TR_LINES_AT_ROOT)
        self.tree_root = self.tree.AddRoot('Hidden Root')
        left_sizer.Add(self.tree, 1, wx.EXPAND | wx.ALL, 0)

        self.tree.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnTreeSelChanged)

        #creating right panel
        self.right_panel = wx.Panel(self.splitter, style=wx.BORDER_RAISED)
        self.right_panel.SetBackgroundColour("f5f5f5")
        right_sizer = wx.BoxSizer(wx.VERTICAL)
        self.right_panel.SetSizer(right_sizer)

        self.splitter.SplitVertically(self.left_panel, self.right_panel)
        self.splitter.SetSashPosition(250, True)
        self.splitter.SetMinimumPaneSize(250)

        self.central_panel = wx.Panel(self.right_panel, style=wx.BORDER_RAISED)
        self.central_panel.SetBackgroundColour("f5f5f5") #change to "f5f5f5"
        self.dispay_panel = wx.Panel(self.right_panel, style=wx.BORDER_NONE)
        self.dispay_panel.SetBackgroundColour(wx.Colour(255, 255, 255))
        central_sizer = wx.BoxSizer(wx.VERTICAL)
        central_sizer.Add(self.central_panel, 4, wx.EXPAND | wx.ALL, 2)
        central_sizer.Add(self.dispay_panel, 6, wx.EXPAND, wx.ALL, 0)

        self.right_panel.SetSizer(central_sizer) #set central_sizer to right_panel NOT to central_panel

        self.display_grid = wx.grid.Grid(self.dispay_panel, -1)
        self.display_grid.CreateGrid(500, 100)
        self.display_grid.SetDefaultRowSize(5)
        self.display_grid.EnableEditing(False)
        self.display_grid.EnableGridLines(True)
        self.display_grid.EnableDragColSize(True)
        self.display_grid.SetRowLabelSize(0)
        self.display_grid.SetColLabelSize(20)
        display_sizer = wx.BoxSizer(wx.VERTICAL)
        display_sizer.Add(self.display_grid, wx.ID_ANY, wx.EXPAND | wx.ALL, 0)

        self.dispay_panel.SetSizer(display_sizer)

    def ClearTree(self):
        self.tree.DeleteChildren(self.tree_root)

    def UpdateView(self):
        self.ClearTree()

        if self.current_view == 'Accounting':
            #populating accounting tree view
            balance_sheet = self.tree.AppendItem(self.tree_root, "Balance Sheet")
            profit_loss = self.tree.AppendItem(self.tree_root, "Profit and Loss")

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

            self.tree.ExpandAll()

        elif self.current_view == 'Reports':
            liquidity = self.tree.AppendItem(self.tree_root, 'Liquidity ratios')
            cbr = self.tree.AppendItem(self.tree_root, 'Central Bank')

            lcr = self.tree.AppendItem(liquidity, 'Liquidity Coverage Ratio')
            nsfr = self.tree.AppendItem(liquidity, 'Net Stable Funding Ratio')
            self.tree.AppendItem(cbr, 'Weighted average rates')

            self.tree.ExpandAll()
            self.tree.SelectItem(lcr)

        elif self.current_view == 'Views':
            #populating view tree
            accounting = self.tree.AppendItem(self.tree_root, 'Accounting')
            sib = self.tree.AppendItem(self.tree_root, 'SIB')

            self.tree.AppendItem(accounting, 'Con_saldo')
            self.tree.AppendItem(accounting, 'Clients')
            self.tree.AppendItem(accounting, 'Contracts')

            lcr = self.tree.AppendItem(sib, 'Liquidity Coverage Ratio')
            self.tree.AppendItem(lcr, 'Due from banks')
            self.tree.AppendItem(lcr, 'Due to banks')
            self.tree.AppendItem(lcr, 'REPO')
            self.tree.AppendItem(lcr, 'Securities')
            self.tree.AppendItem(lcr, 'Due to individuals')
            self.tree.AppendItem(lcr, 'Due to customers')
            self.tree.AppendItem(lcr, 'Due from individuals')
            self.tree.AppendItem(lcr, 'Obligatory expenses')
            self.tree.AppendItem(lcr, 'Securities issued')

            nsfr = self.tree.AppendItem(sib, 'Net Stable Funding Ratio')
            self.tree.AppendItem(nsfr, 'Due to individuals')
            self.tree.AppendItem(nsfr, 'Due to customers')

            self.tree.ExpandAll()
            self.tree.SelectItem(lcr)

    def OnCreateReport(self, event):
        if self.current_view != 'Accounting' and hasattr(self, 'current_report'):
            self.CreateReport(self.current_report)

    def OnTreeSelChanged(self, event):
        item = event.GetItem()
        if not item.IsOk():
            return

        text = self.tree.GetItemText(item).strip()

        if self.current_view != 'Accounting':
            self.HandleReportSelection(text)
            #later add elif self.current_view == 'Accounting': --to react to item selection in accounting view

    def HandleReportSelection(self, report_name):

        #mapping displayed names to internal report keys
        report_map = {
            'Liquidity Coverage Ratio': 'lcr',
            'Net Stable Funding Ratio': 'nsfr',
            'Weighted average rates': 'weighted_rates',
            'Due from banks': 'view1',
            'Due to banks': 'view2'
            #More reports to be added here
        }

        key = report_map.get(report_name)
        if key:
            self.current_report = key
            self.CreateReport(key, title=report_name)
            self.SetStatusText(f"Report: {report_name}")
            return

    def CreateReport(self, report_key, title='Report'):
        if self.oracle_cursor is None:
            self.ShowMessage("Not connected to database", "Warning")
            self.ClearGrid()
            return

        project_folder = os.path.dirname(os.path.abspath(__file__))
        scripts_folder = os.path.join(project_folder, 'scripts')

        #removing old data and structure
        self.ClearGrid()

        try:
            if report_key == 'lcr':
                sql = """
                SELECT * FROM etl.CALC_SZKO
                WHERE 1=1
                AND DT_REP = :dt
                """
                params = (self.GetReportDateISO(),)
                columns = ['REPORT DATE', 'ITEM', 'LINE CODE', 'ARTICLE', 'AMOUNT', 'COEFFICIENT', 'WEIGHTED AMOUNT']

            elif report_key == 'nsfr':
                sql = "SELECT * FROM Articles"
                #params = (self.GetReportDateISO(),)
                columns = ['Article UID', 'Parent Article UID', 'Article Code', 'Article Name', 'Article Sort Order', 'Balance Sheet Side', 'Article Level']

            elif report_key == 'weighted_rates':
                sql = """
                SELECT * FROM sales
                WHERE DT_REP > ?
                """
                params = (self.GetReportDateISO(),)
                columns = ['DATE', 'ITEM', 'AMOUNT']
                print("weighted rates script OK")

            elif report_key == 'view1':

                script = os.path.join(scripts_folder, 'view1.sql')

                if not os.path.exists(script):
                    wx.MessageBox(f"SQL file not found: {script}", "Error", wx.OK | wx.ICON_ERROR)
                    return

                with open(script, 'r') as file:
                    sql = file.read().strip()

                params = (self.GetReportDateISO(),)
                columns = ['REPORT DATE', 'ACCOUNT', 'ACCOUNT ID', 'ACCOUNT DESCRIPTION', 'CONTRACT', 'CONTRACT ID', 'ACCOUNT ROLE', 'CONTO', 'CLIENT ID', 'CLIENT SUBTYPE', 'INN', 'CLIENT NAME', 'CLIENT TYPE', 'COUNTRY', 'REGION ID', 'SEGMENT', 'PRODUCT', 'PRODUCT TYPE', 'PRODUCT SUBTYPE', 'OKOPF', 'OKVED CODE', 'OKVED NAME', 'OKVED TYPE', 'CONTRACT TYPE', 'SME', 'CURRENCY', 'OPEN DATE', 'CLOSE DATE PLAN', 'CLOSE DATE FACT', 'CLOSE DATE', 'INFLOW', 'AMOUNT', 'QUALITY CATEGORY', 'PROVISION RATE', 'OVERDUE AMOUNT', 'PD', 'LOSS ALLOWANCE']

            elif report_key == 'view2':

                script = os.path.join(scripts_folder, 'view2.sql')

                if not os.path.exists(script):
                    wx.MessageBox(f"SQL file not found: {script}", "Error", wx.OK | wx.ICON_ERROR)
                    return

                with open(script, 'r') as file:
                    sql = file.read().strip()

                params = (self.GetReportDateISO(),)
                columns = ['REPORT DATE', 'CONTO', 'PRODUCT TYPE', 'PRODUCT SUBTYPE', 'CONTRACT TYPE', 'OUTFLOW', 'AMOUNT']

            else:
                self.display_grid.AppendRows(1)
                self.display_grid.SetCellValue(0, 0, f"Report '{report_key}' not implemented yet")
                return

            #executing query
            self.oracle_cursor.execute(sql, params)
            rows = self.oracle_cursor.fetchall()

            if not rows:
                print("no rows")
                #self.display_grid.AppendRows(1)
                #self.display_grid.SetCellValue(0, 0, "No data for selected date")

            #column names from cursor or from our predefined list
            if columns:
                col_names = columns
            else:
                col_names = [desc[0].upper().replace("_", " ") for desc in self.cursor.description]


            #setting up grid structure
            self.display_grid.AppendCols(len(col_names))
            for i, name in enumerate(col_names):
                self.display_grid.SetColLabelValue(i, name)

            self.display_grid.AppendRows(len(rows))

            print("Grid structure set successfully")


            #filling data
            for r, row in enumerate(rows):
                for c, value in enumerate(row):
                    display_value = f"{value:.2f}" if isinstance(value, (int, float)) else str(value or "")
                    self.display_grid.SetCellValue(r, c, display_value)

            #formatting and usability
            self.display_grid.AutoSize()
            #self.display_grid.SetDefaultRowSize(17)
            self.display_grid.SetColLabelSize(19)
            self.display_grid.SetRowLabelSize(0)
            self.display_grid.EnableEditing(False)

        except Exception as e:
            self.ShowMessage(f"Error loading report:\n{str(e)}", "Database Error")
            self.ClearGrid()

    def ClearGrid(self):
        if self.display_grid.GetNumberRows() > 0:
                self.display_grid.DeleteRows(0, self.display_grid.GetNumberRows())
        if self.display_grid.GetNumberCols() > 0:
                self.display_grid.DeleteCols(0, self.display_grid.GetNumberCols())

    def GetReportDateISO(self):
        #converting wx.DatePickerCtrl value to 'YYYY-MM-DD' string
        dt_rep = self.date_ctrl.GetValue()
        year = dt_rep.GetYear()
        month = dt_rep.GetMonth() + 1
        day = dt_rep.GetDay()
        dt_rep = date(year, month, day)
        return dt_rep
        #return f"{dt_rep.GetDay():02d}-{dt_rep.GetMonth()+1:02d}-{dt_rep.GetYear():04d}"

    def ShowMessage(self, msg, title = "Information"):
        wx.MessageBox(msg, title, wx.OK | wx.ICON_INFORMATION)

def start_app():
    app = wx.App(False)

    frame = MainFrame()

    app.MainLoop()

def load_icon(filename):
    path = os.path.join('icons', filename)
    bmp = wx.Bitmap(path)
    if not bmp.IsOk():
        print(f'Warning: Could not load icon: {path}')

    return bmp

if __name__ == "__main__":
    start_app()
