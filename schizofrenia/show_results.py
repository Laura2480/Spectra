import sys
from pathlib import Path

import cv2
import json
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import animation

# Definisci le connessioni tra i keypoints in MediaPipe
POSE_CONNECTIONS = [(0, 1),(1, 2),(2, 3),(0, 4),(4, 5),(5, 6),(1, 7),(4, 8),(9, 10),(11, 12),(11, 13),
    (13, 15),(12, 14),(14, 16),(11, 23),(12, 24),(23, 24),(23, 25),(25, 27),(24, 26),(26, 28),(27, 29),
    (29, 31),(27, 31),(28, 30),(30, 32),(28, 32)]

# Recupera i dati da un file .json
def load_keypoints_from_json(filename):
    """Carica i keypoints da un file JSON."""
    with open(filename, 'r') as f:
        results = json.load(f)
    return results

# Disegna lo scheletro della persona nella finestra
def draw_keypoints_on_image(keypoints, width=500, height=500):
    """Disegna i keypoints su un'immagine vuota e le connessioni tra di essi."""
    # Crea un'immagine bianca come sfondo
    image = np.ones((height, width, 3), dtype=np.uint8) * 255

    # Disegna i keypoints
    for keypoint in keypoints:
        x, y = int(keypoint[0] * width), int(keypoint[1] * height)
        cv2.circle(image, (x, y), 5, (0, 0, 255), -1)

    # Disegna le connessioni tra i keypoints
    for connection in POSE_CONNECTIONS:
        p1, p2 = connection
        if p1 < len(keypoints) and p2 < len(keypoints):
            x1, y1 = int(keypoints[p1][0] * width), int(keypoints[p1][1] * height)
            x2, y2 = int(keypoints[p2][0] * width), int(keypoints[p2][1] * height)
            cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), 2)

    return image

def draw_keypoints_on_image_3d(keypoints, width=500, height=500, depth=500):
    """Disegna i keypoints su un'immagine vuota e le connessioni tra di essi."""
    # Crea un'immagine bianca come sfondo
    image = np.ones((height, width, depth), dtype=np.uint8) * 255

    # Disegna i keypoints
    for keypoint in keypoints:
        x, y, z = int(keypoint[0] * width), int(keypoint[1] * height), int(keypoint[2] * depth)
        cv2.circle(image, (x, y, z), 5, (0, 0, 255), -1)

    # Disegna le connessioni tra i keypoints
    for connection in POSE_CONNECTIONS:
        p1, p2 = connection
        if p1 < len(keypoints) and p2 < len(keypoints):
            x1, y1 = int(keypoints[p1][0] * width), int(keypoints[p1][1] * height)
            x2, y2 = int(keypoints[p2][0] * width), int(keypoints[p2][1] * height)
            cv2.line(image, (x1, y1), (x2, y2), (255, 0, 0), 2)

    return image


def draw_keypoints_on_3d_ax(ax, keypoints, xlim, ylim, zlim):
    xs, ys, zs = zip(*keypoints)
    ax.scatter(xs, ys, zs, c='r', marker='o')

    for p1, p2 in POSE_CONNECTIONS:
        if p1 < len(keypoints) and p2 < len(keypoints):
            x = [keypoints[p1][0], keypoints[p2][0]]
            y = [keypoints[p1][1], keypoints[p2][1]]
            z = [keypoints[p1][2], keypoints[p2][2]]
            ax.plot(x, y, z, c='b')

    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_zlim(*zlim)
    ax.invert_zaxis()  # Se z è invertito
    ax.invert_xaxis()
    ax.view_init(elev=90, azim=90)  # regola angolo di vista
    ax.set_title("Pose 3D Frame")

def main():
    if len(sys.argv) < 2:
        path = "results/6_riprese_18_01_2025/PAZIENTE 2/videos_results"
        filename = "20250118_121807.json"
    else:
        full_path = Path(sys.argv[1])
        path = full_path.parent.as_posix()
        filename = full_path.name

    keypoints_data = load_keypoints_from_json(path + '/' + filename)
    frames = keypoints_data['frames']

    # Calcola limiti globali per mantenere l'inquadratura fissa
    all_keypoints = np.array([pt for frame in frames for pt in frame])
    x_min, x_max = all_keypoints[:, 0].min(), all_keypoints[:, 0].max()
    y_min, y_max = all_keypoints[:, 1].min(), all_keypoints[:, 1].max()
    z_min, z_max = all_keypoints[:, 2].min(), all_keypoints[:, 2].max()

    padding = 0.1
    x_range = x_max - x_min
    y_range = y_max - y_min
    z_range = z_max - z_min

    x_min_pad = x_min - x_range * padding
    x_max_pad = x_max + x_range * padding
    y_min_pad = y_min - y_range * padding
    y_max_pad = y_max + y_range * padding
    z_min_pad = z_min - z_range * padding
    z_max_pad = z_max + z_range * padding

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    def update(frame_idx):
        ax.clear()
        draw_keypoints_on_3d_ax(ax, frames[frame_idx],
                                xlim=(x_min_pad, x_max_pad),
                                ylim=(y_min_pad, y_max_pad),
                                zlim=(z_min_pad, z_max_pad))

    # Calcola l'intervallo per 60 fps
    interval = 1000 / 60  # 16.67 ms per frame

    ani = animation.FuncAnimation(fig, update, frames=len(frames), interval=interval)

    # Salva l'animazione come video
    ani.save(path + filename[:-4] + ".mp4", writer='ffmpeg', fps=60)

    # Mostra l'animazione
    plt.show()

if __name__ == "__main__":
    main()
