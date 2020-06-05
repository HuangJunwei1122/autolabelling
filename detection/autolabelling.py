import os
from shutil import rmtree
import wx
import imghdr

from test import detect, rect_pic, built_save_dir
from sketch_window import SketchWindow
from detect_thread import Detection


filesFilter = "All files (*.*)|*.*"
TXT_FILE = 'LABEL'
RECT_PIC_FILE = 'RECT_PIC'


class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title='AutoLabelling', size=(1920, 1080))
        self.is_detecting = False
        self.sketch_window = SketchWindow(self, -1)
        self.sketch_window.Bind(wx.EVT_MOTION, self.OnSketchMotion)
        self.pic_dir = os.getcwd()
        self.pic_list = []
        self.list_box = wx.ListBox(self, -1, pos=(0, 0), size=(-1, -1),
                                   choices=self.pic_list, style=wx.LB_SINGLE | wx.LB_ALWAYS_SB | wx.LB_SORT)
        self.list_box.Bind(wx.EVT_LISTBOX_DCLICK, self.on_choose_pic)
        self.sketch_recm = wx.Window(self, -1)
        self.statusbar = self.CreateStatusBar()
        self.menu_init()
        self.InitUI()
        self.init_save_file()

    def init_save_file(self):
        rmtree(TXT_FILE, ignore_errors=True)
        rmtree(RECT_PIC_FILE, ignore_errors=True)
        os.makedirs(TXT_FILE)
        os.makedirs(RECT_PIC_FILE)

    def on_choose_pic(self, event):
        if self.list_box.GetCount() == 0:
            return
        name = event.GetString()
        if name in self.sketch_window.pic_list:
            self.sketch_window.pic_index = self.list_box.FindString(name)
        self.sketch_window.work_pic_name = os.path.join(self.pic_dir, name)
        self.sketch_window.reInitBuffer = True

    def menu_init(self):
        menubar = wx.MenuBar()
        file = wx.Menu()
        q = wx.Menu()
        h = wx.Menu()
        pick_one_pic = file.Append(wx.ID_FILE1, u"选择图片", u'选择一张图片')
        cd_dir = file.Append(wx.ID_FILE2, u"选择目录", u'进入该目录')
        menubar.Append(file, "&File")
        menubar.Append(q, "&Exit")
        menubar.Append(h, "&Help")
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU, self.on_open_pic, pick_one_pic)
        self.Bind(wx.EVT_MENU, self.on_open_file, cd_dir)

    def InitUI(self):
        sizer_all = wx.BoxSizer(wx.HORIZONTAL)
        sizer_all_left = wx.BoxSizer(wx.VERTICAL)
        sizer_listbox = wx.BoxSizer(wx.HORIZONTAL)
        sizer_pic = wx.BoxSizer(wx.HORIZONTAL)
        # sizer_top = wx.BoxSizer(wx.HORIZONTAL)
        sizer_bottom = wx.BoxSizer(wx.HORIZONTAL)

        # sizer_recm = wx.BoxSizer(wx.VERTICAL)

        sizer_pic.Add(self.sketch_window, 1, flag=wx.EXPAND | wx.ALL)
        sizer_listbox.Add(self.list_box, 1, flag=wx.EXPAND | wx.ALL)
        # sizer_recm.Add(self.sketch_recm, 1, flag=wx.EXPAND | wx.ALL)
        # sizer_top.Add(sizer_pic, 4, flag=wx.EXPAND | wx.ALL)
        # sizer_top.Add((5, -1))
        # sizer_top.Add(sizer_recm, 3, flag=wx.EXPAND | wx.ALL)
        # sizer_top.Add((5, -1))
        # sizer_top.Add(sizer_listbox, 1, flag=wx.EXPAND | wx.ALL)

        # sizer_all_left.Add(sizer_top, 9, flag=wx.EXPAND | wx.ALL, border=5)
        sizer_all_left.Add(sizer_pic, 9, flag=wx.EXPAND | wx.ALL, border=5)
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
        sizer_bottom.Add(btn_prev, 1, flag=wx.SHAPED | wx.ALL | wx.ALIGN_LEFT)
        sizer_bottom.Add(btn_detection, 1, flag=wx.SHAPED | wx.ALL | wx.ALIGN_CENTER)
        sizer_bottom.Add(btn_clear, 1, flag=wx.SHAPED | wx.ALL | wx.ALIGN_CENTER)
        # sizer_bottom.Add(btn_recommend, 1, flag=wx.SHAPED | wx.ALL | wx.LEFT | wx.RIGHT, border=0)
        sizer_bottom.Add(btn_next, 1, flag=wx.SHAPED | wx.ALL | wx.ALIGN_RIGHT)
        # sizer_bottom.Add(info_window, 1, flag=wx.SHAPED | wx.LEFT | wx.RIGHT, border=1)

        sizer_all_left.Add(sizer_bottom, 1, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=5)

        sizer_all.Add(sizer_all_left, 3, flag=wx.EXPAND | wx.ALL)
        # sizer_all.Add((5, -1))
        sizer_all.Add(sizer_listbox, 1, flag=wx.EXPAND | wx.ALL)

        # 激活sizer
        self.SetSizer(sizer_all)
        self.SetAutoLayout(True)
        sizer_all.Fit(self)
        self.Show(True)

        self.Center()

    def OnSketchMotion(self, event):
        self.statusbar.SetStatusText(str(event.GetPosition()))
        event.Skip()

    def reinit_sketch_window(self):
        self.sketch_window.last_label = ''
        self.sketch_window.pic_list = []
        self.pic_list = []
        self.sketch_window.pic_info = {}
        self.sketch_window.pic_index = 0

    def on_open_pic(self, event):
        # 定义按钮的名称和功能，wx.FD_OPEN代表这个按钮用于选择、打开文件
        dlg = wx.FileDialog(self, message=u"打开文件", wildcard=filesFilter, style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.sketch_window.work_pic_name = dlg.GetPath()
            self.reinit_sketch_window()
            self.pic_dir = os.path.dirname(self.sketch_window.work_pic_name)
            self.sketch_window.pic_dir = self.pic_dir
            self.list_box.Set(self.pic_list)
            self.sketch_window.reInitBuffer = True
        dlg.Destroy()

    def on_open_file(self, event):
        dlg = wx.DirDialog(self, u"选择文件夹", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            # rect_value = []
            self.pic_dir = dlg.GetPath()
            self.sketch_window.pic_dir = self.pic_dir
            self.pic_list = sorted([i for i in next(os.walk(self.pic_dir))[2]
                                    if imghdr.what(os.path.join(self.pic_dir, i))])
            self.sketch_window.pic_list = self.pic_list[:]
            self.sketch_window.pic_info = {}
            self.sketch_window.pic_index = 0
            self.list_box.Set(self.pic_list)
            if self.pic_list:
                self.sketch_window.work_pic_name = os.path.join(self.sketch_window.pic_dir,
                                                                self.sketch_window.pic_list[0])
                self.list_box.SetSelection(self.sketch_window.pic_index)
            else:
                self.sketch_window.work_pic_name = None

            # for _ in range(len(self.pic_list)):
            #     rect_value.append([])
            # self.sketch_window.pic_info = dict(zip(self.sketch_window.pic_list, rect_value))
            self.sketch_window.reInitBuffer = True
        dlg.Destroy()

    def on_button_detection(self, event):
        if self.is_detecting:
            dlg = wx.MessageDialog(None, u"正在检测中，请等待当前检测过程结束", "MessageDialog", wx.OK)
            dlg.ShowModal()
            dlg.Destroy()
            return
        else:
            self.is_detecting = True
        if not self.pic_list and not self.sketch_window.work_pic_name:
            self.is_detecting = False
            return
        try:
            built_save_dir()
        except PermissionError:
            self.is_detecting = False
            return
        if not self.pic_list:
            detect(self.sketch_window.work_pic_name, file_or_pic='pic')
            self.is_detecting = False
        else:
            thread = Detection(self)
            thread.start()

    def on_detect_done(self, cost_time):
        print(u'本次检测耗时{}s'.format(cost_time))
        self.pic_dir = os.path.join(os.getcwd(), r'pic_with_rect\rect_pic')
        self.sketch_window.pic_dir = self.pic_dir
        self.pic_list = sorted([i for i in next(os.walk(self.pic_dir))[2]
                                if imghdr.what(os.path.join(self.pic_dir, i))])
        self.sketch_window.pic_list = self.pic_list[:]
        self.sketch_window.pic_info = {}
        self.sketch_window.pic_index = 0
        if self.pic_list:
            self.sketch_window.work_pic_name = os.path.join(self.sketch_window.pic_dir,
                                                            self.sketch_window.pic_list[0])
        else:
            self.sketch_window.work_pic_name = None
        self.list_box.Set(self.pic_list)
        if self.list_box.GetCount() > 0:
            self.list_box.SetSelection(self.sketch_window.pic_index)
        self.sketch_window.reInitBuffer = True
        self.is_detecting = False
        dlg = wx.MessageDialog(None, u"自动检测已完成！\n总耗时{}s".format(cost_time), "MessageDialog", wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def on_button_recommend(self, event):
        pass

    def on_button_clear(self, event):
        if not self.sketch_window.work_pic_name:
            return
        pic_dir = os.path.dirname(self.sketch_window.work_pic_name)
        name = self.sketch_window.work_pic_name[len(pic_dir)+1:]
        if name in self.sketch_window.pic_info:
            self.sketch_window.pic_info[name] = []
            self.sketch_window.rect_points = []
            self.sketch_window.reInitBuffer = True

    def on_button_next(self, event):
        if not self.sketch_window.pic_list or self.sketch_window.pic_index == len(self.sketch_window.pic_list) - 1:
            return
        self.sketch_window.pic_index += 1

        self.list_box.SetSelection(self.sketch_window.pic_index)

        self.sketch_window.reInitBuffer = True

    def on_button_prev(self, event):
        if not self.sketch_window.pic_list or self.sketch_window.pic_index == 0:
            return
        self.sketch_window.pic_index -= 1

        self.list_box.SetSelection(self.sketch_window.pic_index)

        self.sketch_window.reInitBuffer = True


app = wx.App()
frm = MyFrame()
frm.Show()
app.MainLoop()
