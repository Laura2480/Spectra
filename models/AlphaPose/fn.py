import torch
import re
import os
import collections
import cv2
from opt import opt
from tqdm import tqdm
import time
import matplotlib.pyplot as plt
from PIL import Image
import numpy as np
import math
import copy

RED = (0, 0, 255)
GREEN = (0, 255, 0)
BLUE = (255, 0, 0)
CYAN = (255, 255, 0)
YELLOW = (0, 255, 255)
ORANGE = (0, 165, 255)
PURPLE = (255, 0, 255)

numpy_type_map = {
    'float64': torch.DoubleTensor,
    'float32': torch.FloatTensor,
    'float16': torch.HalfTensor,
    'int64': torch.LongTensor,
    'int32': torch.IntTensor,
    'int16': torch.ShortTensor,
    'int8': torch.CharTensor,
    'uint8': torch.ByteTensor,
}

_use_shared_memory = True

def coco2h36m2D(x):
    '''
        Input: x (J,2)
        
        COCO: {0-nose 1-Leye 2-Reye 3-Lear 4Rear 5-Lsho 6-Rsho 7-Lelb 8-Relb 9-Lwri 10-Rwri 11-Lhip 12-Rhip 13-Lkne 14-Rkne 15-Lank 16-Rank}
        
        H36M:
        0: 'root',
        1: 'rhip',
        2: 'rkne',
        3: 'rank',
        4: 'lhip',
        5: 'lkne',
        6: 'lank',
        7: 'belly',
        8: 'neck',
        9: 'nose',
        10: 'head',
        11: 'lsho',
        12: 'lelb',
        13: 'lwri',
        14: 'rsho',
        15: 'relb',
        16: 'rwri'
    '''
    y = np.zeros(x.shape)
    y[0,:] = (x[11,:] + x[12,:]) * 0.5
    y[1,:] = x[12,:]
    y[2,:] = x[14,:]
    y[3,:] = x[16,:]
    y[4,:] = x[11,:]
    y[5,:] = x[13,:]
    y[6,:] = x[15,:]
    y[8,:] = (x[5,:] + x[6,:]) * 0.5
    y[7,:] = (y[0,:] + y[8,:]) * 0.5
    y[9,:] = x[0,:]
    y[10,:] = (x[1,:] + x[2,:]) * 0.5
    y[11,:] = x[5,:]
    y[12,:] = x[7,:]
    y[13,:] = x[9,:]
    y[14,:] = x[6,:]
    y[15,:] = x[8,:]
    y[16,:] = x[10,:]
    return y

def collate_fn(batch):
    r"""Puts each data field into a tensor with outer dimension batch size"""

    error_msg = "batch must contain tensors, numbers, dicts or lists; found {}"
    elem_type = type(batch[0])

    if isinstance(batch[0], torch.Tensor):
        out = None
        if _use_shared_memory:
            # If we're in a background process, concatenate directly into a
            # shared memory tensor to avoid an extra copy
            numel = sum([x.numel() for x in batch])
            storage = batch[0].storage()._new_shared(numel)
            out = batch[0].new(storage)
        return torch.stack(batch, 0, out=out)
    elif elem_type.__module__ == 'numpy' and elem_type.__name__ != 'str_' \
            and elem_type.__name__ != 'string_':
        elem = batch[0]
        if elem_type.__name__ == 'ndarray':
            # array of string classes and object
            if re.search('[SaUO]', elem.dtype.str) is not None:
                raise TypeError(error_msg.format(elem.dtype))

            return torch.stack([torch.from_numpy(b) for b in batch], 0)
        if elem.shape == ():  # scalars
            py_type = float if elem.dtype.name.startswith('float') else int
            return numpy_type_map[elem.dtype.name](list(map(py_type, batch)))
    elif isinstance(batch[0], int_classes):
        return torch.LongTensor(batch)
    elif isinstance(batch[0], float):
        return torch.DoubleTensor(batch)
    elif isinstance(batch[0], string_classes):
        return batch
    elif isinstance(batch[0], collections.Mapping):
        return {key: collate_fn([d[key] for d in batch]) for key in batch[0]}
    elif isinstance(batch[0], collections.Sequence):
        transposed = zip(*batch)
        return [collate_fn(samples) for samples in transposed]

    raise TypeError((error_msg.format(type(batch[0]))))


def collate_fn_list(batch):
    img, inp, im_name = zip(*batch)
    img = collate_fn(img)
    im_name = collate_fn(im_name)

    return img, inp, im_name


def vis_frame_fast(frame, im_res, format='coco'):
    '''
    frame: frame image
    im_res: im_res of predictions
    format: coco or mpii

    return rendered image
    '''
    if format == 'coco':
        l_pair = [
            (0, 1), (0, 2), (1, 3), (2, 4),  # Head
            (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),
            (17, 11), (17, 12),  # Body
            (11, 13), (12, 14), (13, 15), (14, 16)
        ]
        p_color = [(0, 255, 255), (0, 191, 255),(0, 255, 102),(0, 77, 255), (0, 255, 0), #Nose, LEye, REye, LEar, REar
                    (77,255,255), (77, 255, 204), (77,204,255), (191, 255, 77), (77,191,255), (191, 255, 77), #LShoulder, RShoulder, LElbow, RElbow, LWrist, RWrist
                    (204,77,255), (77,255,204), (191,77,255), (77,255,191), (127,77,255), (77,255,127), (0, 255, 255)] #LHip, RHip, LKnee, Rknee, LAnkle, RAnkle, Neck
        line_color = [(0, 215, 255), (0, 255, 204), (0, 134, 255), (0, 255, 50), 
                    (77,255,222), (77,196,255), (77,135,255), (191,255,77), (77,255,77), 
                    (77,222,255), (255,156,127), 
                    (0,127,255), (255,127,77), (0,77,255), (255,77,36)]
    elif format == 'mpii':
        l_pair = [
            (8, 9), (11, 12), (11, 10), (2, 1), (1, 0),
            (13, 14), (14, 15), (3, 4), (4, 5),
            (8, 7), (7, 6), (6, 2), (6, 3), (8, 12), (8, 13)
        ]
        p_color = [PURPLE, BLUE, BLUE, RED, RED, BLUE, BLUE, RED, RED, PURPLE, PURPLE, PURPLE, RED, RED,BLUE,BLUE]
    else:
        NotImplementedError

    im_name = im_res['imgname'].split('/')[-1]
    img = frame
    for human in im_res['result']:
        part_line = {}
        kp_preds = human['keypoints']
        kp_scores = human['kp_score']
        kp_preds = torch.cat((kp_preds, torch.unsqueeze((kp_preds[5,:]+kp_preds[6,:])/2,0)))
        kp_scores = torch.cat((kp_scores, torch.unsqueeze((kp_scores[5,:]+kp_scores[6,:])/2,0)))
        # Draw keypoints
        for n in range(kp_scores.shape[0]):
            if kp_scores[n] <= 0.05:
                continue
            cor_x, cor_y = int(kp_preds[n, 0]), int(kp_preds[n, 1])
            part_line[n] = (cor_x, cor_y)
            cv2.circle(img, (cor_x, cor_y), 4, p_color[n], -1)
        # Draw limbs
        for i, (start_p, end_p) in enumerate(l_pair):
            if start_p in part_line and end_p in part_line:
                start_xy = part_line[start_p]
                end_xy = part_line[end_p]
                cv2.line(img, start_xy, end_xy, line_color[i], 2*int(kp_scores[start_p] + kp_scores[end_p]) + 1)
    return img


def vis_frame(frame, im_res,convertH36=False, format='coco',):
    '''
    frame: frame image
    im_res: im_res of predictions
    format: coco or mpii

    return rendered image
    '''
    if format == 'coco':
        l_pair = [
            (0, 1), (0, 2), (1, 3), (2, 4),  # Head
            (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),
            (17, 11), (17, 12),  # Body
            (11, 13), (12, 14), (13, 15), (14, 16)
        ]

        p_color = [(0, 255, 255), (0, 191, 255),(0, 255, 102),(0, 77, 255), (0, 255, 0), #Nose, LEye, REye, LEar, REar
                    (77,255,255), (77, 255, 204), (77,204,255), (191, 255, 77), (77,191,255), (191, 255, 77), #LShoulder, RShoulder, LElbow, RElbow, LWrist, RWrist
                    (204,77,255), (77,255,204), (191,77,255), (77,255,191), (127,77,255), (77,255,127), (0, 255, 255)] #LHip, RHip, LKnee, Rknee, LAnkle, RAnkle, Neck
        line_color = [(0, 215, 255), (0, 255, 204), (0, 134, 255), (0, 255, 50), 
                    (77,255,222), (77,196,255), (77,135,255), (191,255,77), (77,255,77), 
                    (77,222,255), (255,156,127), 
                    (0,127,255), (255,127,77), (0,77,255), (255,77,36)]

        l_pair_h36 = [
               [0, 1], #right hip
               [1, 2], [2, 3], #right leg
               [0, 4], #left hip
               [4, 5], [5, 6], #left leg
               [0, 7], [7, 8],#torso
               [8, 9], # lower head
               [8, 11], [8, 14], #shoulders
               [9, 10], #top head
               [11, 12], [12, 13], #left arm
               [14, 15], [15, 16] #right arm
               ]

        line_color_h36 = [
                      (255,156,127), #right hip -
                      (255,127,77), (255,77,36), #right leg -
                      (77,222,255), #left hip
                      (0,127,255),  (0,77,255), #left leg -
                      (0, 215, 255), (0, 255, 204), #torso
                      (77,255,222), #lower head -
                      (0, 134, 255), (0, 255, 50), #shoulders -
                      (91,252,235), #top head
                      (77,135,255),(77,196,255), #left arm
                      (77,255,77),(191,255,77) #right arm
                      ]

        p_color_h36=[
                (255,156,127),
                (255,127,77),
                (255,77,36),
                (255,77,36),
                (0,127,255),
                (0,77,255),
                (0,77,255),
                (0, 255, 204),
                (0, 194, 152),
                (91,252,235),
                (77,255,222),
                (77,135,255),
                (77,196,255),
                (77,196,255),
                (191,255,77),
                (77,255,77),
                (77,255,77)
                ]

    elif format == 'mpii':
        l_pair = [
            (8, 9), (11, 12), (11, 10), (2, 1), (1, 0),
            (13, 14), (14, 15), (3, 4), (4, 5),
            (8, 7), (7, 6), (6, 2), (6, 3), (8, 12), (8, 13)
        ]
        p_color = [PURPLE, BLUE, BLUE, RED, RED, BLUE, BLUE, RED, RED, PURPLE, PURPLE, PURPLE, RED, RED, BLUE, BLUE]
        line_color = [PURPLE, BLUE, BLUE, RED, RED, BLUE, BLUE, RED, RED, PURPLE, PURPLE, RED, RED, BLUE, BLUE]
    else:
        raise NotImplementedError

    im_name = im_res['imgname'].split('/')[-1]
    img = frame
    height,width = img.shape[:2]
    img = cv2.resize(img,(int(width/2), int(height/2)))
    for human in im_res['result']:
        part_line = {}
        kp_preds = human['keypoints']
        kp_scores = human['kp_score']
        kp_preds = torch.cat((kp_preds, torch.unsqueeze((kp_preds[5,:]+kp_preds[6,:])/2,0)))
        kp_scores = torch.cat((kp_scores, torch.unsqueeze((kp_scores[5,:]+kp_scores[6,:])/2,0)))
        kp_preds_processed=process_kps(kp_preds,height,width)
        human['keypoints_normalized']=kp_preds_processed
        if convertH36:
          kp_preds=coco2h36m2D(kp_preds)
          nose_x, nose_y = int(kp_preds[8, 0]), int(kp_preds[8, 1])
          neck_x, neck_y = int(kp_preds[9, 0]), int(kp_preds[9, 1])
          radius = math.sqrt((neck_x - nose_x)**2 + (neck_y - nose_y)**2)

          blur_circle_on_image(img, (nose_x, nose_y), radius, 39)
        # Draw keypoints
        for n in range(kp_scores.shape[0]):
            if kp_scores[n] <= 0.05:
                continue
            cor_x, cor_y = int(kp_preds[n, 0]), int(kp_preds[n, 1])
            part_line[n] = (int(cor_x/2), int(cor_y/2))
            bg = img.copy()
            if convertH36:
              cv2.circle(bg, (int(cor_x/2), int(cor_y/2)), 2, p_color_h36[n], -1)
            else:
              cv2.circle(bg, (int(cor_x/2), int(cor_y/2)), 2, p_color[n], -1)
            # Now create a mask of logo and create its inverse mask also
            transparency = float(max(0, min(1, kp_scores[n])))
            img = cv2.addWeighted(bg, transparency, img, 1-transparency, 0)
        # Draw limbs
        for i, (start_p, end_p) in enumerate(l_pair):
            if start_p in part_line and end_p in part_line:
                start_xy = part_line[start_p]
                end_xy = part_line[end_p]
                bg = img.copy()

                X = (start_xy[0], end_xy[0])
                Y = (start_xy[1], end_xy[1])
                mX = np.mean(X)
                mY = np.mean(Y)
                length = ((Y[0] - Y[1]) ** 2 + (X[0] - X[1]) ** 2) ** 0.5
                angle = math.degrees(math.atan2(Y[0] - Y[1], X[0] - X[1]))
                stickwidth = (kp_scores[start_p] + kp_scores[end_p]) + 1
                polygon = cv2.ellipse2Poly((int(mX),int(mY)), (int(length/2), int(stickwidth)), int(angle), 0, 360, 1)
                if convertH36:
                  cv2.fillConvexPoly(bg, polygon, line_color_h36[i])
                else:
                  cv2.fillConvexPoly(bg, polygon, line_color[i])
                #cv2.line(bg, start_xy, end_xy, line_color[i], (2 * (kp_scores[start_p] + kp_scores[end_p])) + 1)
                transparency = float(max(0, min(1, 0.5*(kp_scores[start_p] + kp_scores[end_p]))))
                img = cv2.addWeighted(bg, transparency, img, 1-transparency, 0)
        '''
        # Draw keypoints norm
        for n in range(kp_scores.shape[0]):
            if kp_scores[n] <= 0.05:
                continue
            cor_x, cor_y = int(kp_preds_processed[n, 0]), int(kp_preds_processed[n, 1])
            part_line[n] = (int(cor_x/2), int(cor_y/2))
            bg = img.copy()
            cv2.circle(bg, (int(cor_x/2), int(cor_y/2)), 2, BLUE, -1)
            # Now create a mask of logo and create its inverse mask also
            transparency = 0.5*(float(max(0, min(1, kp_scores[n]))))
            img = cv2.addWeighted(bg, transparency, img, 1-transparency, 0)

        # Draw limbs norm
        for i, (start_p, end_p) in enumerate(l_pair):
            if start_p in part_line and end_p in part_line:
                start_xy = part_line[start_p]
                end_xy = part_line[end_p]
                bg = img.copy()

                X = (start_xy[0], end_xy[0])
                Y = (start_xy[1], end_xy[1])
                mX = np.mean(X)
                mY = np.mean(Y)
                length = ((Y[0] - Y[1]) ** 2 + (X[0] - X[1]) ** 2) ** 0.5
                angle = math.degrees(math.atan2(Y[0] - Y[1], X[0] - X[1]))
                stickwidth = (kp_scores[start_p] + kp_scores[end_p]) + 1
                polygon = cv2.ellipse2Poly((int(mX),int(mY)), (int(length/2), int(stickwidth)), int(angle), 0, 360, 1)
                cv2.fillConvexPoly(bg, polygon, BLUE)
                #cv2.line(bg, start_xy, end_xy, line_color[i], (2 * (kp_scores[start_p] + kp_scores[end_p])) + 1)
                transparency = 0.5*(float(max(0, min(1, 0.5*(kp_scores[start_p] + kp_scores[end_p])))))
                img = cv2.addWeighted(bg, transparency, img, 1-transparency, 0)
        '''
    img = cv2.resize(img,(width,height),interpolation=cv2.INTER_CUBIC)
    return img


def getTime(time1=0):
    if not time1:
        return time.time()
    else:
        interval = time.time() - time1
        return time.time(), interval

def process_kps( kps,  height,width):
    
    bbox=get_box(kps)
    
    
    centro_frame_x, centro_frame_y = width / 2, height / 2

    x_min, x_max,y_min, y_max = bbox
        
    # Calcolo del centro del bounding box
    centro_box_x = (x_min + x_max) / 2
    centro_box_y = (y_min + y_max) / 2
    '''
    print(f"largezza {width}")
    print(f"altezza {height}")
    print(f" box centro x {centro_box_x}")
    print(f" box centro y {centro_box_y}")
    '''
    # Calcolo del fattore di scala basato sull'altezza fissa
    fattore_scala = 0.9*height / (y_max - y_min)
    
    kps_processed=kps.clone()
    kps_processed[:, 0] =  (kps[:, 0] - centro_box_x) * fattore_scala + centro_frame_x
    kps_processed[:, 1] =  (kps[:, 1] - centro_box_y) * fattore_scala + centro_frame_y
    
    return kps_processed


def get_box(kp):
    xmin = kp[:, 0].min()
    xmax = kp[:, 0].max()
    ymin = kp[:, 1].min()
    ymax = kp[:, 1].max()
    #print(f"le cordinate del box :\n x_min={xmin}\n x_max={xmax}\n y_min={ymin}\n y_max={ymax}")
    #return expand_bbox(xmin, xmax, ymin, ymax, img_width, img_height)
    return [xmin, xmax, ymin, ymax]

def blur_circle_on_image(img, center, radius, blur_value):
    # Load the original image
    
    # Create a mask with the same dimensions as the image, initially all zeros (black)
    mask = np.zeros_like(img)
    
    # Fill a circle in the mask with white (255) at the specified center and radius
    cv2.circle(mask, center, radius, (255, 255, 255), thickness=-1)
    
    
    # Convert mask to grayscale (needed for the next steps)
    mask_gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to the original image
    blurred_img = cv2.GaussianBlur(img, (blur_value, blur_value), 0)
    
    
    # Combine the original and blurred images according to the mask
    result = np.where(mask_gray[:,:,None] == 255, blurred_img, img)
    return result
    # Convert BGR to RGB
    #img_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)


