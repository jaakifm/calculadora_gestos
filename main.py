from utils.config_camara import init_camera
import cv2
from utils.config import WIDTH, HEIGHT, buttonListValues
from sample_main import Button
from Detector_gestos import Detector_gestos

cap = init_camera()
detecor_gestos = Detector_gestos()

if not cap.isOpened():
    print("LA camara no se pudo inicializar")
    exit(1)
else:
    print("Camara inicializada correctamente")

cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

print("Video capture started at {}x{}".format(
    int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
    int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
))

# main
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to read frame")
        break

    # detectar gestos
    frame = detecor_gestos.detectar(frame)
    gesto = detecor_gestos.asignar_gesto_detectado(frame)

    if gesto:
        print(f"Gesto detectado: {gesto}")

    # dibujar botones


    cv2.imshow("Calculadora por gestos", frame)

    # Escape
    if cv2.waitKey(1) & 0xFF == 27:
        break

