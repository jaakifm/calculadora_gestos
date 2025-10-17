import cv2
import mediapipe as mp
import math
import time


class DetectorGestos:
    def __init__(self, cooldown=2.5):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        self.drawer = mp.solutions.drawing_utils
        self.last_gesture = None
        self.last_time = 0
        self.cooldown = cooldown
        self.gesto_confirmado = None
        self.tiempo_confirmacion = 0
        self.tiempo_estabilidad = 0.5  # Tiempo que debe mantenerse el gesto

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
        """Cuenta dedos levantados de forma precisa"""
        lm = hand_landmarks.landmark
        dedos = []

        # Pulgar - detección robusta
        pulgar_tip = lm[4]
        pulgar_mcp = lm[2]
        
        if label == "Right":
            dedos.append(1 if pulgar_tip.x < pulgar_mcp.x - 0.05 else 0)
        else:
            dedos.append(1 if pulgar_tip.x > pulgar_mcp.x + 0.05 else 0)

        # Índice, medio, anular, meñique
        for id in [8, 12, 16, 20]:
            tip = lm[id]
            pip = lm[id - 2]
            dedos.append(1 if tip.y < pip.y - 0.04 else 0)

        return dedos, sum(dedos)

    def _detectar_puño_cerrado(self, hand_landmarks):
        """Detecta puño completamente cerrado (0)"""
        lm = hand_landmarks.landmark
        dedos_cerrados = 0
        
        # Verificar TODOS los dedos cerrados (incluyendo pulgar)
        for id in [4, 8, 12, 16, 20]:
            tip = lm[id]
            base = lm[5 if id == 4 else id - 3]
            if tip.y >= base.y - 0.03:
                dedos_cerrados += 1
        
        return dedos_cerrados == 5

    def _detectar_gesto_C(self, hand_landmarks, label):
        """Detecta gesto C: pulgar e índice extendidos formando L, resto cerrados"""
        lm = hand_landmarks.landmark
        
        # Pulgar extendido lateralmente
        pulgar_tip = lm[4]
        pulgar_mcp = lm[2]
        pulgar_abierto = abs(pulgar_tip.x - pulgar_mcp.x) > 0.08
        
        # Índice extendido hacia arriba
        indice_tip = lm[8]
        indice_pip = lm[6]
        indice_abierto = indice_tip.y < indice_pip.y - 0.05
        
        # Medio, anular, meñique cerrados
        dedos_cerrados = 0
        for id in [12, 16, 20]:
            tip = lm[id]
            base = lm[id - 3]
            if tip.y >= base.y - 0.02:
                dedos_cerrados += 1
        
        return pulgar_abierto and indice_abierto and dedos_cerrados == 3

    def _detectar_operacion(self, hand_landmarks, label):
        """Detecta gestos de operaciones matemáticas"""
        lm = hand_landmarks.landmark
        
        indice = lm[8]
        medio = lm[12]
        anular = lm[16]
        menique = lm[20]
        muneca = lm[0]
        
        # Verificar qué dedos están extendidos
        indice_ext = indice.y < lm[6].y - 0.05
        medio_ext = medio.y < lm[10].y - 0.05
        anular_ext = anular.y < lm[14].y - 0.05
        menique_ext = menique.y < lm[18].y - 0.05
        pulgar_ext = abs(lm[4].x - lm[2].x) > 0.08
        
        # + : Índice y medio extendidos, resto cerrado
        if indice_ext and medio_ext and not anular_ext and not menique_ext and not pulgar_ext:
            return "+"
        
        # - : Solo índice extendido
        if indice_ext and not medio_ext and not anular_ext and not menique_ext:
            return "-"
        
        # × : Índice y meñique extendidos, medio y anular cerrados
        if indice_ext and menique_ext and not medio_ext and not anular_ext:
            return "×"
        
        # ÷ : Índice, medio y anular extendidos, meñique cerrado
        if indice_ext and medio_ext and anular_ext and not menique_ext and not pulgar_ext:
            return "÷"
        
        return None

    def _contar_dedos_dos_manos(self, manos, handedness):
        """Cuenta dedos totales de ambas manos"""
        total = 0
        for i, mano in enumerate(manos):
            label = handedness[i].classification[0].label if handedness else "Right"
            _, num = self._contar_dedos(mano, label)
            total += num
        return total

    def detectar_gesto(self, frame):
        if not hasattr(self, "results") or not self.results.multi_hand_landmarks:
            self.gesto_confirmado = None
            return None

        H, W, _ = frame.shape
        manos = self.results.multi_hand_landmarks
        handedness = getattr(self.results, "multi_handedness", None)
        gesto_detectado = None

        # ========== DOS MANOS ==========
        if len(manos) == 2:
            # Verificar si es el gesto "="
            palma1 = manos[0].landmark[9]
            palma2 = manos[1].landmark[9]
            
            dist_x = abs((palma1.x - palma2.x) * W)
            dist_y = abs((palma1.y - palma2.y) * H)
            
            if dist_x < 180 and dist_y < 80:
                gesto_detectado = "="
            else:
                # Contar dedos totales (6-10)
                total_dedos = self._contar_dedos_dos_manos(manos, handedness)
                if 6 <= total_dedos <= 10:
                    gesto_detectado = str(total_dedos)

        # ========== UNA MANO ==========
        elif len(manos) == 1:
            mano = manos[0]
            label = handedness[0].classification[0].label if handedness else "Right"
            
            # 1. Detectar puño cerrado (0)
            if self._detectar_puño_cerrado(mano):
                gesto_detectado = "0"
            
            # 2. Detectar gesto C (Clear)
            elif self._detectar_gesto_C(mano, label):
                gesto_detectado = "C"
            
            # 3. Detectar operaciones
            else:
                operacion = self._detectar_operacion(mano, label)
                if operacion:
                    gesto_detectado = operacion
                else:
                    # 4. Contar dedos (1-5)
                    _, num_dedos = self._contar_dedos(mano, label)
                    if 1 <= num_dedos <= 5:
                        gesto_detectado = str(num_dedos)

        # ========== SISTEMA DE CONFIRMACIÓN ==========
        now = time.time()
        
        # Si no se detecta gesto, resetear confirmación
        if not gesto_detectado:
            self.gesto_confirmado = None
            self.tiempo_confirmacion = 0
            return None
        
        # Si es un gesto nuevo, iniciar confirmación
        if gesto_detectado != self.gesto_confirmado:
            self.gesto_confirmado = gesto_detectado
            self.tiempo_confirmacion = now
            return None
        
        # Si el gesto se mantiene estable el tiempo necesario
        if (now - self.tiempo_confirmacion) >= self.tiempo_estabilidad:
            # Verificar cooldown desde último gesto enviado
            if (now - self.last_time) >= self.cooldown:
                self.last_gesture = gesto_detectado
                self.last_time = now
                self.gesto_confirmado = None  # Resetear para próximo gesto
                return gesto_detectado
        
        return None

    def obtener_tiempo_restante(self):
        """Retorna el tiempo restante de cooldown"""
        now = time.time()
        restante = self.cooldown - (now - self.last_time)
        return max(0, restante)