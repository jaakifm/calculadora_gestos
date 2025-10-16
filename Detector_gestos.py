#importar librerias

import cv2
import mediapipe as mp
import math
import time

#clase con sus metodos
class Detector_gestos:
    def __init__(self):
        self.Manos = mp.solution.hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            model_complexity=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.Draw = mp.solutions.drawing_utils
        self.ultimo_gesto = None
        self.tiempo__ultimo_gesto = 0 
        self.tiempo = 1
    
    def detectar(self, img, dibujar=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.resultados = self.Manos.process(imgRGB)

        #dibujar en camara los landmarks de las manos que detecta
        if self.resultados.multi_hand_landmarks:
            for mano_Landmarks in self.resultados.multi_hand_landmarks:
                if dibujar:
                    self.Draw.draw_landmarks(img, mano_Landmarks, mp.solutions.hands.HAND_CONNECTIONS)
        return img
    
    def asignar_gesto_detectado(self, img):
        if not self.resultados.multi_hand_landmarks:
            return None

        num_dedos_totales = 0
        gesto = None
        H, W, _ = img.shape

        # ----------- CASO ESPECIAL: Gesto "=" (dos palmas enfrentadas)
        if len(self.resultados.multi_hand_landmarks) == 2:
            mano1 = self.resultados.multi_hand_landmarks[0]
            mano2 = self.resultados.multi_hand_landmarks[1]
            palma1 = mano1.landmark[0]
            palma2 = mano2.landmark[0]

            # Convertir coordenadas a pixeles
            x1, y1 = int(palma1.x * W), int(palma1.y * H)
            x2, y2 = int(palma2.x * W), int(palma2.y * H)
            distancia_palmas = math.hypot(x2 - x1, y2 - y1)

            # Si las palmas están una encima de otra (pequeña distancia vertical)
            if abs(y1 - y2) < 100 and distancia_palmas < 250:
                gesto = "="

        # ----------- GESTOS CON UNA SOLA MANO (números, C, etc.)
        else:
            mano = self.resultados.multi_hand_landmarks[0]
            lm = mano.landmark

            # Coordenadas de puntos clave (puntas de los dedos)
            dedos_ids = [4, 8, 12, 16, 20]
            dedos_arriba = []

            # Pulgar: comparar posición x
            if lm[4].x < lm[3].x:
                dedos_arriba.append(1)
            else:
                dedos_arriba.append(0)

            # Otros dedos: comparar y con su articulación anterior
            for id in [8, 12, 16, 20]:
                if lm[id].y < lm[id - 2].y:
                    dedos_arriba.append(1)
                else:
                    dedos_arriba.append(0)

            num_dedos = sum(dedos_arriba)
            num_dedos_totales = num_dedos

            # ---- GESTO DE BORRADO ("C" = mano curvada)
            # Comprobar curvatura de los dedos: si están parcialmente doblados
            dedos_flexionados = 0
            for id in [8, 12, 16, 20]:
                dist = math.hypot(
                    (lm[id].x - lm[id - 2].x) * W,
                    (lm[id].y - lm[id - 2].y) * H
                )
                if dist < 40:  # dedo doblado
                    dedos_flexionados += 1

            # Si la mayoría de los dedos están doblados pero no puño cerrado → "C"
            if 1 <= dedos_flexionados <= 3 and num_dedos_totales < 3:
                gesto = "C"
            else:
                # Número de dedos visibles = número
                gesto = str(num_dedos_totales)

        # Control de repetición (cooldown)
        ahora = time.time()
        if gesto and (ahora - self.tiempo_ultimo_gesto) > self.cooldown:
            self.ultimo_gesto = gesto
            self.tiempo_ultimo_gesto = ahora
            return gesto

        return None