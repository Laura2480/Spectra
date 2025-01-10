import torch
import numpy as np
import ipdb
import glob
import os
import io
import math
import random
import json
import pickle
import math
from torch.utils.data import Dataset, DataLoader
from lib.utils.utils_data import crop_scale

def coco2h36m(x):
    '''
        Input: x ( T x V x C)
        
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
    y[:,0,:] = (x[:,11,:] + x[:,12,:]) * 0.5
    y[:,1,:] = x[:,12,:]
    y[:,2,:] = x[:,14,:]
    y[:,3,:] = x[:,16,:]
    y[:,4,:] = x[:,11,:]
    y[:,5,:] = x[:,13,:]
    y[:,6,:] = x[:,15,:]
    y[:,8,:] = (x[:,5,:] + x[:,6,:]) * 0.5
    y[:,7,:] = (y[:,0,:] + y[:,8,:]) * 0.5
    y[:,9,:] = x[:,0,:]
    y[:,10,:] = (x[:,1,:] + x[:,2,:]) * 0.5
    y[:,11,:] = x[:,5,:]
    y[:,12,:] = x[:,7,:]
    y[:,13,:] = x[:,9,:]
    y[:,14,:] = x[:,6,:]
    y[:,15,:] = x[:,8,:]
    y[:,16,:] = x[:,10,:]
    return y

def halpe2h36m(x):
    '''
        Input: x (T x V x C)  
       //Halpe 26 body keypoints
    {0,  "Nose"},
    {1,  "LEye"},
    {2,  "REye"},
    {3,  "LEar"},
    {4,  "REar"},
    {5,  "LShoulder"},
    {6,  "RShoulder"},
    {7,  "LElbow"},
    {8,  "RElbow"},
    {9,  "LWrist"},
    {10, "RWrist"},
    {11, "LHip"},
    {12, "RHip"},
    {13, "LKnee"},
    {14, "Rknee"},
    {15, "LAnkle"},
    {16, "RAnkle"},
    {17,  "Head"},
    {18,  "Neck"},
    {19,  "Hip"},
    {20, "LBigToe"},
    {21, "RBigToe"},
    {22, "LSmallToe"},
    {23, "RSmallToe"},
    {24, "LHeel"},
    {25, "RHeel"},
    '''
    T, V, C = x.shape
    y = np.zeros([T,17,C])
    y[:,0,:] = x[:,19,:]
    y[:,1,:] = x[:,12,:]
    y[:,2,:] = x[:,14,:]
    y[:,3,:] = x[:,16,:]
    y[:,4,:] = x[:,11,:]
    y[:,5,:] = x[:,13,:]
    y[:,6,:] = x[:,15,:]
    y[:,7,:] = (x[:,18,:] + x[:,19,:]) * 0.5
    y[:,8,:] = x[:,18,:]
    y[:,9,:] = x[:,0,:]
    y[:,10,:] = x[:,17,:]
    y[:,11,:] = x[:,5,:]
    y[:,12,:] = x[:,7,:]
    y[:,13,:] = x[:,9,:]
    y[:,14,:] = x[:,6,:]
    y[:,15,:] = x[:,8,:]
    y[:,16,:] = x[:,10,:]
    return y
    
def read_input(json_path, vid_size, scale_range, focus,keypoints_normalized=False):
    with open(json_path, "r") as read_file:
        results = json.load(read_file)
    kpts_all = []
    for item in results:
        if focus!=None and item['idx']!=focus:
            continue
        if keypoints_normalized:
          kpts = np.array(item['keypoints_normalized']).reshape([-1,3])
        else:
          kpts = np.array(item['keypoints']).reshape([-1,3])
        kpts_all.append(kpts)
    kpts_all = np.array(kpts_all)
    if (kpts_all.shape[1]==17):
      kpts_all = coco2h36m(kpts_all)
    else:
      kpts_all = halpe2h36m(kpts_all)

    if vid_size:
        w, h = vid_size
        scale = min(w,h) / 2.0
        kpts_all[:,:,:2] = kpts_all[:,:,:2] - np.array([w, h]) / 2.0
        kpts_all[:,:,:2] = kpts_all[:,:,:2] / scale
        motion = kpts_all
    if scale_range:
        motion = crop_scale(kpts_all, scale_range) 
    return motion.astype(np.float32)

class WildDetDataset(Dataset):
    def __init__(self, json_path, clip_len=243, vid_size=None, scale_range=None, focus=None,keypoints_normalized=False):
        self.json_path = json_path
        self.clip_len = clip_len
        self.vid_all = read_input(json_path, vid_size, scale_range, focus,keypoints_normalized=keypoints_normalized)
        
    def __len__(self):
        'Denotes the total number of samples'
        return math.ceil(len(self.vid_all) / self.clip_len)
    
    def __getitem__(self, index):
        'Generates one sample of data'
        st = index*self.clip_len
        end = min((index+1)*self.clip_len, len(self.vid_all))
        return self.vid_all[st:end]