import wx
# class SketchApp(wx.App):
#     def OnInit(self):
#         bmp = wx.Image('splash.png').ConvertToBitmap()
#         wx.SplashScreen(bmp, wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT, 1000, None, -1)
#         wx.Yield()
#         frame = SketchFrame(None)
#         frame.Show(True)
#         self.SetTopWindow(frame)
#         return True
#
# app = wx.App()
# d = wx.GetTextFromUser('请输入','try',default_value = '', parent = None)
# print(d,type(d))

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        # self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_MOTION, self.OnSketchMotion)
        self.statusbar = self.CreateStatusBar()
        self.pos = (0,0)
        self.InitBuffer()
    def OnSketchMotion(self, event):
        self.pos = event.GetPosition()
        self.InitBuffer()
        self.statusbar.SetStatusText(str(self.pos))
        event.Skip()
    def InitBuffer(self):
        w, h = self.GetClientSize()
        # 创建一个缓存的设备上下文
        self.buffer = wx.Bitmap(w, h)
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        self.DrawGraph(dc)
    def DrawGraph(self, dc):
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        dc.SetPen(wx.Pen('red', 2))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(*self.pos, 5,5)
        dc.DrawBitmap(self, dc.CrossHair(self.pos))
    def OnMotion(self, event):
        self.pos = event.GetPosition()
    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self, self.buffer)

if __name__ == '__main__':
    app = wx.App()
    frm = MyFrame()
    frm.Show()
    app.MainLoop()

