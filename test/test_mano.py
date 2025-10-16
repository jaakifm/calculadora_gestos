# test_mano.py
import cv2
import mediapipe as mp
import math
import sys

def contar_dedos(hand_landmarks, W, H):
    lm = hand_landmarks.landmark
    dedos_ids = [4, 8, 12, 16, 20]
    dedos_arriba = []

    # Pulgar: comparar con metacarpiano (3)
    # Nota: para manos derechas/izquierdas la comparación x puede invertirse; aquí usamos heurística simple:
    try:
        if lm[4].x < lm[3].x:
            dedos_arriba.append(1)
        else:
            dedos_arriba.append(0)
    except:
        dedos_arriba.append(0)

    # Dedos restantes: comparar punta con la articulación dos posiciones atrás
    for id in (8, 12, 16, 20):
        try:
            if lm[id].y < lm[id - 2].y:
                dedos_arriba.append(1)
            else:
                dedos_arriba.append(0)
        except:
            dedos_arriba.append(0)

    return sum(dedos_arriba), dedos_arriba

def main(cam_index=0):
    mp_hands = mp.solutions.hands
    mp_drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(cam_index)
    if not cap.isOpened():
        print(f"ERROR: no se pudo abrir la cámara index={cam_index}")
        print("Prueba con otro índice de cámara (0,1,2) o cierra otras apps que usen la cámara.")
        return

    with mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5
    ) as hands:
        print("Cámara abierta. Presiona ESC para salir.")
        while True:
            ret, frame = cap.read()
            if not ret:
                print("ERROR: frame vacío (ret=False)")
                break

            H, W, _ = frame.shape
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(frame_rgb)

            texto_debug = "Manos: 0"

            if results.multi_hand_landmarks:
                texto_debug = f"Manos: {len(results.multi_hand_landmarks)}"
                total_dedos = 0
                # procesar cada mano
                for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                    dedos, arreglo = contar_dedos(hand_landmarks, W, H)
                    total_dedos += dedos
                    # Mostrar número de dedos de cada mano en la imagen
                    cv2.putText(frame, f"Mano{i+1}: {dedos} ({arreglo})", (10, 30 + i*30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

                # heurística simple para = (dos palmas enfrentadas)
                if len(results.multi_hand_landmarks) >= 2:
                    p0 = results.multi_hand_landmarks[0].landmark[0]
                    p1 = results.multi_hand_landmarks[1].landmark[0]
                    x0, y0 = int(p0.x * W), int(p0.y * H)
                    x1, y1 = int(p1.x * W), int(p1.y * H)
                    dist = math.hypot(x1 - x0, y1 - y0)
                    cv2.putText(frame, f"DistPalmas:{int(dist)}", (10, H-50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,0,0), 2)
                    if abs(y0 - y1) < 100 and dist < 250:
                        cv2.putText(frame, "Gesto detectado: =", (W//2 - 100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0,0,255), 3)
                else:
                    # mostrar gesto numérico simple (suma de dedos detectados)
                    cv2.putText(frame, f"Gesto numerico total: {total_dedos}", (W//2 - 140, 50),
                                cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0,0,255), 3)
            else:
                cv2.putText(frame, "Manos: 0", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

            # información en consola para debug
            sys.stdout.write("\r" + texto_debug)
            sys.stdout.flush()

            cv2.imshow("TEST_MEDIAPIPE", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            if key == ord('0'):  # probar otros índices
                cap.release()
                cam_index = 0
                cap = cv2.VideoCapture(cam_index)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main(0)
