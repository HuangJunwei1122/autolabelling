import threading
import wx
import time

from test import detect


class Detection(threading.Thread):
    def __init__(self, window):
        super(Detection, self).__init__()
        self.window = window
        self.event = threading.Event()

    def run(self):
        # 显示一些状态
        # start_time = time.time()
        all_time = detect(self.window.pic_dir, file_or_pic='file')
        print(all_time)
        # stop_time = time.time()
        wx.CallAfter(self.window.on_detect_done, all_time)


