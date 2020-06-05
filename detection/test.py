import cv2
import os
from shutil import rmtree
from pathlib import Path
import imghdr
import time
import torch
import threading

from process import pre_process, ctdet_decode, post_process, merge_outputs
from model import get_model

save_path = r'pic_with_rect'
rect_pic = os.path.join(save_path, 'rect_pic')
rect_txt = os.path.join(save_path, 'rect_txt')


def built_save_dir():
    rmtree(save_path, ignore_errors=True)
    os.makedirs(save_path)
    os.makedirs(rect_pic)
    os.makedirs(rect_txt)


class KeepModel(object):
    _model_lock = threading.Lock()

    def __init__(self, model_path, test_gpu):
        self.model = self.load_model(model_path, test_gpu)

    def __new__(cls, model_path, test_gpu):
        if not hasattr(cls, '_instance'):
            with KeepModel._model_lock:
                if not hasattr(cls, '_instance'):
                    KeepModel._instance = super().__new__(cls)
        return KeepModel._instance

    @staticmethod
    def load_model(model_path, test_gpu):
        heads = {'hm': 1, 'wh': 2, 'reg': 2}
        model = get_model(34, heads, -1)
        model.load_state_dict(torch.load(f'{model_path}', map_location='cpu'))
        model.to(torch.device(test_gpu))
        model = model.eval()
        return model


def detection1(image_dir, model_path):
    built_save_dir()
    root = Path(image_dir)
    test_gpu = "cpu"
    time1 = time.time()
    model = KeepModel(model_path, test_gpu).model
    time2 = time.time()
    print(u'加载模型用时{}s'.format(time2-time1))
    all_time = 0
    for item in root.iterdir():
        if not imghdr.what(item):
            continue
        try:
            ori_img = cv2.imread(str(item))
            ori_img = cv2.resize(ori_img, (640, 480))
        except cv2.error:
            continue
        img = ori_img
        time_start = time.time()
        img, meta = pre_process(img)
        with torch.no_grad():
            img = img.to(torch.device(test_gpu))
            output = model(img)
            hm = output['hm'].sigmoid_()
            wh = output['wh']
            reg = output['reg']
            dets = ctdet_decode(hm, wh, reg=reg, K=30)
            dets = post_process(dets, meta)
            detection = [dets]
            results = merge_outputs(detection)
        time_end = time.time()
        all_time += time_end-time_start
        result = results[1]
        i = 0
        for r in result:
            with open(os.path.join(rect_txt, os.path.splitext(str(item))[0].split('\\')[-1]+'.txt'), 'a') as f:
                f.write('{} {} {} {} {}\n'.format(int(r[0]), int(r[1]), int(r[2]-r[0]), int(r[3]-r[1]), i))
            cv2.rectangle(ori_img, (int(r[0]), int(r[1])), (int(r[2]), int(r[3])), (255, 0, 0), 2)
            cv2.putText(ori_img, str(i), (int(r[0]), int(r[1])), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 2)
            i += 1
        if len(result) != 0:
            print(os.path.join(rect_pic, os.path.basename(str(item)))+'               {}s'.format(time_end-time_start))
            try:
                cv2.imwrite(os.path.join(rect_pic, os.path.basename(str(item))), ori_img)
            except cv2.error:
                name = os.path.splitext(os.path.basename(str(item)))[0] + '.jpg'
                cv2.imwrite(os.path.join(rect_pic, name), ori_img)
    return all_time


def detection2(image_path, model_path):
    test_gpu = "cpu"
    model = KeepModel(model_path, test_gpu).model

    ori_img = cv2.imread(image_path)
    ori_img = cv2.resize(ori_img, (640, 480))
    img = ori_img
    img, meta = pre_process(img)
    with torch.no_grad():
        img = img.to(torch.device(test_gpu))
        output = model(img)
        hm = output['hm'].sigmoid_()
        wh = output['wh']
        reg = output['reg']
        dets = ctdet_decode(hm, wh, reg=reg, K=30)
        dets = post_process(dets, meta)
        detection = [dets]
        results = merge_outputs(detection)

    result = results[1]
    for r in result:
        cv2.rectangle(ori_img, (int(r[0]), int(r[1])), (int(r[2]), int(r[3])), (255, 0, 0), 2)
    cv2.imshow('img', ori_img)
    cv2.waitKey()


def detect(pic_dir, model_1_or_2=1, file_or_pic='file'):
    if model_1_or_2 == 1:
        if file_or_pic == 'file':
            return detection1(pic_dir, './model/pretrain.pth')
        elif file_or_pic == 'pic':
            return detection2(pic_dir, './model/pretrain.pth')
    elif model_1_or_2 == 2:
        if file_or_pic == 'file':
            return detection1(pic_dir, './model/last.pth')
        elif file_or_pic == 'pic':
            return detection2(pic_dir, './model/last.pth')

if __name__ == '__main__':
    root = './images'
    model_path = './model/pretrain.pth'
    # detection2(r'D:\PC_projests\test\CV_lable_tool\detection\images\timg.jpg', model_path)
    detection1(root, model_path)

