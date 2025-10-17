# main.py
import cv2
from utils.config_camara import init_camera
from utils.config import WIDTH, HEIGHT, buttonListValues
from Detector_gestos import DetectorGestos
from Button import Button

cap = init_camera()
detector = DetectorGestos(cooldown=1.0)

if not cap.isOpened():
    print("La cámara no se pudo inicializar")
    exit(1)
else:
    print("Cámara inicializada correctamente")

cap.set(3, WIDTH)
cap.set(4, HEIGHT)

buttonlist = []
for y in range(5):
    for x in range(4):
        if y == 0 and x >= 2:
            break
        xpos = int(WIDTH - 500 + x * 100)
        ypos = int(HEIGHT * 0.15 + y * 100)
        if y == 0 and x == 1:
            xpos += 100
        if y == 0:
            width = 200
        else:
            width = 100
        buttonlist.append(Button((xpos, ypos), width, 100, buttonListValues[y][x]))

operation = ""

# ========== LOOP PRINCIPAL ==========
while True:
    success, img = cap.read()
    if not success:
        break

    # Detección y dibujo
    img = detector.detectar(img)
    gesto = detector.detectar_gesto(img)

    # Calcular posición y área del display
    operation_x = int(WIDTH - 500)
    operation_y = int(HEIGHT * 0.05)
    cv2.rectangle(img, (operation_x, operation_y),
                  (operation_x + 400, operation_y + 120),
                  (225, 225, 225), cv2.FILLED)
    cv2.rectangle(img, (operation_x, operation_y),
                  (operation_x + 400, operation_y + 120),
                  (50, 50, 50), 3)

    # Dibujar botones
    for button in buttonlist:
        button.draw(img)

    # Mostrar gesto detectado
    if gesto:
        cv2.putText(img, f"Gesto: {gesto}", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        if gesto == "C":
            operation = ""
        elif gesto == "=":
            try:
                operation = str(eval(operation))
            except:
                operation = "Error"
        elif gesto.isdigit():
            operation += gesto

    # Mostrar operación en display
    cv2.putText(img, operation, (operation_x + 10, operation_y + 75),
                cv2.FONT_HERSHEY_PLAIN, 3, (50, 50, 50), 3)

    # Mostrar cámara
    cv2.imshow('Calculadora Gestual', img)

    # Salir con 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
