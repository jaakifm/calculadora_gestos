# Calculadora por gestos

Proyecto que implementa una calculadora controlada por gestos de mano usando OpenCV y MediaPipe.

El principal objetivo del código es, detectar la cantidad de dedos mostrados atraves de las 2 manos, o gestos sencillos realizados con las mismas, para integrarse en una interfaz sencilla que se muestra por pantalla para simular una calculadora.


## Características

- Detección de manos y sus respectivos landmarks con MediaPipe.
- Reconocimiento básico de gestos: números por dedos levantados, gesto "L" (mediante indice y pulgar) para borrar y gesto "=" mostrando la palma derecha.
- Interfaz gráfica sobre el feed de la cámara con botones de calculadora (dibujados usando OpenCV).

## Requisitos

- Python 3.12 recomendado
- Paquetes Python:
	- opencv-python
	- mediapipe


Puedes instalarlos con pip:

```bash
pip install opencv-python mediapipe 
```

Otra forma de intalar todas las dependencias requeridas es mediante el archivo `requirements.txt`, ejecutando en la terminal:

```bash
pip install -r requirements.txt
```


## Estructura del proyecto

- `main.py` - Programa principal que inicializa la cámara, ejecuta la detección de gestos y muestra el feed.
- `Detector_gestos.py` - Clase `Detector_gestos` que envuelve MediaPipe Hands y contiene la lógica para asignar gestos los gestos detectados a su respectiva interpretación.
- `operador.py` en el que se lleva a cabo las operaciones matematicas y habilita el funcionamiento correctod e la calculadora.
- `utils/` - Configuraciones auxiliares:
	- `config_camara.py` - Inicialización de la cámara (función `init_camera`).
	- `config.py` - Constantes como `WIDTH`, `HEIGHT` y `buttonListValues`.
- `requirements.txt` - Archivo para intalar todas las dependencias requeridas.
- Finalmente hay una carpeta aparte del codigo pricipal llamada test, en la que se guardo una prueba para la comprobacion del funcionamiento de los landmark de Mediapipe.

## Uso

1. Conecta una cámara (webcam integrada o externa).
2. Abre un terminal en la carpeta del proyecto.
3. Ejecuta:

```bash
python main.py
```

Esto abrirá una ventana con el feed de la cámara. El programa detectará manos y, cuando reconozca un gesto estable (según la lógica de `Detector_gestos`), imprimirá el gesto detectado en la consola.

## Notas de implementación

- `Detector_gestos.py` usa MediaPipe para obtener los landmarks de la mano. La función `asignar_gesto_detectado` implementa la localización de cada landmark para asociarla a un gesto segun la distancia entre ellos:
	- Números (0-9) según dedos levantados.
	- Gesto "C" (una L mediante el indice u el pulgar) según distancia entre articulaciones de los dedos.
	- Gesto "=" cuando se detecta la mano izquierda completamente estirada.

- Hay variables de control de tiempo (cooldown) para evitar lecturas repetidas del mismo gesto; revisa `Detector_gestos.py` si quieres ajustar la sensibilidad o el intervalo.


## Solución a posibles problemas

- Si la cámara no se inicializa, prueba cambiar el "INDEX_CAMARA" en `utils/config.py` (0, 1, 2...).



