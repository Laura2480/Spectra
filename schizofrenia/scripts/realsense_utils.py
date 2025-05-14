from scripts.quality_measure_utils import *

EXPECTED_FRAME_INTERVAL = 1 / 60

def setup_realsense(bag_file):
    """Inizializza il dispositivo RealSense dal file .bag"""
    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(str(bag_file), repeat_playback=False)
    profile = pipeline.start(config)

    playback = profile.get_device().as_playback()
    playback.set_real_time(False)

    return pipeline,playback, profile

def get_frames(pipeline, playback):
    """Ottiene il frame dalla pipeline"""
    frames = pipeline.wait_for_frames()

    # Se non ci sono frame e la riproduzione è terminata, restituisci None
    if not frames or playback.current_status() == rs.playback_status.stopped:
        return None, None, None

    color_frame = frames.get_color_frame()
    depth_frame = frames.get_depth_frame()

    if not color_frame:
        return None, None, None

    current_timestamp = color_frame.get_timestamp() / 1000
    return np.asanyarray(color_frame.get_data()), np.asanyarray(depth_frame.get_data()), current_timestamp

def check_frame_loss(previous_timestamp, current_timestamp, threshold_factor=1.5):
    """Verifica se il tempo tra due frame consecutivi è troppo lungo."""
    if previous_timestamp is not None:
        frame_interval = current_timestamp - previous_timestamp
        if frame_interval > EXPECTED_FRAME_INTERVAL * threshold_factor:
            return True
    return False

def stop_realsense(pipeline):
    """Ferma la pipeline di RealSense"""
    pipeline.stop()


def get_aligned_frames(pipeline):
    align_to = rs.stream.color
    align = rs.align(align_to)

    frames = pipeline.wait_for_frames()
    aligned_frames = align.process(frames)
    depth_frame = aligned_frames.get_depth_frame()
    color_frame = aligned_frames.get_color_frame()
    return np.asanyarray(color_frame.get_data()), np.asanyarray(depth_frame.get_data()), align, depth_frame

def assessment_quality(bag_file):
    pipeline, playback, profile = setup_realsense(bag_file)
    color_image, depth_image, align, depth_frame = get_aligned_frames(pipeline)

    # Rileva modello camera e imposta baseline
    device_name = get_device_name(profile)
    baseline = get_baseline(device_name)

    # ACCURATEZZA
    accuracy_error = get_accuracy(depth_image)

    # PRECISIONE
    rms_precision = get_rms_precision(depth_image)

    # FILL RATE
    fill_rate = get_fill_rate(depth_image)

    # RUMORE IMMAGINE
    noise_rms, gray = get_image_noise(color_image)

    # SHARPNESS
    sfn = get_sharpness(gray)

    # JITTER TEMPORALE SU PUNTO FISSO
    jitter = get_jitter(pipeline,align)

    # PLANARITA'
    plane_error = get_planarity(depth_frame)

    results = {
        "camera_model": device_name,
        "baseline_m": baseline,
        "accuracy_error_mm": accuracy_error,
        "rms_precision_mm": rms_precision,
        "fill_rate_percent": fill_rate,
        "image_noise_rms": noise_rms,
        "sharpness_sfn": sfn,
        "temporal_jitter_mm": jitter,
        "planarity_error_m": plane_error
    }

    stop_realsense(pipeline)

    return results

# Funzione che processa i risultati di un video
def process_video_result(total_frames, lost_frames, invalid_keypoint_frames):
    valid_frames = total_frames - lost_frames
    keypoint_valid_frames = valid_frames - invalid_keypoint_frames

    frame_loss_pct = f"{(lost_frames / total_frames * 100):.1f}%" if total_frames else "0.0%"
    keypoint_loss_pct = f"{(invalid_keypoint_frames / keypoint_valid_frames * 100):.1f}%" if keypoint_valid_frames else "0.0%"
    lost_frames_results = {
        "total_frames": total_frames,
        "lost_frames": lost_frames,
        "invalid_keypoint_frames": invalid_keypoint_frames,
        "frame_loss_pct": frame_loss_pct,
        "keypoint_loss_pct": keypoint_loss_pct
    }
    return lost_frames_results

# Funzione che migliora la luminosità dei video
def apply_brightness_contrast(color_frame):
    lab = cv2.cvtColor(color_frame, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)

    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)

    limg = cv2.merge((cl, a, b))
    return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)