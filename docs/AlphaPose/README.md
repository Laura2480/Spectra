## AlphaPose
[AlphaPose](http://www.mvig.org/research/alphapose.html) is an accurate multi-person pose estimator, which is the **first open-source system that achieves 70+ mAP (75 mAP) on COCO dataset and 80+ mAP (82.1 mAP) on MPII dataset.** 
To match poses that correspond to the same person across frames, we also provide an efficient online pose tracker called Pose Flow. It is the **first open-source online pose tracker that achieves both 60+ mAP (66.5 mAP) and 50+ MOTA (58.3 MOTA) on PoseTrack Challenge dataset.**

AlphaPose supports both Linux and **Windows!**


## Results
### Pose Estimation
Results on COCO test-dev 2015:
<center>

| Method | AP @0.5:0.95 | AP @0.5 | AP @0.75 | AP medium | AP large |
|:-------|:-----:|:-------:|:-------:|:-------:|:-------:|
| OpenPose (CMU-Pose) | 61.8 | 84.9 | 67.5 | 57.1 | 68.2 |
| Detectron (Mask R-CNN) | 67.0 | 88.0 | 73.1 | 62.2 | 75.6 |
| **AlphaPose** | **73.3** | **89.2** | **79.1** | **69.0** | **78.6** |

</center>

Results on MPII full test set:
<center>

| Method | Head | Shoulder | Elbow | Wrist | Hip | Knee | Ankle | Ave |
|:-------|:-----:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|:-------:|
| OpenPose (CMU-Pose) | 91.2 | 87.6 | 77.7 | 66.8 | 75.4 | 68.9 | 61.7 | 75.6 |
| Newell & Deng | **92.1** | 89.3 | 78.9 | 69.8 | 76.2 | 71.6 | 64.7 | 77.5 |
| **AlphaPose** | 91.3 | **90.5** | **84.0** | **76.4** | **80.3** | **79.9** | **72.4** | **82.1** |

</center>

More results and models are available in the [docs/MODEL_ZOO.md](docs/MODEL_ZOO.md).

### Pose Tracking

Please read [trackers/README.md](trackers/) for details.

### CrowdPose

Please read [docs/CrowdPose.md](docs/CrowdPose.md) for details.


## Installation
Please check out [docs/INSTALL.md](docs/INSTALL.md)

## Model Zoo
Please check out [docs/MODEL_ZOO.md](docs/MODEL_ZOO.md)

- **Inference**: Inference demo
``` bash
./scripts/inference.sh ${CONFIG} ${CHECKPOINT} ${VIDEO_NAME} # ${OUTPUT_DIR}, optional
```
Inference SMPL (Download the SMPL model `basicModel_neutral_lbs_10_207_0_v1.0.0.pkl` from [here](https://smpl.is.tue.mpg.de/) and put it in `model_files/`).
``` bash
./scripts/inference_3d.sh ./configs/smpl/256x192_adam_lr1e-3-res34_smpl_24_3d_base_2x_mix.yaml ${CHECKPOINT} ${VIDEO_NAME} # ${OUTPUT_DIR}, optional
```
For high level API, please refer to `./scripts/demo_api.py`. To enable tracking, please refer to [this page](../../src/AlphaPose/trackers).

- **Training**: Train from scratch
``` bash
./scripts/train.sh ${CONFIG} ${EXP_ID}
```

- **Validation**: Validate your model on MSCOCO val2017
``` bash
./scripts/validate.sh ${CONFIG} ${CHECKPOINT}
```

Examples:

Demo using `FastPose` model.
``` bash
./scripts/inference.sh configs/coco/resnet/256x192_res50_lr1e-3_1x.yaml pretrained_models/fast_res50_256x192.pth ${VIDEO_NAME}
#or
python scripts/demo_inference.py --cfg configs/coco/resnet/256x192_res50_lr1e-3_1x.yaml --checkpoint pretrained_models/fast_res50_256x192.pth --indir examples/demo/
#or if you want to use yolox-x as the detector
python scripts/demo_inference.py --detector yolox-x --cfg configs/coco/resnet/256x192_res50_lr1e-3_1x.yaml --checkpoint pretrained_models/fast_res50_256x192.pth --indir examples/demo/
```
More detailed inference options and examples, please refer to [GETTING_STARTED.md](docs/GETTING_STARTED.md)
