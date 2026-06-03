# ============================================================
# gramatica_module.py
# Módulo de Gramática Libre de Contexto (CFG) 
# ============================================================

import tkinter as tk
from tkinter import simpledialog, scrolledtext
import random


# ══════════════════════════════════════════════════════════
# SECCIÓN 1 — CONSTRUCCIÓN DE LA GRAMÁTICA
# ══════════════════════════════════════════════════════════

def construir_gramatica(no_terminales_str, terminales_str, S_str, producciones_str):
    """
    Construye el diccionario que representa la gramática G = (V, T, S, P)
    a partir de los textos ingresados por el usuario en la interfaz.

    Una Gramática Libre de Contexto (CFG) se define formalmente como:
        G = (V, T, S, P)
        V → Conjunto de símbolos no terminales (variables)
        T → Conjunto de símbolos terminales
        S → Símbolo inicial (S ∈ V)
        P → Conjunto de reglas de producción: A → α,
            donde A ∈ V  y  α ∈ (V ∪ T)*

    Args:
        no_terminales_str (str): No terminales separados por espacio.
                                 Ejemplo: "S A B"
        terminales_str    (str): Terminales separados por espacio.
                                 Ejemplo: "a b c"
        S_str             (str): Símbolo inicial.
                                 Ejemplo: "S"
        producciones_str  (str): Reglas de producción, una por línea.
                                 Formato: "A -> símbolo1 símbolo2 ..."
                                 Ejemplo: "S -> a A\nA -> b"

    Returns:
        dict: Diccionario con las claves:
              'V' → set de no terminales
              'T' → set de terminales
              'S' → string con el símbolo inicial
              'P' → dict {NT: [[s1, s2, ...], ...]}, donde cada valor es
                    la lista de cuerpos de producción del no terminal NT.
    """
    # split() divide por espacios en blanco (espacios, tabs, saltos de línea)
    # set(...) elimina duplicados en caso de que el usuario los ingrese
    V = set(no_terminales_str.split())
    T = set(terminales_str.split())

    # strip() elimina espacios o saltos de línea al inicio/fin del símbolo inicial
    S = S_str.strip()

    # Construimos el diccionario de producciones P.
    # Estructura interna: { 'NT': [ ['s1','s2'], ['s3'], ... ], ... }
    # Cada valor es una lista de producciones; cada producción es una lista de símbolos.
    P = {}
    for linea in producciones_str.splitlines():
        linea = linea.strip()

        # Saltamos líneas vacías y líneas sin la flecha '->'
        if not linea or '->' not in linea:
            continue

        # split('->', 1) hace una sola partición, en caso de que '->'
        # aparezca dentro del cuerpo (aunque es poco común en CFG simples)
        izquierda, derecha = linea.split('->', 1)

        NT     = izquierda.strip()       # No terminal del lado izquierdo
        cuerpo = derecha.strip().split() # Lista de símbolos del cuerpo

        # setdefault garantiza que la clave NT exista antes de agregar
        # Así, un mismo NT puede tener múltiples producciones (A → α | β | ...)
        P.setdefault(NT, []).append(cuerpo)

    return {'V': V, 'T': T, 'S': S, 'P': P}


# ══════════════════════════════════════════════════════════
# SECCIÓN 2 — VALIDACIÓN DE LA GRAMÁTICA
# ══════════════════════════════════════════════════════════

def validar_gramatica(g):
    """
    Verifica que la gramática G = (V, T, S, P) sea consistente antes
    de realizar cualquier operación sobre ella.

    Comprobaciones realizadas:
      1. V no está vacío.
      2. T no está vacío.
      3. S pertenece a V.
      4. V y T no comparten símbolos (serían ambiguos).
      5. S tiene al menos una producción definida.

    Args:
        g (dict): Gramática construida por construir_gramatica().

    Returns:
        (bool, str): Tupla donde:
                     - El bool indica si la gramática es válida.
                     - El str contiene el mensaje de error (vacío si es válida).
    """
    # Verificamos que el conjunto de no terminales no esté vacío
    if not g['V']:
        return False, "El conjunto de no terminales V está vacío."

    # Verificamos que el conjunto de terminales no esté vacío
    if not g['T']:
        return False, "El conjunto de terminales T está vacío."

    # El símbolo inicial debe pertenecer a V (requerimiento fundamental de CFG)
    if g['S'] not in g['V']:
        return False, f"El símbolo inicial '{g['S']}' no pertenece a V."

    # V y T deben ser conjuntos disjuntos: un símbolo no puede ser
    # al mismo tiempo terminal y no terminal
    comunes = g['V'] & g['T']   # intersección de conjuntos
    if comunes:
        return False, f"V y T comparten símbolos: {comunes}. Deben ser disjuntos."

    # El símbolo inicial debe tener al menos una producción
    if g['S'] not in g['P']:
        return False, f"El símbolo inicial '{g['S']}' no tiene producciones definidas."

    return True, ""   # Gramática válida, sin errores


# ══════════════════════════════════════════════════════════
# SECCIÓN 3 — VERIFICACIÓN DE PERTENENCIA A LA GRAMÁTICA
# ══════════════════════════════════════════════════════════

def pertenece_frase(frase_str, gramatica, max_profundidad=20):
    """
    Determina si una frase puede ser derivada a partir del símbolo
    inicial S, es decir, si pertenece al lenguaje L(G).

    ─── Método: Backtracking con Derivación Izquierda ───────────────

    La derivación izquierda siempre expande el no terminal más a la
    izquierda de la forma sentencial actual. Esto garantiza una
    búsqueda sistemática y evita derivaciones equivalentes duplicadas.

    Pasos del algoritmo:
      1. Partimos de la forma sentencial [S].
      2. Encontramos el primer no terminal en la sentencia actual.
      3. Probamos cada producción de ese no terminal (backtracking).
      4. Si la nueva forma sentencial es igual a la frase objetivo
         Y solo contiene terminales → éxito (pertenece).
      5. Si la sentencia tiene solo terminales pero ≠ objetivo → falla.
      6. Si se supera max_profundidad → falla (evita bucles infinitos).

    Args:
        frase_str      (str): Frase a verificar, símbolos separados por espacio.
                              Ejemplo: "a a b"  o  "America es un continente"
        gramatica      (dict): La gramática G construida por construir_gramatica().
        max_profundidad(int): Límite de pasos de derivación. Con 20 se manejan
                              frases que requieran hasta 20 expansiones de NT.

    Returns:
        bool: True si la frase ∈ L(G), False en caso contrario.
    """
    # Dividimos la frase objetivo en lista de símbolos individuales
    # Ejemplo: "a a b" → ['a', 'a', 'b']
    objetivo = frase_str.split()

    def backtrack(sentencia, profundidad):
        """
        Función recursiva interna: intenta derivar 'objetivo' desde 'sentencia'.

        Args:
            sentencia   (list[str]): Forma sentencial actual de la derivación.
            profundidad (int):       Número de expansiones realizadas hasta aquí.

        Returns:
            bool: True si se puede alcanzar 'objetivo' desde 'sentencia'.
        """
        # ── Caso base: límite de profundidad alcanzado ────────────────────
        # Detenemos la búsqueda para evitar recursión infinita en gramáticas
        # con ciclos (ej: A → A o A → B, B → A)
        if profundidad > max_profundidad:
            return False

        # ── Caso base: encontramos el objetivo ────────────────────────────
        # La sentencia coincide con el objetivo Y es pura de terminales
        if sentencia == objetivo and all(s in gramatica['T'] for s in sentencia):
            return True

        # ── Caso base: sentencia terminal pero no coincide ────────────────
        # No quedan no terminales que expandir y no llegamos al objetivo
        if all(s in gramatica['T'] for s in sentencia):
            return False

        # ── Paso recursivo: expansión izquierda ───────────────────────────
        # Buscamos el PRIMER no terminal en la sentencia actual
        for idx, simbolo in enumerate(sentencia):
            if simbolo in gramatica['V']:

                # Probamos cada producción disponible para este no terminal
                for produccion in gramatica['P'].get(simbolo, []):
                    # Reemplazamos el NT por el cuerpo de la producción
                    # Ejemplo: ['a', 'A', 'b'] con A → ['x', 'y']
                    #        → ['a', 'x', 'y', 'b']
                    nueva = sentencia[:idx] + produccion + sentencia[idx+1:]

                    # Llamada recursiva con la nueva forma sentencial
                    if backtrack(nueva, profundidad + 1):
                        return True   # Derivación exitosa encontrada

                # Si ninguna producción del NT izquierdo lleva al objetivo,
                # no hay derivación izquierda que funcione desde aquí
                return False

        # No se encontró ningún NT en la sentencia (solo terminales, ya tratado)
        return False

    # Iniciamos la búsqueda desde la forma sentencial inicial [S]
    return backtrack([gramatica['S']], 0)


# ══════════════════════════════════════════════════════════
# SECCIÓN 4 — GENERACIÓN DE FRASES
# ══════════════════════════════════════════════════════════

def generar_frases(gramatica, n=10, max_profundidad=20):
    """
    Genera hasta n frases ÚNICAS pertenecientes al lenguaje L(G)
    mediante derivaciones aleatorias desde el símbolo inicial S.

    ─── Algoritmo ───────────────────────────────────────────────────

    Por cada intento:
      1. Partimos de la sentencia [S].
      2. Encontramos el primer no terminal en la sentencia.
      3. Elegimos UNA PRODUCCIÓN AL AZAR (esto introduce variedad).
      4. Repetimos hasta que la sentencia sea pura de terminales
         o se alcance max_profundidad.
      5. Si la sentencia final tiene solo terminales, la guardamos
         como frase válida.

    El uso de un set para acumular frases garantiza que no haya
    duplicados, aunque la gramática genere la misma frase varias veces.

    Args:
        gramatica      (dict): La gramática G.
        n              (int):  Número de frases a generar (10 a 50).
        max_profundidad(int):  Límite de pasos por derivación.

    Returns:
        list[str]: Lista ordenada de frases generadas (puede ser menor
                   que n si la gramática tiene un lenguaje muy pequeño).
    """
    frases_unicas = set()    # set para eliminar duplicados automáticamente

    # Número máximo de intentos: suficiente incluso para gramáticas restrictivas
    max_intentos = max(n * 20, 200)
    intentos = 0

    while len(frases_unicas) < n and intentos < max_intentos:
        intentos += 1

        # Comenzamos siempre desde el símbolo inicial
        sentencia   = [gramatica['S']]
        profundidad = 0

        # Derivamos mientras queden no terminales y no superemos el límite
        while any(s in gramatica['V'] for s in sentencia) and profundidad < max_profundidad:

            # Encontramos el primer no terminal (derivación izquierda)
            # next(...) busca el índice del primer elemento de sentencia que esté en V
            idx = next(i for i, s in enumerate(sentencia) if s in gramatica['V'])
            nt  = sentencia[idx]

            # Obtenemos las producciones de este NT
            producciones = gramatica['P'].get(nt, [])
            if not producciones:
                break   # El NT no tiene producciones → derivación fallida

            # Elegimos una producción AL AZAR para generar variedad
            # random.choice selecciona un elemento al azar de la lista
            prod_elegida = random.choice(producciones)

            # Reemplazamos el NT por su producción elegida
            sentencia = sentencia[:idx] + prod_elegida + sentencia[idx+1:]
            profundidad += 1

        # Si la sentencia final tiene solo terminales, es una frase válida del lenguaje
        if all(s in gramatica['T'] for s in sentencia):
            # ' '.join(sentencia) une la lista con espacios: ['a','b'] → 'a b'
            frases_unicas.add(' '.join(sentencia))

    # Devolvemos las frases ordenadas (para presentación consistente en el informe)
    return sorted(frases_unicas)


# ══════════════════════════════════════════════════════════
# SECCIÓN 5 — INTERFAZ GRÁFICA (GUI)
# ══════════════════════════════════════════════════════════

def main():
    """
    Construye y lanza la interfaz gráfica del módulo de gramática.

    Permite al usuario:
    - Ingresar y MODIFICAR los cuatro componentes de G = (V, T, S, P).
    - Verificar si una frase pertenece al lenguaje L(G).
    - Generar entre 10 y 50 frases del lenguaje.
    - Limpiar todos los campos para ingresar una nueva gramática.
    """
    root = tk.Tk()
    root.title("📚 Módulo Gramática — G = (V, T, S, P)")
    root.geometry("740x810")
    root.configure(bg="#f4f4f4")

    # ── Encabezado ────────────────────────────────────────────────────────
    tk.Label(root,
             text="📚 Gramática Libre de Contexto  G = (V, T, S, P)",
             font=('Arial', 13, 'bold'), bg="#f4f4f4").pack(pady=(10, 2))
    tk.Label(root,
             text="Ingrese o modifique los componentes. Los campos son editables en cualquier momento.",
             font=('Arial', 9), fg="#555555", bg="#f4f4f4").pack(pady=(0, 6))

    # ── Campo: No terminales V ────────────────────────────────────────────
    tk.Label(root,
             text="🔤 No terminales V  (separados por espacio, ej: S A B)",
             font=('Arial', 11), bg="#f4f4f4").pack(padx=10, anchor='w', pady=(6, 0))
    nt_entry = tk.Entry(root, width=62, font=('Consolas', 12), justify='center')
    nt_entry.pack(padx=10)

    # ── Campo: Terminales T ───────────────────────────────────────────────
    tk.Label(root,
             text="🔡 Terminales T  (separados por espacio, ej: a b c)",
             font=('Arial', 11), bg="#f4f4f4").pack(padx=10, anchor='w', pady=(8, 0))
    t_entry = tk.Entry(root, width=62, font=('Consolas', 12), justify='center')
    t_entry.pack(padx=10)

    # ── Campo: Símbolo inicial S ──────────────────────────────────────────
    tk.Label(root,
             text="🎯 Símbolo inicial S  (debe pertenecer a V)",
             font=('Arial', 11), bg="#f4f4f4").pack(padx=10, anchor='w', pady=(8, 0))
    s_entry = tk.Entry(root, width=20, font=('Consolas', 12), justify='center')
    s_entry.pack(padx=10)

    # ── Campo: Producciones P ─────────────────────────────────────────────
    tk.Label(root,
             text="📐 Producciones P  (una por línea, formato: A -> s1 s2 ...)",
             font=('Arial', 11), bg="#f4f4f4").pack(padx=10, anchor='w', pady=(8, 0))
    prod_text = scrolledtext.ScrolledText(root, width=62, height=6,
                                           font=('Consolas', 10))
    prod_text.pack(padx=10, pady=(0, 8))

    # ── Campo: Número de frases a generar ─────────────────────────────────
    # El enunciado pide "entre 10 y 50 frases"; aquí el usuario lo elige.
    n_frame = tk.Frame(root, bg="#f4f4f4")
    n_frame.pack(padx=10, anchor='w', pady=(0, 4))
    tk.Label(n_frame,
             text="🔢 Frases a generar (10 – 50):",
             font=('Arial', 11), bg="#f4f4f4").pack(side='left')
    n_frases_var = tk.StringVar(value="10")   # Valor inicial: mínimo requerido
    tk.Entry(n_frame, textvariable=n_frases_var, width=5,
             font=('Consolas', 12), justify='center').pack(side='left', padx=6)

    # ── Área de resultados ────────────────────────────────────────────────
    output = scrolledtext.ScrolledText(root, width=85, height=13,
                                        font=('Consolas', 11),
                                        bg='#ffffff', bd=2, relief='solid')
    output.pack(padx=10, pady=(6, 6))

    # ──────────────────────────────────────────────────────────────────────
    # Función auxiliar: leer campos y validar la gramática
    # ──────────────────────────────────────────────────────────────────────
    def leer_y_validar():
        """
        Lee los cuatro campos de la GUI, construye el diccionario de la
        gramática G y verifica su consistencia.

        Si hay errores (ej: S no está en V), los muestra en el área de
        resultados y devuelve None para detener la operación solicitada.

        Returns:
            dict | None: La gramática si es válida, None si hay errores.
        """
        # Construimos G a partir de los textos de los Entry/ScrolledText
        g = construir_gramatica(
            nt_entry.get(),
            t_entry.get(),
            s_entry.get(),
            prod_text.get('1.0', 'end')  # '1.0' = línea 1, col 0 (inicio)
        )

        # Validamos la gramática y mostramos el error si hay alguno
        valida, mensaje = validar_gramatica(g)
        if not valida:
            output.delete('1.0', 'end')
            output.insert('end', f"⚠️  Gramática inválida: {mensaje}\n"
                                  f"    Corrija los campos y vuelva a intentarlo.\n")
            return None

        return g

    # ──────────────────────────────────────────────────────────────────────
    # Acción: Verificar si una frase pertenece a la gramática
    # ──────────────────────────────────────────────────────────────────────
    def accion_verificar():
        """
        Lee y valida la gramática, pide una frase al usuario mediante un
        diálogo modal y muestra si la frase pertenece a L(G) o no.
        """
        output.delete('1.0', 'end')

        # Intentamos construir y validar la gramática
        g = leer_y_validar()
        if g is None:
            return   # leer_y_validar ya mostró el error

        # askstring abre un cuadro de diálogo para ingresar la frase
        frase = simpledialog.askstring(
            "Verificación de frase",
            "Ingrese la frase a verificar\n"
            "(símbolos separados por espacio):"
        )
        if frase is None:
            return   # El usuario presionó Cancelar

        frase = frase.strip()
        if not frase:
            output.insert('end', "⚠️  La frase ingresada está vacía.\n")
            return

        # Verificamos pertenencia mediante backtracking
        resultado = pertenece_frase(frase, g)

        # Mostramos el resultado de forma clara
        output.insert('end', f"{'═'*55}\n")
        output.insert('end', f"  Frase evaluada : \"{frase}\"\n")
        output.insert('end', f"  Símbolo inicial: {g['S']}\n")
        output.insert('end', f"  No terminales  : {sorted(g['V'])}\n")
        output.insert('end', f"  Terminales     : {sorted(g['T'])}\n")
        output.insert('end', f"{'─'*55}\n")
        if resultado:
            output.insert('end', "  Resultado : ✅  La frase PERTENECE a L(G)\n")
        else:
            output.insert('end', "  Resultado : ❌  La frase NO PERTENECE a L(G)\n")
        output.insert('end', f"{'═'*55}\n")

    # ──────────────────────────────────────────────────────────────────────
    # Acción: Generar frases del lenguaje L(G)
    # ──────────────────────────────────────────────────────────────────────
    def accion_generar():
        """
        Lee y valida la gramática, genera entre 10 y 50 frases del
        lenguaje L(G) y las muestra numeradas en el área de resultados.

        Si la gramática no puede generar todas las frases solicitadas
        (lenguaje finito o muy pequeño), informa cuántas se lograron.
        """
        output.delete('1.0', 'end')

        # Intentamos construir y validar la gramática
        g = leer_y_validar()
        if g is None:
            return

        # Leemos el número de frases deseado con clamp [10, 50]
        try:
            n = int(n_frases_var.get())
        except ValueError:
            n = 10
        n = max(10, min(50, n))   # Garantizamos que 10 ≤ n ≤ 50

        # Generamos las frases mediante derivaciones aleatorias
        frases = generar_frases(g, n=n)

        # Mostramos los resultados
        output.insert('end', f"{'═'*55}\n")
        output.insert('end', f"  Frases de L(G) — solicitadas: {n}\n")
        output.insert('end', f"{'─'*55}\n")

        if frases:
            for i, f in enumerate(frases, 1):
                output.insert('end', f"  {i:>3}.  {f}\n")
            output.insert('end', f"{'─'*55}\n")
            output.insert('end', f"  Frases generadas: {len(frases)}\n")

            # Avisamos si se generaron MENOS de las solicitadas
            if len(frases) < n:
                output.insert('end',
                    f"\n  ⚠️  Solo se generaron {len(frases)} frases únicas.\n"
                    f"      La gramática tiene un lenguaje pequeño o la\n"
                    f"      profundidad máxima ({20}) es insuficiente.\n")
        else:
            # Si no se generó ninguna frase, orientamos al usuario
            output.insert('end',
                "  ⚠️  No se pudo generar ninguna frase.\n"
                "      Revise que las producciones permitan llegar\n"
                "      a sentencias de solo terminales desde S.\n")

        output.insert('end', f"{'═'*55}\n")

    # ──────────────────────────────────────────────────────────────────────
    # Acción: Limpiar todos los campos
    # ──────────────────────────────────────────────────────────────────────
    def accion_limpiar():
        """
        Limpia todos los campos de entrada y el área de resultados,
        dejando la interfaz lista para ingresar una nueva gramática.
        
        Esto cubre el punto 1 del enunciado: "debe permitir hacer
        modificaciones a los datos ingresados".
        """
        nt_entry.delete(0, 'end')        # Limpia el campo de no terminales
        t_entry.delete(0, 'end')         # Limpia el campo de terminales
        s_entry.delete(0, 'end')         # Limpia el campo del símbolo inicial
        prod_text.delete('1.0', 'end')   # Limpia el área de producciones
        output.delete('1.0', 'end')      # Limpia el área de resultados
        n_frases_var.set("10")           # Restaura el número de frases a 10

    # ── Botones de acción ─────────────────────────────────────────────────
    btn_frame = tk.Frame(root, bg="#f4f4f4")
    btn_frame.pack(pady=10)

    # Botón: Verificar si una frase pertenece al lenguaje L(G)
    tk.Button(btn_frame,
              text="🧪 Verificar frase",
              command=accion_verificar,
              font=('Arial', 11), bg="#d0eaff", width=17
              ).pack(side='left', padx=4)

    # Botón: Generar n frases del lenguaje L(G) de forma aleatoria
    tk.Button(btn_frame,
              text="🎲 Generar frases",
              command=accion_generar,
              font=('Arial', 11), bg="#c1f0c1", width=17
              ).pack(side='left', padx=4)

    # Botón: Limpiar todos los campos para ingresar una gramática nueva
    tk.Button(btn_frame,
              text="🗑 Limpiar todo",
              command=accion_limpiar,
              font=('Arial', 11), bg="#fff3cd", width=17
              ).pack(side='left', padx=4)

    # Botón: Volver al menú principal (main.py)
    # __import__('main') carga el módulo main.py en tiempo de ejecución
    # y .main() llama a su función para reabrir el menú principal
    tk.Button(btn_frame,
              text="⏹ Volver al menú",
              command=lambda: [root.destroy(), __import__('main').main()],
              font=('Arial', 11), bg="#ffcccc", width=17
              ).pack(side='left', padx=4)

    root.mainloop()


# Punto de entrada si se ejecuta el módulo directamente (sin main.py)
if __name__ == "__main__":
    main()
