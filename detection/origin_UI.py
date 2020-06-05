import wx
def InitUI(self):
    sizer_all = wx.BoxSizer(wx.HORIZONTAL)
    sizer_all_left = wx.BoxSizer(wx.VERTICAL)
    sizer_listbox = wx.BoxSizer(wx.HORIZONTAL)
    sizer_pic = wx.BoxSizer(wx.HORIZONTAL)
    sizer_top = wx.BoxSizer(wx.HORIZONTAL)
    sizer_bottom = wx.BoxSizer(wx.HORIZONTAL)

    # sizer_recm = wx.BoxSizer(wx.VERTICAL)

    sizer_pic.Add(self.sketch_window, 1, flag=wx.EXPAND | wx.ALL)
    sizer_listbox.Add(self.list_box, 1, flag=wx.EXPAND | wx.ALL)
    # sizer_recm.Add(self.sketch_recm, 1, flag=wx.EXPAND | wx.ALL)
    sizer_top.Add(sizer_pic, 4, flag=wx.EXPAND | wx.ALL)
    # sizer_top.Add((5, -1))
    # sizer_top.Add(sizer_recm, 3, flag=wx.EXPAND | wx.ALL)
    sizer_top.Add((5, -1))
    sizer_top.Add(sizer_listbox, 1, flag=wx.EXPAND | wx.ALL)

    sizer_all_left.Add(sizer_top, 9, flag=wx.EXPAND | wx.ALL, border=5)
    sizer_all_left.Add((-1, 1))

    btn_prev = wx.Button(self, -1, u"上一张")
    self.Bind(wx.EVT_BUTTON, self.on_button_prev, btn_prev)

    btn_next = wx.Button(self, -1, u"下一张")
    self.Bind(wx.EVT_BUTTON, self.on_button_next, btn_next)

    btn_detection = wx.Button(self, -1, u"自动检测")
    self.Bind(wx.EVT_BUTTON, self.on_button_detection, btn_detection)

    btn_clear = wx.Button(self, -1, u"清除标注")
    self.Bind(wx.EVT_BUTTON, self.on_button_clear, btn_clear)

    # btn_recommend = wx.Button(self, -1, u"推荐编号")
    # self.Bind(wx.EVT_BUTTON, self.on_button_recommend, btn_recommend)

    # sizer_bottom = wx.FlexGridSizer(rows=1, cols=5, vgap=1, hgap=0)
    sizer_bottom.Add(btn_prev, 1, flag=wx.SHAPED | wx.ALL | wx.LEFT | wx.RIGHT, border=0)
    sizer_bottom.Add(btn_detection, 1, flag=wx.SHAPED | wx.ALL | wx.LEFT | wx.RIGHT, border=0)
    sizer_bottom.Add(btn_clear, 1, flag=wx.SHAPED | wx.ALL | wx.LEFT | wx.RIGHT, border=0)
    # sizer_bottom.Add(btn_recommend, 1, flag=wx.SHAPED | wx.ALL | wx.LEFT | wx.RIGHT, border=0)
    sizer_bottom.Add(btn_next, 1, flag=wx.SHAPED | wx.ALL | wx.LEFT | wx.RIGHT, border=0)
    # sizer_bottom.Add(info_window, 1, flag=wx.SHAPED | wx.LEFT | wx.RIGHT, border=1)

    sizer_all_left.Add(sizer_bottom, 1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)

    # 激活sizer
    self.SetSizer(sizer_all_left)
    self.SetAutoLayout(True)
    sizer_all_left.Fit(self)
    self.Show(True)

    self.Center()