import cv2
from utils.config import WIDTH, HEIGHT

def init_camera():
    cap = cv2.VideoCapture(0)  # Cambiar a 1 o 2 según tu dispositivo
    cap.set(3, WIDTH)
    cap.set(4, HEIGHT)
    return cap