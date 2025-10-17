class Operador:
    def __init__(self):
        self.operacion = ""

    def procesar(self, valor):
        """Procesa el valor recibido (número, operador o control)."""

        # Lista de caracteres válidos
        caracteres_validos = ['0','1','2','3','4','5','6','7','8','9',
                              '+','-','*','/','.','C','<','=']

        # Ignorar valores no válidos (por ejemplo: MODO_OP, MODO_NUM)
        if valor not in caracteres_validos:
            return self.operacion

        # === CONTROLES ===
        if valor == "C":
            self.operacion = ""
        elif valor == "<":
            self.operacion = self.operacion[:-1]
        elif valor == "=":
            self.operacion = self.calcular()
        else:
            # Concatenar valor válido
            self.operacion += valor

        return self.operacion

    def calcular(self):
        """Evalúa la operación actual y devuelve el resultado."""
        try:
            resultado = str(eval(self.operacion))
        except Exception:
            resultado = "Error"
        return resultado

    def obtener_operacion(self):
        """Devuelve la cadena actual para mostrar en pantalla."""
        return self.operacion
