# main.py
import cv2
from utils.config_camara import init_camera
from utils.config import WIDTH, HEIGHT, buttonListValues
from Detector_gestos import DetectorGestos
from Button import Button
#from boton_ayuda import mostrar_instrucciones  # <-- Ventana de ayuda

# === Inicialización cámara y detector ===
cap = init_camera()
detector = DetectorGestos()

if not cap.isOpened():
    print("❌ La cámara no se pudo inicializar")
    exit(1)
else:
    print("✅ Cámara inicializada correctamente")

cap.set(3, WIDTH)
cap.set(4, HEIGHT)

# === Crear botones de la calculadora ===
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

operation = ""
display_operation = ""

# # === Parámetros botón AYUDA ===
# ayuda_x, ayuda_y = 50, 50     # posición arriba a la izquierda (visible)
# ayuda_w, ayuda_h = 200, 60
# ayuda_color = (255, 255, 255)

# # --- Callback de clics ---
# def click_event(event, x, y, flags, param):
#     if event == cv2.EVENT_LBUTTONDOWN:
#         if ayuda_x < x < ayuda_x + ayuda_w and ayuda_y < y < ayuda_y + ayuda_h:
#             print("📘 Botón de ayuda presionado")
#             mostrar_instrucciones()

# # Asociar callback al nombre de la ventana
# cv2.namedWindow('Calculadora Gestual')
# cv2.setMouseCallback('Calculadora Gestual', click_event)

# === LOOP PRINCIPAL ===
while True:
    success, img = cap.read()
    if not success:
        break

    # Dibujar landmarks de las manos
    img = detector.detectar(img)
    gesto = detector.detectar_gesto(img)

    # === Rectángulo del área de operación ===
    operation_x = int(WIDTH - 500)
    operation_y = int(HEIGHT * 0.05)
    cv2.rectangle(img, (operation_x, operation_y),
                  (operation_x + 400, operation_y + 120),
                  (225, 225, 225), cv2.FILLED)
    cv2.rectangle(img, (operation_x, operation_y),
                  (operation_x + 400, operation_y + 120),
                  (50, 50, 50), 3)

    # === Dibujar botones ===
    for button in buttonlist:
        button.draw(img)

    # # === Dibujar botón de ayuda (arriba a la izquierda para asegurar visibilidad) ===
    # cv2.rectangle(img, (ayuda_x, ayuda_y),
    #               (ayuda_x + ayuda_w, ayuda_y + ayuda_h),
    #               ayuda_color, cv2.FILLED)
    # cv2.rectangle(img, (ayuda_x, ayuda_y),
    #               (ayuda_x + ayuda_w, ayuda_y + ayuda_h),
    #               (0, 0, 0), 2)
    # cv2.putText(img, "Ayuda (?)", (ayuda_x + 20, ayuda_y + 40),
    #             cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

    # === Procesar gesto ===
    if gesto:
        if gesto == "C":
            operation = ""
        elif gesto == "=":
            try:
                operation = str(eval(operation))
            except:
                operation = "Error"
        elif gesto.isdigit() or gesto in ['+', '-', '*', '/', '.']:
            operation += gesto

    # Mostrar operación actual
    display_operation = operation
    cv2.putText(img, display_operation, (operation_x + 10, operation_y + 75),
                cv2.FONT_HERSHEY_PLAIN, 3, (50, 50, 50), 3)

    # === Mostrar ventana principal ===
    cv2.imshow('Calculadora Gestual', img)

    # --- Salir con Q ---
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
