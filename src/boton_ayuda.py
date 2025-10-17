# utils/ayuda.py
import cv2
import numpy as np

def mostrar_instrucciones():
    """Abre una ventana con instrucciones de uso."""
    # Crear una imagen negra como fondo
    ayuda_img = np.zeros((700, 800, 3), dtype=np.uint8)
    ayuda_img[:] = (40, 40, 40)  # fondo gris oscuro

    # Texto informativo
    instrucciones = [
        "=== INSTRUCCIONES DE USO ===",
        "",
        "1️⃣  Coloca las manos frente a la cámara.",
        "2️⃣  Los gestos representan números y operaciones:",
        "     Puño cerrado .......... 0",
        "     Un dedo levantado ..... 1",
        "     Dos dedos levantados .. 2",
        "     Tres dedos levantados . 3",
        "     Cuatro dedos .......... 4",
        "     Cinco dedos (mano izquierda) ........... 5",
        "     Seis-diez dedos ....... 6–10",
        "     una L (mediante el indice u el pulgar) ........... C (borrar)",
        "     Palma de la mano derecha  = (calcular)",
        "     Indice y meñique  cambiar de modo (número/operador)",
        "     Un dedo ......... +",
        "     Dos dedos ...... -",
        "     Tres dedos ........ *",
        "     Cuatro dedos ......... /",
        "",
        "3️⃣  La operación aparece arriba en la calculadora.",
        "4️⃣  Usa 'q' para salir del programa.",
        "",
        "Haz clic nuevamente en la esquina inferior izquierda para cerrar."
    ]

    y = 50
    for linea in instrucciones:
        color = (255, 255, 255)
        font_scale = 0.8
        if "===" in linea:
            color = (0, 255, 255)
            font_scale = 1.0
        cv2.putText(ayuda_img, linea, (40, y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, 2)
        y += 40

    # Mostrar ventana
    cv2.imshow("Ayuda - Calculadora Gestual", ayuda_img)
    cv2.waitKey(0)
    cv2.destroyWindow("Ayuda - Calculadora Gestual")
