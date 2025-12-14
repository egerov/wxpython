import wx
import wx.aui

class ModernFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, title="Modern wxPython UI with Toolbar", size=(1000, 700))

        # Use AuiManager for modern docking panes
        self.mgr = wx.aui.AuiManager(self)

        # Create menu bar
        self.create_menu_bar()

        # Create toolbar
        self.create_toolbar()

        # Left sidebar (navigation)
        self.left_panel = wx.Panel(self)
        self.left_panel.SetBackgroundColour(wx.Colour(40, 44, 52))  # Dark sidebar

        tree = wx.TreeCtrl(self.left_panel, style=wx.TR_HAS_BUTTONS | wx.TR_LINES_AT_ROOT)
        root = tree.AddRoot("Navigation")
        tree.AppendItem(root, "Dashboard")
        tree.AppendItem(root, "Projects")
        tree.AppendItem(root, "Files")
        tree.AppendItem(root, "Settings")
        tree.AppendItem(root, "Help")
        tree.Expand(root)

        left_sizer = wx.BoxSizer(wx.VERTICAL)
        left_sizer.Add(tree, 1, wx.EXPAND | wx.ALL, 5)
        self.left_panel.SetSizer(left_sizer)

        # Main content area
        self.main_panel = wx.Panel(self)
        self.main_panel.SetBackgroundColour(wx.Colour(30, 30, 30))

        content_text = wx.StaticText(
            self.main_panel,
            label="Main Content Area\n\nWelcome to the application!\nUse the toolbar for quick actions.",
            style=wx.ALIGN_CENTER
        )
        content_text.SetForegroundColour(wx.WHITE)
        content_text.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))

        main_sizer = wx.BoxSizer(wx.VERTICAL)
        main_sizer.Add(content_text, 1, wx.ALIGN_CENTER | wx.ALL, 50)
        self.main_panel.SetSizer(main_sizer)

        # Add panes to AuiManager
        self.mgr.AddPane(self.left_panel, wx.aui.AuiPaneInfo().
                         Name("sidebar").
                         Caption("Navigation").
                         Left().
                         BestSize(280, -1).
                         MinSize(200, -1).
                         CloseButton(False).
                         MaximizeButton(True))

        # Toolbar at the top
        self.mgr.AddPane(self.toolbar, wx.aui.AuiPaneInfo().
                         Name("toolbar").
                         Caption("Toolbar").
                         ToolbarPane().
                         Top().
                         CloseButton(False).
                         Gripper(True))

        # Main content in center
        self.mgr.AddPane(self.main_panel, wx.aui.AuiPaneInfo().
                         Name("main").
                         CenterPane().
                         CloseButton(False))

        self.mgr.Update()

        # Status bar
        self.CreateStatusBar()
        self.SetStatusText("Ready")

        self.Centre()

    def create_menu_bar(self):
        menubar = wx.MenuBar()

        file_menu = wx.Menu()
        file_menu.Append(wx.ID_NEW, "&New\tCtrl+N")
        file_menu.Append(wx.ID_OPEN, "&Open\tCtrl+O")
        file_menu.Append(wx.ID_SAVE, "&Save\tCtrl+S")
        file_menu.AppendSeparator()
        file_menu.Append(wx.ID_EXIT, "E&xit\tAlt+F4")
        menubar.Append(file_menu, "&File")

        help_menu = wx.Menu()
        help_menu.Append(wx.ID_ABOUT, "&About")
        menubar.Append(help_menu, "&Help")

        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.on_exit, id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, self.on_about, id=wx.ID_ABOUT)

    def create_toolbar(self):
        self.toolbar = tb = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_HORIZONTAL)

        tb.AddTool(wx.ID_NEW, "New", wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, (24,24)), "Create new")
        tb.AddTool(wx.ID_OPEN, "Open", wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, (24,24)), "Open file")
        tb.AddTool(wx.ID_SAVE, "Save", wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR, (24,24)), "Save file")
        tb.AddSeparator()

        tb.AddTool(wx.ID_CUT, "Cut", wx.ArtProvider.GetBitmap(wx.ART_CUT, wx.ART_TOOLBAR, (24,24)))
        tb.AddTool(wx.ID_COPY, "Copy", wx.ArtProvider.GetBitmap(wx.ART_COPY, wx.ART_TOOLBAR, (24,24)))
        tb.AddTool(wx.ID_PASTE, "Paste", wx.ArtProvider.GetBitmap(wx.ART_PASTE, wx.ART_TOOLBAR, (24,24)))
        tb.AddSeparator()

        tb.AddTool(wx.ID_UNDO, "Undo", wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_TOOLBAR, (24,24)))
        tb.AddTool(wx.ID_REDO, "Redo", wx.ArtProvider.GetBitmap(wx.ART_REDO, wx.ART_TOOLBAR, (24,24)))

        tb.Realize()

    def on_exit(self, event):
        self.mgr.UnInit()
        self.Close()

    def on_about(self, event):
        wx.MessageBox("Modern wxPython UI Demo\nWith MenuBar, Toolbar, and Sidebar",
                      "About", wx.OK | wx.ICON_INFORMATION)


# ========================
# START OF THE APPLICATION
# ========================
if __name__ == "__main__":
    # Create the wx.App instance (required for all wxPython apps)
    app = wx.App(False)  # False = don't redirect stdout/stderr to window

    # Create the main window (frame)
    frame = ModernFrame()

    # THIS LINE SHOWS THE WINDOW ON SCREEN
    frame.Show()  # <-- Important: makes the window visible

    # Start the main event loop (keeps the app running and responsive)
    app.MainLoop()
# ========================
# END OF APPLICATION START
# ========================
