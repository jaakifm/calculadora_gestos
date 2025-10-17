import cv2
import mediapipe as mp
import math
import time


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