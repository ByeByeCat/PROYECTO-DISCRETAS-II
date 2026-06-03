# ============================================================
# Validador de Tramas TCP/IP mediante Máquina de Estados Finita (FSM)
# Proyecto Final — Matemáticas Discretas II
# ============================================================

import tkinter as tk
from tkinter import scrolledtext


# ============================================================
# ███  DEFINICIÓN FORMAL DE LA FSM  ███
#
# Una Máquina de Estados Finita (FSM) se define formalmente como:
#
#   M = (Q, Σ, δ, q0, F)
#
# ─── Componentes ───────────────────────────────────────────
#
# Q  = { INICIO, LEYENDO_PREAMBULO, LEYENDO_CONTROL,
#         TRAMA_VALIDA, TRAMA_INVALIDA, FIN_TRAMA }
#       Conjunto finito de estados.
#
# Σ  = { 0, 1 }
#       Alfabeto de entrada: un bit individual por transición.
#
# q0 = INICIO
#       Estado inicial de la máquina.
#
# F  = { TRAMA_VALIDA, TRAMA_INVALIDA }
#       Estados de aceptación: marcan el resultado de evaluar una trama.
#
# δ : Q × Σ → Q
#       Función de transición (implementada en FSM.transicion).
#
# ─── Tabla de transiciones δ(q, a) ────────────────────────
#
#  Estado actual      │ Condición/evento           │ Siguiente estado
#  ───────────────────┼────────────────────────────┼──────────────────────
#  INICIO             │ cualquier bit              │ LEYENDO_PREAMBULO
#  LEYENDO_PREAMBULO  │ bit_pos < 13               │ LEYENDO_PREAMBULO
#  LEYENDO_PREAMBULO  │ bit_pos == 13              │ LEYENDO_CONTROL
#  LEYENDO_CONTROL    │ acumulados < 4             │ LEYENDO_CONTROL
#  LEYENDO_CONTROL    │ acumulados==4 ∧ C1 ∧ C2   │ TRAMA_VALIDA
#  LEYENDO_CONTROL    │ acumulados==4 ∧ ¬(C1 ∧ C2)│ TRAMA_INVALIDA
#  TRAMA_VALIDA       │ cualquier bit              │ FIN_TRAMA
#  TRAMA_INVALIDA     │ cualquier bit              │ FIN_TRAMA
#  FIN_TRAMA          │ bit_pos < 31               │ FIN_TRAMA
#  FIN_TRAMA          │ bit_pos == 31              │ INICIO  (nueva trama)
#
# ─── Condiciones de validez de una trama ──────────────────
#
#   Sea B = int(trama[13:17], 2)   → valor entero de los 4 bits de control
#   Sea L = lista_validacion[i]    → valor de validación para la trama i
#
#   C1 : B mod 2 == 0              → B es par (múltiplo de 2)
#   C2 : (B + L) mod 5 == 0        → la suma es múltiplo de 5
#
#   Trama válida  ⟺  C1 ∧ C2
#
# ─── Veredicto de la transmisión ──────────────────────────
#
#   Sea E = (tramas inválidas / total tramas) × 100
#   Transmisión correcta ⟺ E < 20   (estrictamente menor)
#
# ─── Posición de los bits de control ──────────────────────
#
#   El enunciado indica: "en el bit 14 inicia la validación
#   de los próximos 4 bits de control".
#
#   En notación 1-indexed (estándar de protocolos):   bits 14, 15, 16, 17
#   En notación 0-indexed (Python, cadenas):   índices 13, 14, 15, 16
#   Extracción en Python:  trama[13:17]
# ============================================================


# ══════════════════════════════════════════════════════════
# SECCIÓN 1 — ESTADOS DE LA FSM
# ══════════════════════════════════════════════════════════

class Estados:
    """
    Define los estados Q de la FSM como constantes de clase.

    Usar constantes en lugar de cadenas literales dispersas por el
    código evita errores de escritura y facilita el mantenimiento.

    Descripción de cada estado:
        INICIO            → q0. La FSM espera el primer bit de una nueva trama.
        LEYENDO_PREAMBULO → Procesando bits 0-12: son irrelevantes para la
                            validación y se descartan.
        LEYENDO_CONTROL   → Acumulando los 4 bits del campo de control
                            (índices 13, 14, 15 y 16 de la trama).
        TRAMA_VALIDA      → Estado final de aceptación: C1 y C2 se cumplen.
        TRAMA_INVALIDA    → Estado final de rechazo: al menos una condición falla.
        FIN_TRAMA         → Consumiendo los bits restantes (índices 17-31)
                            tras haber evaluado la trama.
    """
    INICIO            = "INICIO"
    LEYENDO_PREAMBULO = "LEYENDO_PREAMBULO"
    LEYENDO_CONTROL   = "LEYENDO_CONTROL"
    TRAMA_VALIDA      = "TRAMA_VALIDA"
    TRAMA_INVALIDA    = "TRAMA_INVALIDA"
    FIN_TRAMA         = "FIN_TRAMA"


# ══════════════════════════════════════════════════════════
# SECCIÓN 2 — IMPLEMENTACIÓN DE LA FSM
# ══════════════════════════════════════════════════════════

class FSM:
    """
    Máquina de Estados Finita (FSM) para validar tramas de 32 bits
    del protocolo TCP/IP modificado académicamente.

    La FSM recibe los bits de cada trama de forma secuencial
    (uno por uno) y determina si cada trama cumple las condiciones
    de validez definidas por el protocolo.

    Atributos internos:
        lista_validacion (list[int]): Valores de referencia L[0..n-1].
        estado (str):                 Estado actual de la FSM (∈ Q).
        bit_actual (int):             Posición del bit en la trama (0-31).
        bits_control (list[int]):     Acumulador de bits del campo de control.
        trama_num (int):              Índice de la trama en proceso.
        resultados (list[bool]):      Veredicto de cada trama procesada.
        detalles (list[dict]):        Info detallada de cada evaluación (para GUI).
    """

    # ── Constantes del protocolo ──────────────────────────────────────────
    #
    # BIT_INICIO_CONTROL: primera posición (0-indexed) del campo de control.
    #   Enunciado: "en el BIT 14 inicia la validación" (notación 1-indexed)
    #   Python 0-indexed: bit 14 (1-indexed) = índice 13 (0-indexed)
    BIT_INICIO_CONTROL = 13

    # NUM_BITS_CONTROL: tamaño del campo de control (siempre 4 bits).
    NUM_BITS_CONTROL = 4

    # BITS_POR_TRAMA: longitud de cada trama.
    #   El enunciado la reduce de 64 a 32 bits por motivos académicos.
    BITS_POR_TRAMA = 32

    # ─────────────────────────────────────────────────────────────────────

    def __init__(self, lista_validacion):
        """
        Inicializa la FSM en el estado q0 = INICIO con todos los
        contadores en sus valores iniciales.

        Args:
            lista_validacion (list[int]): Un valor entero (0-15) por cada
                trama esperada. Se usa como L[i] en la condición C2.
        """
        self.lista_validacion = lista_validacion   # Referencia de validación
        self.estado           = Estados.INICIO     # Estado actual → q0
        self.bit_actual       = 0                  # Índice del bit actual (0-31)
        self.bits_control     = []                 # Acumulador de los 4 bits de control
        self.trama_num        = 0                  # Número de la trama en curso (índice)
        self.resultados       = []                 # True=válida / False=inválida por trama
        self.detalles         = []                 # Historial detallado para la GUI

    # ──────────────────────────────────────────────────────────────────────
    # FUNCIÓN DE TRANSICIÓN PRINCIPAL:  δ(estado, bit) → nuevo_estado
    # ──────────────────────────────────────────────────────────────────────
    def transicion(self, bit):
        """
        Implementa la función de transición δ : Q × Σ → Q.

        Recibe UN bit del alfabeto Σ = {0, 1} y, de acuerdo con el
        estado actual, actualiza el estado de la FSM.

        Este método es el núcleo de la máquina de estados. Cada llamada
        procesa exactamente un bit de la trama de 32 bits.

        Args:
            bit (int): Valor del bit de entrada; debe ser 0 ó 1.
        """

        # ── δ(INICIO, bit) = LEYENDO_PREAMBULO ──────────────────────────
        # Al recibir el primer bit de una nueva trama, la FSM sale del
        # estado inicial y comienza a leer el preámbulo.
        # El bit actual pertenece al preámbulo y se descarta.
        if self.estado == Estados.INICIO:
            self.estado = Estados.LEYENDO_PREAMBULO

        # ── δ(LEYENDO_PREAMBULO, bit) ─────────────────────────────────────
        # Permanecemos en este estado mientras el índice del bit sea menor
        # a 13 (bits del preámbulo, irrelevantes para la validación).
        # Cuando alcanzamos el índice 13, transitamos a LEYENDO_CONTROL
        # y guardamos ese primer bit de control en el acumulador.
        elif self.estado == Estados.LEYENDO_PREAMBULO:
            if self.bit_actual == self.BIT_INICIO_CONTROL:
                # Llegamos al primer bit del campo de control (índice 13)
                self.estado       = Estados.LEYENDO_CONTROL
                self.bits_control = [bit]    # Iniciamos el acumulador con el bit 13

        # ── δ(LEYENDO_CONTROL, bit) ───────────────────────────────────────
        # Acumulamos bits del campo de control hasta completar los 4.
        # El bit 13 ya fue guardado en la transición desde PREAMBULO,
        # por lo que aquí comenzamos desde el bit 14 en adelante.
        elif self.estado == Estados.LEYENDO_CONTROL:
            self.bits_control.append(bit)    # Guardamos el bit actual

            # ¿Ya acumulamos los 4 bits del campo de control?
            if len(self.bits_control) == self.NUM_BITS_CONTROL:
                # Evaluamos C1 y C2, y transitamos a VALIDA o INVALIDA
                self._evaluar_condiciones()

        # ── δ(TRAMA_VALIDA | TRAMA_INVALIDA, bit) = FIN_TRAMA ────────────
        # El resultado de la trama ya quedó registrado en _evaluar_condiciones.
        # Pasamos a FIN_TRAMA para consumir los bits restantes (índices 17-31)
        # sin cambiar el veredicto.
        elif self.estado in (Estados.TRAMA_VALIDA, Estados.TRAMA_INVALIDA):
            self.estado = Estados.FIN_TRAMA

        # ── δ(FIN_TRAMA, bit) = FIN_TRAMA ────────────────────────────────
        # Permanecemos aquí consumiendo los bits de la "cola" de la trama.
        # El método _fin_trama() se encargará del reinicio al llegar al bit 31.
        elif self.estado == Estados.FIN_TRAMA:
            pass    # No hay cambio de estado; solo consumimos el bit

        # ── Avanzamos el puntero de bits ──────────────────────────────────
        self.bit_actual += 1

        # ── ¿Se completaron los 32 bits de la trama? ──────────────────────
        # Si es así, registramos el resultado y reseteamos para la siguiente.
        if self.bit_actual == self.BITS_POR_TRAMA:
            self._fin_trama()

    # ──────────────────────────────────────────────────────────────────────
    # EVALUACIÓN DE LAS CONDICIONES DE VALIDEZ
    # ──────────────────────────────────────────────────────────────────────
    def _evaluar_condiciones(self):
        """
        Evalúa las dos condiciones de validez del protocolo sobre los
        4 bits de control acumulados en self.bits_control.

        ─ Condición C1: El valor entero de los 4 bits de control debe
          ser MÚLTIPLO DE 2 (número par). Equivale a verificar que el
          último bit del campo sea 0.
          Ejemplo: bits='1100' → valor=12 → 12 mod 2 = 0  ✅

        ─ Condición C2: La SUMA del valor de control más el valor de la
          lista de validación correspondiente a esta trama debe ser
          MÚLTIPLO DE 5.
          Ejemplo: B=12, L=3 → B+L=15 → 15 mod 5 = 0  ✅

        Transita a TRAMA_VALIDA si C1 y C2 se cumplen simultáneamente;
        de lo contrario transita a TRAMA_INVALIDA.
        """
        # Medida de seguridad: verificamos que exista un valor L[i] para esta trama.
        # Normalmente el UI lo garantiza, pero lo controlamos por robustez.
        if self.trama_num >= len(self.lista_validacion):
            self.estado = Estados.TRAMA_INVALIDA
            return

        # ── Conversión bits → entero ──────────────────────────────────────
        # self.bits_control es una lista de enteros, p.ej. [1, 1, 0, 0].
        # map(str, ...) convierte cada int al carácter '0' o '1'.
        # ''.join(...)  concatena los caracteres → '1100'.
        # int(..., 2)   convierte la cadena binaria a entero decimal → 12.
        valor_control = int(''.join(map(str, self.bits_control)), 2)

        # Valor de la lista de validación para esta trama
        valor_lista = self.lista_validacion[self.trama_num]

        # Suma de ambos valores (usada en C2)
        suma = valor_control + valor_lista

        # ── Condición C1: B es par (múltiplo de 2) ───────────────────────
        # Un número es par si y solo si su residuo al dividir entre 2 es 0.
        condicion1 = (valor_control % 2 == 0)

        # ── Condición C2: (B + L) es múltiplo de 5 ───────────────────────
        condicion2 = (suma % 5 == 0)

        # La trama es válida solo si AMBAS condiciones se cumplen
        es_valida = condicion1 and condicion2

        # ── Guardamos el detalle de esta evaluación para mostrar en GUI ───
        self.detalles.append({
            'trama':         self.trama_num + 1,                   # Número de trama (1-indexed)
            'bits_control':  ''.join(map(str, self.bits_control)),  # String de bits de control
            'valor_control': valor_control,                         # Valor decimal del campo
            'valor_lista':   valor_lista,                           # Valor decimal L[i]
            'suma':          suma,                                   # B + L
            'cond1':         condicion1,                             # ¿Cumple C1?
            'cond2':         condicion2,                             # ¿Cumple C2?
            'valida':        es_valida                               # ¿Trama válida en total?
        })

        # ── Transición final según el resultado ───────────────────────────
        if es_valida:
            self.estado = Estados.TRAMA_VALIDA
        else:
            self.estado = Estados.TRAMA_INVALIDA

    # ──────────────────────────────────────────────────────────────────────
    # FIN DE TRAMA Y REINICIO DE LA FSM
    # ──────────────────────────────────────────────────────────────────────
    def _fin_trama(self):
        """
        Se invoca automáticamente cuando se han procesado los 32 bits
        de la trama actual. Realiza dos acciones:

        1. Registra el veredicto final en self.resultados
           (True si terminó en TRAMA_VALIDA, False en otro caso).
        2. Reinicia los contadores y regresa al estado INICIO (q0),
           dejando la FSM lista para procesar la siguiente trama.

        Este reinicio es lo que permite a la FSM procesar múltiples
        tramas en secuencia sin necesidad de recrearla.
        """
        # Guardamos el resultado: True = VÁLIDA, False = cualquier otro estado
        self.resultados.append(self.estado == Estados.TRAMA_VALIDA)

        # Avanzamos al índice de la siguiente trama en la lista de validación
        self.trama_num += 1

        # Reseteamos los contadores internos de la trama actual
        self.bit_actual   = 0    # Volvemos al bit 0 para la próxima trama
        self.bits_control = []   # Vaciamos el acumulador de control

        # Regresamos a q0 para la siguiente trama
        self.estado = Estados.INICIO

    # ──────────────────────────────────────────────────────────────────────
    # ENTRADA BIT A BIT  (requerimiento explícito del enunciado)
    # ──────────────────────────────────────────────────────────────────────
    def procesar_bit_a_bit(self, trama_str):
        """
        Alimenta la FSM con los bits de una trama UNO POR UNO.

        Esto implementa directamente el requerimiento del enunciado:
        "los datos ingresan bit a bit, o una lista de las tramas de 32 bit".

        La trama se recibe como string de 32 caracteres '0'/'1'.
        Internamente, cada carácter se convierte al entero 0 ó 1
        y se envía a transicion(), que aplica δ un paso a la vez.

        Args:
            trama_str (str): Cadena de exactamente 32 caracteres '0'/'1'.
        """
        for bit_char in trama_str:
            # int('0') = 0 y int('1') = 1
            # Pasamos el bit a la función de transición δ
            self.transicion(int(bit_char))

    # ──────────────────────────────────────────────────────────────────────
    # RESUMEN GLOBAL DE LA TRANSMISIÓN
    # ──────────────────────────────────────────────────────────────────────
    def obtener_resumen(self):
        """
        Calcula y devuelve las estadísticas de la transmisión completa.

        Returns:
            dict con los campos:
              'total'            → número total de tramas procesadas
              'validas'          → tramas que cumplieron C1 y C2
              'invalidas'        → tramas que fallaron al menos una condición
              'porcentaje_error' → (invalidas / total) × 100
              'correcta'         → True si porcentaje_error < 20 (estrictamente)
        """
        total     = len(self.resultados)
        invalidas = self.resultados.count(False)
        validas   = total - invalidas

        # Porcentaje de error: proporción de tramas inválidas multiplicada por 100
        porcentaje_error = (invalidas / total * 100) if total > 0 else 0.0

        # El enunciado dice "error MENOR AL 20%", no "menor o igual".
        # Por eso usamos < 20.0 (comparación estricta).
        correcta = porcentaje_error < 20.0

        return {
            'total':            total,
            'validas':          validas,
            'invalidas':        invalidas,
            'porcentaje_error': porcentaje_error,
            'correcta':         correcta
        }


# ══════════════════════════════════════════════════════════
# SECCIÓN 3 — FUNCIONES DE VALIDACIÓN DE ENTRADA
# ══════════════════════════════════════════════════════════

def validar_4bits(s):
    """
    Verifica que la cadena s sea un valor binario de exactamente 4 bits.

    Se usa para validar cada entrada de la lista de validación antes
    de convertirla a entero y pasarla a la FSM.

    Args:
        s (str): Cadena a verificar.
    Returns:
        bool: True si tiene exactamente 4 caracteres y todos son '0' o '1'.
    """
    return len(s) == 4 and all(c in '01' for c in s)


def validar_32bits(s):
    """
    Verifica que la cadena s sea una trama binaria de exactamente 32 bits.

    Se usa para validar cada trama ingresada por el usuario antes de
    alimentarla a la FSM.

    Args:
        s (str): Cadena a verificar.
    Returns:
        bool: True si tiene exactamente 32 caracteres y todos son '0' o '1'.
    """
    return len(s) == 32 and all(c in '01' for c in s)


# ══════════════════════════════════════════════════════════
# SECCIÓN 4 — FUNCIÓN PRINCIPAL DE PROCESAMIENTO
# ══════════════════════════════════════════════════════════

def procesar(valid_entries, trama_entries, output):
    """
    Coordina el proceso completo de validación de tramas:

      1. Lee y valida las entradas del usuario desde la GUI.
      2. Construye la lista de validación L y la lista de tramas.
      3. Crea la FSM y la alimenta trama a trama, bit a bit.
      4. Muestra los resultados detallados en el área de texto.

    Args:
        valid_entries (list[tk.Entry]): Campos de la lista de validación.
        trama_entries (list[tk.Entry]): Campos de las tramas de 32 bits.
        output (scrolledtext.ScrolledText): Área de texto para resultados.
    """
    # Limpiamos el área de resultados antes de mostrar nueva información
    output.delete('1.0', 'end')

    # ── Paso 1: Leer y validar la lista de validación ────────────────────
    lista_validacion = []
    for i, entry in enumerate(valid_entries):
        bits = entry.get().strip()        # Leemos el valor e ignoramos espacios
        if not validar_4bits(bits):
            output.insert('end',
                f"⚠️  Error en lista[{i+1}]: '{bits}' "
                f"no es un valor válido de 4 bits binarios.\n")
            return                        # Detenemos el proceso si hay un error
        # int(bits, 2) convierte el string binario a entero: '0010' → 2
        lista_validacion.append(int(bits, 2))

    # ── Paso 2: Leer y validar las tramas ────────────────────────────────
    tramas = []
    for i, entry in enumerate(trama_entries):
        bits = entry.get().strip()        # Leemos la trama e ignoramos espacios
        if not validar_32bits(bits):
            output.insert('end',
                f"⚠️  Error en trama {i+1}: "
                f"debe tener exactamente 32 bits binarios.\n")
            return                        # Detenemos el proceso si hay un error
        tramas.append(bits)

    # Verificamos que la lista de validación tenga suficientes entradas
    # (debe haber al menos un valor L[i] por cada trama)
    if len(tramas) > len(lista_validacion):
        output.insert('end',
            "⚠️  La lista de validación debe tener "
            "al menos tantos valores como tramas.\n")
        return

    # ── Paso 3: Crear e inicializar la FSM ───────────────────────────────
    # Instanciamos la FSM con la lista de validación leída del usuario.
    # La FSM comienza en q0 = INICIO, lista para procesar la primera trama.
    fsm = FSM(lista_validacion)

    # ── Paso 4: Alimentar la FSM bit a bit con cada trama ────────────────
    # procesar_bit_a_bit entrega los 32 bits de cada trama uno por uno,
    # cumpliendo el requerimiento "los datos ingresan bit a bit".
    for trama in tramas:
        fsm.procesar_bit_a_bit(trama)

    # ── Paso 5: Mostrar los resultados detallados ─────────────────────────
    SEP = "─" * 64
    output.insert('end', f"\n{'═'*64}\n")
    output.insert('end', "  RESULTADOS DE EVALUACIÓN — FSM\n")
    output.insert('end', f"{'═'*64}\n")

    # Encabezado de la tabla de resultados
    output.insert('end',
        f"  {'#':<5}{'Bits[13:16]':<13}{'Val':>5}"
        f"{'Lista':>7}{'Suma':>6}{'C1':>4}{'C2':>4}  Estado\n")
    output.insert('end', f"  {SEP}\n")

    # Una fila por cada trama evaluada
    for d in fsm.detalles:
        icono  = '✅' if d['valida'] else '❌'
        estado = 'VÁLIDA  ' if d['valida'] else 'INVÁLIDA'
        c1     = '✓' if d['cond1'] else '✗'   # C1: valor par
        c2     = '✓' if d['cond2'] else '✗'   # C2: suma múltiplo de 5
        output.insert('end',
            f"  T{d['trama']:<4}{d['bits_control']:<13}"
            f"{d['valor_control']:>5}{d['valor_lista']:>7}"
            f"{d['suma']:>6}{c1:>4}{c2:>4}  {icono} {estado}\n")

    # ── Paso 6: Mostrar el resumen global de la transmisión ───────────────
    r = fsm.obtener_resumen()
    output.insert('end', f"  {SEP}\n")
    output.insert('end', f"  Total tramas procesadas : {r['total']}\n")
    output.insert('end', f"  Tramas válidas          : {r['validas']}\n")
    output.insert('end', f"  Tramas inválidas        : {r['invalidas']}\n")
    output.insert('end', f"  Porcentaje de error     : {r['porcentaje_error']:.2f}%\n")
    output.insert('end', f"  {SEP}\n")

    # Veredicto final (el umbral es ESTRICTAMENTE menor al 20%)
    if r['correcta']:
        output.insert('end', "  ✅ TRANSMISIÓN CORRECTA  (error < 20%)\n")
    else:
        output.insert('end', "  ⚠️  TRANSMISIÓN INCORRECTA (error ≥ 20%)\n")
    output.insert('end', f"{'═'*64}\n")


# ══════════════════════════════════════════════════════════
# SECCIÓN 5 — INTERFAZ GRÁFICA (GUI)
# ══════════════════════════════════════════════════════════

def main():
    """
    Construye y lanza la interfaz gráfica del módulo de tramas.

    Permite al usuario:
    - Elegir el número de tramas a evaluar (entre 5 y 20).
    - Ingresar un valor de 4 bits de validación por cada trama.
    - Ingresar cada trama como cadena de 32 bits.
    - Ejecutar la FSM y visualizar los resultados completos.
    """
    root = tk.Tk()
    root.title("📡 Validador de Tramas — Máquina de Estados Finita")
    root.geometry("870x810")
    root.configure(bg="#f4f4f4")

    # ── Encabezado ────────────────────────────────────────────────────────
    tk.Label(root,
             text="📡 Validador de Tramas TCP/IP  —  Máquina de Estados Finita",
             font=('Arial', 13, 'bold'), bg="#f4f4f4").pack(pady=(10, 2))

    tk.Label(root,
             text="Bits de control: índices 13–16 (0-indexed)  |  "
                  "C1: valor par  |  C2: (valor + lista) mod 5 = 0",
             font=('Arial', 9), fg="#555555", bg="#f4f4f4").pack(pady=(0, 8))

    # ── Configuración: número de tramas ───────────────────────────────────
    cfg = tk.Frame(root, bg="#f4f4f4")
    cfg.pack(pady=4)

    tk.Label(cfg, text="Número de tramas (5 – 20):",
             font=('Arial', 11), bg="#f4f4f4").grid(row=0, column=0, padx=6)

    # Variable que almacena el número de tramas elegido por el usuario
    n_var = tk.StringVar(value="5")   # 5 es el mínimo permitido por el enunciado
    tk.Entry(cfg, textvariable=n_var, width=4,
             font=('Consolas', 12), justify='center').grid(row=0, column=1, padx=4)

    # Listas que almacenan referencias a los Entry widgets generados dinámicamente.
    # Se crean vacías aquí y se rellenan en generar_campos().
    valid_entries = []   # Entradas para la lista de validación
    trama_entries = []   # Entradas para las tramas de 32 bits

    # ── Área de entradas con scroll ───────────────────────────────────────
    # Usamos tk.Canvas + tk.Scrollbar para que la ventana soporte entre
    # 5 y 20 filas sin crecer descontroladamente.
    wrap = tk.Frame(root, bg="#f4f4f4")
    wrap.pack(fill='both', expand=True, padx=10, pady=4)

    canvas    = tk.Canvas(wrap, bg="#f4f4f4", height=320)
    scrollbar = tk.Scrollbar(wrap, orient='vertical', command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    scrollbar.pack(side='right', fill='y')
    canvas.pack(side='left', fill='both', expand=True)

    # Frame interior del Canvas: aquí se colocan los campos de entrada
    inner = tk.Frame(canvas, bg="#f4f4f4")
    cwin  = canvas.create_window((0, 0), window=inner, anchor='nw')

    # Actualizamos la región desplazable cuando cambia el contenido del inner frame
    inner.bind('<Configure>',
               lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

    # Ajustamos el ancho del inner frame al ancho actual del Canvas
    canvas.bind('<Configure>',
                lambda e: canvas.itemconfig(cwin, width=e.width))

    # ── Función para generar los campos de entrada dinámicamente ──────────
    def generar_campos():
        """
        Lee el número de tramas ingresado por el usuario y genera
        dinámicamente los Entry widgets para la lista de validación y
        las tramas de 32 bits.

        Elimina los campos anteriores antes de crear los nuevos, lo que
        permite al usuario cambiar el número de tramas sin reiniciar
        la ventana.
        """
        # Eliminamos los widgets anteriores del frame interior
        for w in inner.winfo_children():
            w.destroy()
        valid_entries.clear()
        trama_entries.clear()

        # Leemos el número de tramas y lo limitamos al rango [5, 20]
        try:
            n = int(n_var.get())
        except ValueError:
            n = 5
        # max(5, min(20, n)) garantiza 5 ≤ n ≤ 20
        n = max(5, min(20, n))

        # ── Encabezados de columnas ───────────────────────────────────────
        for col, (texto, ancho) in enumerate(
                [("#", 5), ("Lista validación (4 bits)", 22), ("Trama (32 bits)", 44)]):
            tk.Label(inner, text=texto,
                     font=('Arial', 10, 'bold'), bg="#cce5ff",
                     width=ancho, relief='ridge'
                     ).grid(row=0, column=col, padx=3, pady=3, sticky='ew')

        # ── Una fila de entrada por trama ─────────────────────────────────
        for i in range(n):
            # Etiqueta con el número de trama
            tk.Label(inner, text=f"T{i+1}",
                     font=('Consolas', 10), bg="#f4f4f4", width=5
                     ).grid(row=i+1, column=0, padx=3, pady=2)

            # Campo para el valor de la lista de validación (4 bits)
            ev = tk.Entry(inner, width=14,
                          font=('Consolas', 12), justify='center')
            ev.grid(row=i+1, column=1, padx=6, pady=2)
            valid_entries.append(ev)

            # Campo para la trama de 32 bits
            et = tk.Entry(inner, width=44,
                          font=('Consolas', 10), justify='center')
            et.grid(row=i+1, column=2, padx=4, pady=2)
            trama_entries.append(et)

    # ── Botón "Generar campos" ─────────────────────────────────────────────
    tk.Button(cfg, text="⚙ Generar campos",
              font=('Arial', 10), bg="#ffe0b2",
              command=generar_campos
              ).grid(row=0, column=2, padx=10)

    # Generamos los campos iniciales con el valor por defecto (5 tramas)
    generar_campos()

    # ── Área de resultados ────────────────────────────────────────────────
    tk.Label(root, text="📋 Resultados:",
             font=('Arial', 11, 'bold'), bg="#f4f4f4").pack(anchor='w', padx=12)

    # Widget de texto con scroll para mostrar los resultados de la FSM
    output = scrolledtext.ScrolledText(
        root, width=84, height=15,
        font=('Consolas', 10), bg='#ffffff', bd=2, relief='solid')
    output.pack(padx=10, pady=(0, 6))

    # ── Botones de acción ─────────────────────────────────────────────────
    btns = tk.Frame(root, bg="#f4f4f4")
    btns.pack(pady=6)

    # Botón principal: ejecuta la FSM con los datos ingresados
    tk.Button(btns,
              text="🧾 Evaluar transmisión (FSM)",
              font=('Arial', 11, 'bold'), bg="#d0f0c0",
              command=lambda: procesar(valid_entries, trama_entries, output)
              ).pack(side='left', padx=8)

    # Botón para volver al menú principal (main.py)
    # __import__('main') carga el módulo main.py en tiempo de ejecución
    # y .main() llama a su función principal para reabrir el menú.
    tk.Button(btns,
              text="⏹ Volver al menú",
              font=('Arial', 11), bg="#ffcccc",
              command=lambda: [root.destroy(), __import__('main').main()]
              ).pack(side='left', padx=8)

    root.mainloop()


# ── Punto de entrada directo ──────────────────────────────────────────
# Permite ejecutar el módulo de tramas directamente (sin pasar por main.py)
# ejecutando: python tramas_module.py
if __name__ == "__main__":
    main()
