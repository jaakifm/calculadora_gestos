import cv2
from utils.config import WIDTH, HEIGHT, INDEX_CAMARA

def init_camera():
    cap = cv2.VideoCapture(INDEX_CAMARA)  # Cambiar a 1 o 2 según tu dispositivo
    cap.set(3, WIDTH)
    cap.set(4, HEIGHT)
    return cap