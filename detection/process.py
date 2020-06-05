import cv2
import torch
import torch.nn as nn
import numpy as np

from image import get_affine_transform, transform_preds
from tools import _tranpose_and_gather_feat, _gather_feat

mean = np.array([0.40789654, 0.44719302, 0.47026115], dtype=np.float32).reshape((1, 1, 3))
std = np.array([0.28863828, 0.27408164, 0.27809835], dtype=np.float32).reshape((1, 1, 3))

def pre_process(image):
    height, width = image.shape[0:2]
    inp_height = (height | 31) + 1
    inp_width = (width | 31) + 1
    c = np.array([width // 2, height // 2], dtype=np.float32)
    s = np.array([inp_width, inp_height], dtype=np.float32)

    trans_input = get_affine_transform(c, s, 0, [inp_width, inp_height])
    inp_image = cv2.warpAffine(image, trans_input, (inp_width, inp_height), flags=cv2.INTER_LINEAR)
    inp_image = ((inp_image / 255. - mean) / std).astype(np.float32)

    images = inp_image.transpose(2, 0, 1).reshape(1, 3, inp_height, inp_width)
    images = torch.from_numpy(images)
    meta = {'c': c, 's': s,
            'out_height': inp_height // 4,
            'out_width': inp_width // 4}
    return images, meta


def _nms(heat, kernel=3):
    pad = (kernel - 1) // 2

    hmax = nn.functional.max_pool2d(
        heat, (kernel, kernel), stride=1, padding=pad)
    keep = (hmax == heat).float()
    return heat * keep



def _topk(scores, K=40):
    batch, cat, height, width = scores.size()

    topk_scores, topk_inds = torch.topk(scores.view(batch, cat, -1), K)

    topk_inds = topk_inds % (height * width)
    topk_ys = (topk_inds / width).int().float()
    topk_xs = (topk_inds % width).int().float()

    topk_score, topk_ind = torch.topk(topk_scores.view(batch, -1), K)
    topk_clses = (topk_ind / K).int()
    topk_inds = _gather_feat(topk_inds.view(batch, -1, 1), topk_ind).view(batch, K)
    topk_ys = _gather_feat(topk_ys.view(batch, -1, 1), topk_ind).view(batch, K)
    topk_xs = _gather_feat(topk_xs.view(batch, -1, 1), topk_ind).view(batch, K)

    return topk_score, topk_inds, topk_clses, topk_ys, topk_xs


def ctdet_decode(heat, wh, reg=None, K=100):
    batch, cat, height, width = heat.size()
    # tmp = heat.cpu().detach().numpy()
    # heat = torch.sigmoid(heat)
    # perform nms on heatmaps
    heat = _nms(heat)

    scores, inds, clses, ys, xs = _topk(heat, K=K)

    reg = _tranpose_and_gather_feat(reg, inds)
    reg = reg.view(batch, K, 2)
    xs = xs.view(batch, K, 1) + reg[:, :, 0:1]
    ys = ys.view(batch, K, 1) + reg[:, :, 1:2]

    wh = _tranpose_and_gather_feat(wh, inds)

    wh = wh.view(batch, K, 2)
    clses = clses.view(batch, K, 1).float()
    scores = scores.view(batch, K, 1)
    bboxes = torch.cat([xs - wh[..., 0:1] / 2,
                        ys - wh[..., 1:2] / 2,
                        xs + wh[..., 0:1] / 2,
                        ys + wh[..., 1:2] / 2], dim=2)
    detections = torch.cat([bboxes, scores, clses], dim=2)

    return detections


def ctdet_post_process(dets, c, s, h, w, num_classes):
    ret = []
    for i in range(dets.shape[0]):
        top_preds = {}
        dets[i, :, :2] = transform_preds(dets[i, :, 0:2], c[i], s[i], (w, h))
        dets[i, :, 2:4] = transform_preds(dets[i, :, 2:4], c[i], s[i], (w, h))
        classes = dets[i, :, -1]
        for j in range(num_classes):
            inds = (classes == j)
            top_preds[j + 1] = np.concatenate([dets[i, inds, :4].astype(np.float32),
                                               dets[i, inds, 4:5].astype(np.float32)], axis=1).tolist()
            ret.append(top_preds)
    return ret


def post_process(dets, meta):
    # dets.size = (batch, K, 6)
    dets = dets.detach().cpu().numpy()
    dets = dets.reshape(1, -1, dets.shape[2])
    dets = ctdet_post_process(dets.copy(), [meta['c']], [meta['s']],
                              meta['out_height'], meta['out_width'], 1)
    dets[0][1] = np.array(dets[0][1], dtype=np.float32).reshape(-1, 5)
    dets[0][1][:, :4] /= 1
    return dets[0]


def merge_outputs(detections):
    results = {}
    results[1] = np.concatenate([detection[1] for detection in detections], axis=0).astype(np.float32)
    scores = np.hstack([results[1][:, 4]])

    thresh = 0.5
    keep_inds = (results[1][:, 4] >= thresh)
    results[1] = results[1][keep_inds]

    if len(scores) > 100:
        kth = len(scores) - 100
        thresh = np.partition(scores, kth)[kth]
        keep_inds = (results[1][:, 4] >= thresh)
        results[1] = results[1][keep_inds]
    return results
