import numpy as np
import cv2
import open3d as o3d
import pyrealsense2 as rs

# Device name
def get_device_name(profile):
    device = profile.get_device()
    device_name = device.get_info(rs.camera_info.name)
    return device_name

# Calcola baseline
def get_baseline(device_name):
    if "D455F" in device_name:
        return 0.095
    return 0.05

# Calcola accuratezza
def get_accuracy(depth_image):
    Z_true = 1000
    Z_measured = np.median(depth_image[240:260, 320:340])
    accuracy_error = abs(Z_measured - Z_true)
    return float(accuracy_error)

# Calcola precisione
def get_rms_precision(depth_image):
    patch = depth_image[240:260, 320:340]
    valid_patch = patch[patch > 0]
    rms_precision = np.std(valid_patch)
    return float(rms_precision)

# Calcola fill rate
def get_fill_rate(depth_image):
    valid_pixels = np.count_nonzero(depth_image)
    total_pixels = depth_image.size
    fill_rate = (valid_pixels / total_pixels) * 100
    return float(fill_rate)

# Calcola rumore immagine
def get_image_noise(color_image):
    gray = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
    noise_rms = np.std(gray[240:260, 320:340])
    return float(noise_rms), gray

# Calcola sharpness
def get_sharpness(gray):
    gx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    grad_mag = np.sqrt(gx ** 2 + gy ** 2)
    sfn = np.var(grad_mag)
    return float(sfn)

# Calcola jitter
def get_jitter(pipeline,align):
    jitter_values = []
    for i in range(30):  # analizza 30 frame
        frames = pipeline.wait_for_frames()
        aligned = align.process(frames)
        depth = np.asanyarray(aligned.get_depth_frame().get_data())
        point_depth = depth[240, 320]
        if point_depth > 0:
            jitter_values.append(point_depth)

    jitter = np.std(jitter_values)
    return float(jitter)

# Calcola planarità
def get_planarity(depth_frame):
    pc = rs.pointcloud()
    points = pc.calculate(depth_frame)
    vtx = np.asanyarray(points.get_vertices()).view(np.float32).reshape(-1, 3)
    pcl = o3d.geometry.PointCloud()
    pcl.points = o3d.utility.Vector3dVector(vtx)
    plane_model, inliers = pcl.segment_plane(distance_threshold=0.01, ransac_n=3, num_iterations=1000)
    a, b, c, d = plane_model
    plane_error = np.mean(np.abs((vtx[inliers] @ np.array([a, b, c]) + d) / np.linalg.norm([a, b, c])))
    return float(plane_error)