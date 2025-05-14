import mediapipe as mp
import cv2
import numpy as np

# Inizializza MediaPipe Pose
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=False, min_detection_confidence=0.5, min_tracking_confidence=0.5)
WIDTH, HEIGHT, DEPTH = 500, 500, 500
total_keypoints = 33

def process_pose(image):
    """Elabora il frame con MediaPipe e disegna i keypoints"""
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_image)

    if results.pose_landmarks:
        mp.solutions.drawing_utils.draw_landmarks(
            image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
        )

    return image


def process_pose_2d(image):
    """Elabora il frame con MediaPipe e disegna i keypoints"""
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_image)
    keypoints = None

    if results.pose_landmarks:
        keypoints = [(lm.x, lm.y) for lm in results.pose_landmarks.landmark]

    return keypoints


def draw_pose_on_grid(keypoints):
    """Disegna la posa su un piano cartesiano in OpenCV"""
    # Crea un'immagine nera come piano cartesiano
    canvas = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8) * 255  # Sfondo bianco

    # Disegna il piano cartesiano
    cv2.line(canvas, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), (0, 0, 0), 1)  # Asse Y
    cv2.line(canvas, (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), (0, 0, 0), 1)  # Asse X

    if keypoints:
        # Converte i keypoints normalizzati in coordinate pixel
        points = [(int(x * WIDTH), int(y * HEIGHT)) for x, y in keypoints]

        # Disegna i punti
        for x, y in points:
            cv2.circle(canvas, (x, y), 5, (0, 0, 255), -1)

        # Disegna le connessioni tra i keypoints
        for connection in mp_pose.POSE_CONNECTIONS:
            p1, p2 = connection
            if p1 < len(points) and p2 < len(points):
                cv2.line(canvas, points[p1], points[p2], (255, 0, 0), 2)

    return canvas

def draw_pose_on_grid_3d(keypoints):
    """Disegna la posa su un piano cartesiano in OpenCV"""
    # Crea un'immagine nera come piano cartesiano
    canvas = np.ones((HEIGHT, WIDTH, DEPTH), dtype=np.uint8) * 255  # Sfondo bianco

    # Disegna il piano cartesiano
    cv2.line(canvas, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), (0, 0, 0), 1)  # Asse Y
    cv2.line(canvas, (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), (0, 0, 0), 1)  # Asse X

    if keypoints:
        # Converte i keypoints normalizzati in coordinate pixel
        points = [(int(x * WIDTH), int(y * HEIGHT)) for x, y in keypoints]

        # Disegna i punti
        for x, y, z in points:
            cv2.circle(canvas, (x, y, z), 5, (0, 0, 255), -1)

        # Disegna le connessioni tra i keypoints
        for connection in mp_pose.POSE_CONNECTIONS:
            p1, p2 = connection
            if p1 < len(points) and p2 < len(points):
                cv2.line(canvas, points[p1], points[p2], (255, 0, 0), 2)

    return canvas


def process_pose_3d(image, depth_frame):
    """Elabora il frame con MediaPipe e restituisce i keypoints 2D con profondità."""
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_image)
    keypoints = None

    if results.pose_landmarks:
        keypoints = [(lm.x, lm.y, lm.z) for lm in results.pose_landmarks.landmark]

    return keypoints


def draw_pose_on_grid_with_depth(keypoints):
    """Disegna la posa su un piano cartesiano OpenCV con informazioni di profondità."""
    canvas = np.ones((HEIGHT, WIDTH, 3), dtype=np.uint8) * 255  # Sfondo bianco

    # Disegna il piano cartesiano
    cv2.line(canvas, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), (0, 0, 0), 1)  # Asse Y
    cv2.line(canvas, (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), (0, 0, 0), 1)  # Asse X

    if keypoints:
        min_depth = min(kp[2] for kp in keypoints if kp[2] > 0)
        max_depth = max(kp[2] for kp in keypoints if kp[2] > 0)

        for x, y, depth in keypoints:
            # Normalizza il colore in base alla profondità
            if depth > 0:
                color = (0, 0, int(255 * (depth - min_depth) / (
                            max_depth - min_depth)))  # Blu più intenso per profondità maggiori
            else:
                color = (0, 0, 255)  # Rosso se non disponibile

            cv2.circle(canvas, (x, y), 5, color, -1)

        # Disegna le connessioni tra i keypoints
        for connection in mp_pose.POSE_CONNECTIONS:
            p1, p2 = connection
            if p1 < len(keypoints) and p2 < len(keypoints):
                cv2.line(canvas, (keypoints[p1][0], keypoints[p1][1]), (keypoints[p2][0], keypoints[p2][1]),
                         (255, 0, 0), 2)

    return canvas

def has_sufficient_keypoints(keypoints):
    """Verifica se ci sono almeno metà + 1 dei keypoints visibili."""
    if keypoints is None:
        return False  # Se keypoints è None, non ci sono punti visibili
    return len(keypoints) >= (total_keypoints // 2) + 1
