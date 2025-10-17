# main.py
import cv2
from utils.config_camara import init_camera
from utils.config import WIDTH, HEIGHT, buttonListValues
from Detector_gestos import DetectorGestos
from Button import Button
from operador import Operador  

# Inicialización
cap = init_camera()
detector = DetectorGestos()
operador = Operador()  

if not cap.isOpened():
    print("❌ La cámara no se pudo inicializar")
    exit(1)
else:
    print("✅ Cámara inicializada correctamente")

cap.set(3, WIDTH)
cap.set(4, HEIGHT)

# Crear botones
buttonlist = []
for y in range(5):
    for x in range(4):
        if y == 0 and x >= 2:
            break
        xpos = int(WIDTH - 500 + x * 100)
        ypos = int(HEIGHT * 0.15 + y * 100)
        if y == 0 and x == 1:
            xpos += 100
        width = 200 if y == 0 else 100
        buttonlist.append(Button((xpos, ypos), width, 100, buttonListValues[y][x]))

# ========== LOOP PRINCIPAL ==========
while True:
    success, img = cap.read()
    if not success:
        break

    # Detección y dibujo de gestos
    img = detector.detectar(img)
    gesto = detector.detectar_gesto(img)

    # Área de display de la operación
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

    # Procesar gesto detectado
    if gesto:
        operador.procesar(gesto)
        print(f"Gesto detectado: {gesto} → {operador.obtener_operacion()}")
        cv2.putText(img, f"Gesto: {gesto}", (50, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    # Mostrar operación o resultado
    cv2.putText(img, operador.obtener_operacion(), (operation_x + 10, operation_y + 75),
                cv2.FONT_HERSHEY_PLAIN, 3, (50, 50, 50), 3)

    # Mostrar cámara
    cv2.imshow('Calculadora Gestual', img)

    # Salir con 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
