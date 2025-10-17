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
        self.tiempo_estabilidad = 0.5
        self.modo_operaciones = False  # Modo números por defecto

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

    def _detectar_cambio_modo(self, hand_landmarks):
        """Detecta gesto para cambiar modo: índice y meñique extendidos (cuernos)"""
        lm = hand_landmarks.landmark
        
        indice_ext = lm[8].y < lm[6].y - 0.05
        medio_cer = lm[12].y >= lm[10].y - 0.02
        anular_cer = lm[16].y >= lm[14].y - 0.02
        menique_ext = lm[20].y < lm[18].y - 0.05
        pulgar_cer = abs(lm[4].x - lm[2].x) < 0.06
        
        return indice_ext and medio_cer and anular_cer and menique_ext and pulgar_cer

    def _detectar_operacion_por_dedos(self, hand_landmarks):
        """Detecta operaciones según número de dedos en modo operaciones"""
        lm = hand_landmarks.landmark
        
        # Contar solo índice, medio, anular (sin pulgar ni meñique)
        indice_ext = lm[8].y < lm[6].y - 0.05
        medio_ext = lm[12].y < lm[10].y - 0.05
        anular_ext = lm[16].y < lm[14].y - 0.05
        
        dedos_operacion = sum([indice_ext, medio_ext, anular_ext])
        
        if dedos_operacion == 1 and indice_ext:
            return "+"
        elif dedos_operacion == 2 and indice_ext and medio_ext:
            return "-"
        elif dedos_operacion == 3 and indice_ext and medio_ext and anular_ext:
            return "×"
        
        return None

    def _detectar_pulgar_arriba(self, hand_landmarks):
        """Detecta pulgar arriba (para división)"""
        lm = hand_landmarks.landmark
        pulgar_tip = lm[4]
        pulgar_mcp = lm[2]
        
        # Pulgar arriba
        pulgar_arriba = pulgar_tip.y < pulgar_mcp.y - 0.08
        
        # Resto de dedos cerrados
        dedos_cerrados = 0
        for id in [8, 12, 16, 20]:
            if lm[id].y >= lm[id - 2].y - 0.02:
                dedos_cerrados += 1
        
        return pulgar_arriba and dedos_cerrados >= 3

    def _detectar_gesto_igual(self, hand_landmarks):
        """Detecta gesto =: mano completamente abierta (5 dedos)"""
        lm = hand_landmarks.landmark
        
        # Todos los dedos extendidos
        dedos_ext = 0
        
        # Pulgar
        if abs(lm[4].x - lm[2].x) > 0.08:
            dedos_ext += 1
        
        # Índice, medio, anular, meñique
        for id in [8, 12, 16, 20]:
            if lm[id].y < lm[id - 2].y - 0.04:
                dedos_ext += 1
        
        return dedos_ext == 5

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

        # ========== UNA MANO ==========
        if len(manos) == 1:
            mano = manos[0]
            label = handedness[0].classification[0].label if handedness else "Right"
            
            # 1. Verificar gesto de cambio de modo (prioridad máxima)
            if self._detectar_cambio_modo(mano):
                gesto_detectado = "MODO_TOGGLE"
            
            # 2. MODO OPERACIONES
            elif self.modo_operaciones:
                # División: pulgar arriba
                if self._detectar_pulgar_arriba(mano):
                    gesto_detectado = "÷"
                else:
                    # Otras operaciones por dedos
                    operacion = self._detectar_operacion_por_dedos(mano)
                    if operacion:
                        gesto_detectado = operacion
            
            # 3. MODO NÚMEROS
            else:
                # Puño cerrado (0)
                if self._detectar_puño_cerrado(mano):
                    gesto_detectado = "0"
                
                # Gesto C (Clear)
                elif self._detectar_gesto_C(mano, label):
                    gesto_detectado = "C"
                
                # Mano abierta (=)
                elif self._detectar_gesto_igual(mano):
                    gesto_detectado = "="
                
                # Números 1-5
                else:
                    _, num_dedos = self._contar_dedos(mano, label)
                    if 1 <= num_dedos <= 5:
                        gesto_detectado = str(num_dedos)

        # ========== DOS MANOS (solo en modo números) ==========
        elif len(manos) == 2 and not self.modo_operaciones:
            # Contar dedos totales (6-10)
            total_dedos = self._contar_dedos_dos_manos(manos, handedness)
            if 6 <= total_dedos <= 10:
                gesto_detectado = str(total_dedos)

        # ========== SISTEMA DE CONFIRMACIÓN ==========
        now = time.time()
        
        # Si no se detecta gesto, resetear confirmación
        if not gesto_detectado:
            self.gesto_confirmado = None
            self.tiempo_confirmacion = 0
            return None
        
        # Gesto de cambio de modo tiene confirmación más rápida
        tiempo_necesario = 0.3 if gesto_detectado == "MODO_TOGGLE" else self.tiempo_estabilidad
        
        # Si es un gesto nuevo, iniciar confirmación
        if gesto_detectado != self.gesto_confirmado:
            self.gesto_confirmado = gesto_detectado
            self.tiempo_confirmacion = now
            return None
        
        # Si el gesto se mantiene estable el tiempo necesario
        if (now - self.tiempo_confirmacion) >= tiempo_necesario:
            # Verificar cooldown desde último gesto enviado
            if (now - self.last_time) >= self.cooldown:
                # Cambiar modo si es el gesto toggle
                if gesto_detectado == "MODO_TOGGLE":
                    self.modo_operaciones = not self.modo_operaciones
                    self.last_gesture = gesto_detectado
                    self.last_time = now
                    self.gesto_confirmado = None
                    return "MODO_OP" if self.modo_operaciones else "MODO_NUM"
                
                # Gesto normal
                self.last_gesture = gesto_detectado
                self.last_time = now
                self.gesto_confirmado = None
                return gesto_detectado
        
        return None

    def obtener_modo(self):
        """Retorna el modo actual"""
        return "OPERACIONES" if self.modo_operaciones else "NÚMEROS"

    def obtener_tiempo_restante(self):
        """Retorna el tiempo restante de cooldown"""
        now = time.time()
        restante = self.cooldown - (now - self.last_time)
        return max(0, restante)