import cv2
import mediapipe as mp
import math
import time

# ========== Clase de Botón ==========
class Button:
    def __init__(self, pos, width, height, value):
        self.pos = pos
        self.width = width
        self.height = height
        self.value = value

    def draw(self, img):
        cv2.rectangle(img, self.pos,
                      (self.pos[0] + self.width, self.pos[1] + self.height),
                      (225, 225, 225), cv2.FILLED)
        cv2.rectangle(img, self.pos,
                      (self.pos[0] + self.width, self.pos[1] + self.height),
                      (50, 50, 50), 3)
        text_x = self.pos[0] + self.width // 2 - 15
        text_y = self.pos[1] + self.height // 2 + 15
        cv2.putText(img, self.value, (text_x, text_y),
                    cv2.FONT_HERSHEY_PLAIN, 3, (50, 50, 50), 3)


# ========== Clase Detector de Gestos ==========
class DetectorGestos:
    def __init__(self, cooldown=1.0):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )
        self.drawer = mp.solutions.drawing_utils
        self.last_gesture = None
        self.last_time = 0
        self.cooldown = cooldown

    def detectar(self, frame):
        imgRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                self.drawer.draw_landmarks(
                    frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS
                )
        return frame

    def _contar_dedos(self, hand_landmarks, label):
        lm = hand_landmarks.landmark
        dedos_arriba = []

        # Pulgar
        if label == "Right":
            dedos_arriba.append(1 if lm[4].x < lm[3].x else 0)
        else:
            dedos_arriba.append(1 if lm[4].x > lm[3].x else 0)

        # Índice a meñique
        for id in [8, 12, 16, 20]:
            dedos_arriba.append(1 if lm[id].y < lm[id - 2].y else 0)

        return sum(dedos_arriba)

    def detectar_gesto(self, frame):
        if not hasattr(self, "results") or not self.results.multi_hand_landmarks:
            return None

        H, W, _ = frame.shape
        gesture = None
        manos = self.results.multi_hand_landmarks
        handedness = getattr(self.results, "multi_handedness", None)

        # Dos manos → "="
        if len(manos) == 2:
            palma1 = manos[0].landmark[0]
            palma2 = manos[1].landmark[0]
            dist = math.hypot((palma1.x - palma2.x) * W, (palma1.y - palma2.y) * H)
            if dist < 250:
                gesture = "="

        else:
            mano = manos[0]
            label = handedness[0].classification[0].label if handedness else "Right"
            num = self._contar_dedos(mano, label)

            # Mano en forma de C
            dedos_flexionados = 0
            lm = mano.landmark
            for id in [8, 12, 16, 20]:
                dist = math.hypot((lm[id].x - lm[id - 2].x) * W,
                                  (lm[id].y - lm[id - 2].y) * H)
                if dist < 40:
                    dedos_flexionados += 1

            if 1 <= dedos_flexionados <= 3 and num < 3:
                gesture = "C"
            else:
                gesture = str(num)

        # Control de repetición
        now = time.time()
        if gesture and (now - self.last_time) > self.cooldown:
            self.last_gesture = gesture
            self.last_time = now
            return gesture
        return None


# ========== CONFIGURACIÓN DE CÁMARA ==========
cap = cv2.VideoCapture(0)  # Cambia a 1 o 2 según tu cámara
WIDTH = 1200
HEIGHT = 1080
cap.set(3, WIDTH)
cap.set(4, HEIGHT)

# Crear botones
buttonListValues = [['C', '<'],
                    ['7', '8', '9', '/'],
                    ['4', '5', '6', '*'],
                    ['1', '2', '3', '-'],
                    ['0', '.', '=', '+']]

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

# Inicializar detector de gestos
detector = DetectorGestos()
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
