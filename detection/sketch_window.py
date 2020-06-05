import wx
import os
filesFilter = "All files (*.*)|*.*"
BASE_DIR = os.getcwd()
TXT_FILE = os.path.join(BASE_DIR, 'LABEL')
RECT_PIC_FILE = os.path.join(BASE_DIR, 'RECT_PIC')

class SketchWindow(wx.Window):
    def __init__(self, parent, ID):
        wx.Window.__init__(self, parent, ID)
        # 文件绝对路径名
        self.work_pic_name = None
        self.label = None
        # self.is_pic = False
        self.pic_dir = os.getcwd()
        self.last_label = ''

        # 保存文件名列表
        self.pic_list = []
        self.pic_index = 0
        self.pic_info = {}
        self.about_draw_rect = False
        self.reInitBuffer = False
        self.SetBackgroundColour('White')
        self.rect_points = []
        self.rect_pos = (0, 0)
        self.pos = (0, 0)
        self.InitBuffer()
        # 连接事件
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Bind(wx.EVT_IDLE, self.OnIdle)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self, self.buffer)

    def get_bitmap(self):
        img = wx.Image(self.work_pic_name, wx.BITMAP_TYPE_ANY)
        img.Rescale(860, 484)
        w = img.GetWidth()
        h = img.GetHeight()
        return img.ConvertToBitmap(), w, h

    def InitBuffer(self):
        w, h = self.GetClientSize()
        # 创建一个缓存的设备上下文
        self.buffer = wx.Bitmap(w, h)
        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        self.DrawGraph(dc, w, h)
        self.reInitBuffer = False

    def DrawGraph(self, dc, w, h):
        dc.SetBackground(wx.Brush(self.GetBackgroundColour()))
        dc.Clear()
        dc.SetPen(wx.Pen('red', 2))
        # dc.SetPen(wx.Pen((0, 0, 255), 2))
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        if not self.work_pic_name:
            return
        img, img_w, img_h = self.get_bitmap()
        if os.path.exists(self.work_pic_name):
            dc.DrawBitmap(img, 0, 0)
        name = os.path.basename(self.work_pic_name)
        if name in self.pic_info:
            for rect in self.pic_info[name]:
                dc.DrawRectangle(*rect)
        else:
            self.pic_info.setdefault(name, [])
        if len(self.rect_points) == 2:
            self.fix_rect_points(img_w, img_h)
            dc.DrawRectangle(*self.form_rect())
            self.pic_info[name].append(self.form_rect())
            if self.label:
                self.save_label(self.label, self.rect_points)
                self.label = None
            self.rect_points = []

        if self.about_draw_rect:
            dc.SetPen(wx.Pen('green', 1))
            dc.DrawLine(0, self.pos[1], w, self.pos[1])
            dc.DrawLine(self.pos[0], 0, self.pos[0], h)
            if len(self.rect_points) == 1:
                dc.SetPen(wx.Pen('red', 2))
                # dc.SetPen(wx.Pen((0, 0, 255), 2))
                dc.DrawRectangle(*self.fix_rect(img_w, img_h))

    def fix_rect(self, img_w, img_h):
        start_x, end_x = sorted([min(max(self.rect_points[0][0], 0), img_w), min(max(self.pos[0], 0), img_w)])
        start_y, end_y = sorted([min(max(self.rect_points[0][1], 0), img_h), min(max(self.pos[1], 0), img_h)])
        return start_x, start_y, end_x - start_x, end_y - start_y

    def fix_rect_points(self, img_w, img_h):
        x1 = min(max(self.rect_points[0][0], 0), img_w)
        x2 = min(max(self.rect_points[1][0], 0), img_w)
        y1 = min(max(self.rect_points[0][1], 0), img_h)
        y2 = min(max(self.rect_points[1][1], 0), img_h)
        self.rect_points[0] = wx.Point(min(x1, x2), min(y1, y2))
        self.rect_points[1] = wx.Point(max(x1, x2), max(y1, y2))

    def form_rect(self):
        x = self.rect_points[0][0]
        y = self.rect_points[0][1]
        w = self.rect_points[1][0] - x
        h = self.rect_points[1][1] - y
        return x, y, w, h

    def OnLeftDown(self, event):
        if not self.about_draw_rect:
            event.Skip()
            return
        self.rect_points = []
        self.rect_pos = event.GetPosition()  # 5 得到鼠标的位置
        self.rect_points.append(self.rect_pos)
        self.CaptureMouse()#6 捕获鼠标

    def OnLeftUp(self, event):
        if not self.about_draw_rect or not self.rect_points:
            event.Skip()
            return
        self.rect_pos = event.GetPosition()  # 5 得到鼠标的位置
        self.rect_points.append(self.rect_pos)
        self.ReleaseMouse()#7 释放鼠标
        self.about_draw_rect = False
        self.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT))
        # temp_rect = self.rect_points[:]
        self.label = wx.GetTextFromUser('请输入目标序号', 'AutoLabelling',
                                    default_value=str(self.last_label),
                                    parent=None, x=self.rect_pos[0], y=self.rect_pos[1], centre=False)
        self.InitBuffer()
        # self.save_label(label, temp_rect)

    def save_label(self, lable, temp_rect):
        txt_name = self.work_pic_name.split('\\')[-1].split('.')[0] + '.txt'
        x = temp_rect[0][0]
        y = temp_rect[0][1]
        w = temp_rect[1][0] - x
        h = temp_rect[1][1] - y
        with open(os.path.join(TXT_FILE, txt_name), 'a') as f:
            f.write('{} {} {} {} {}\n'.format(x, y, w, h, lable))

    def OnMotion(self, event):
        # 确定是否在画矩形状态
        self.pos = event.GetPosition()
        if self.about_draw_rect:
            self.InitBuffer()

        event.Skip()

    # 绘画到设备上下文
    def drawMotion(self, dc, event):
        dc.SetPen(wx.Pen('red', 1))
        dc.CrossHair(*self.pos)

    def OnSize(self, event):
        self.reInitBuffer = True

    def OnIdle(self, event):  # 空闲时的处理
        if self.reInitBuffer:
            if self.pic_list:
                name = self.pic_list[self.pic_index]
                temp_name = os.path.join(self.pic_dir, name)
                if os.path.exists(temp_name):
                    self.work_pic_name = temp_name
            self.InitBuffer()
            self.Refresh(False)

    def OnKeyDown(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_SPACE and self.work_pic_name:
            self.about_draw_rect = True
            self.SetCursor(wx.Cursor(wx.CURSOR_CROSS))
            self.InitBuffer()
        elif key == wx.WXK_ESCAPE:
            self.about_draw_rect = False
            self.SetCursor(wx.Cursor(wx.CURSOR_DEFAULT))
            self.rect_points = []
            self.InitBuffer()
            try:
                self.ReleaseMouse()
            except (SystemError, wx._core.wxAssertionError):
                pass
        else:
            event.Skip()

    def SetColor(self, color):
        self.color = color
        self.pen = wx.Pen(self.color, self.thickness, wx.SOLID)

    def SetThickness(self, num):
        self.thickness = num
        self.pen = wx.Pen(self.color, self.thickness, wx.SOLID)


class SketchFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'Sketch Frame',
                size=(800,600))
        self.sketch = SketchWindow(self, -1)


if __name__ == '__main__':
    app = wx.App()
    frame = SketchFrame(None)
    frame.Show(True)
    app.MainLoop()

