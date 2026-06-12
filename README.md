# Proyecto Final — Matemáticas Discretas II

**Universidad del Valle**  
Profesor: Julián Andrés Rodas Laverde · Semana 17 · 2026-I  
Integrantes:  
Juan Esteban Aguirre Castañeda - 202459676 - 3743  
Bryan Steven Ospina - 202459353 - 3743  
Lenguaje: Python 3 (interfaz gráfica con `tkinter`) 


---

## Tabla de contenido

1. [Estructura del proyecto](#estructura-del-proyecto)
2. [Parte 1 — Gramática Libre de Contexto](#parte-1--gramática-libre-de-contexto-g--v-t-s-p)
3. [Parte 2 — Máquina de Estados Finita (FSM)](#parte-2--máquina-de-estados-finita-fsm)
4. [Casos de prueba](#casos-de-prueba)
5. [Análisis de cumplimiento del enunciado](#análisis-de-cumplimiento-del-enunciado)
6. [Librerías utilizadas](#librerías-utilizadas)
7. [Cómo ejecutar](#cómo-ejecutar)

---

## Estructura del proyecto

```
PROYECTO-DISCRETAS-II-main/
└── Proyecto discretas II MAIN/
    ├── main.py                         # Menú principal (lanza los dos módulos)
    ├── gramatica_module.py             # Módulo de Gramática Libre de Contexto
    ├── tramas_module.py                # Módulo de Tramas / Máquina de Estados Finita
    ├── EJEMPLOS DATOS GRAMATICA/
    │   ├── #1.txt                      # Caso de prueba: lenguaje natural
    │   ├── #2.txt                      # Caso de prueba: a^n b^n
    │   └── #3.txt                      # Caso de prueba: a^n b
    └── EJEMPLOS DATOS TRAMA/
        ├── #1.txt                      # Caso de prueba: 5 tramas
        ├── #2.txt                      # Caso de prueba: 5 tramas (mix)
        └── #3.txt                      # Caso de prueba: 10 tramas
```

---

## Parte 1 — Gramática Libre de Contexto G = (V, T, S, P)

### Definición formal

Una Gramática Libre de Contexto se define formalmente como la tupla:

```
G = (V, T, S, P)
```

| Componente | Notación | Descripción |
|---|---|---|
| No terminales | V | Conjunto de variables o símbolos de trabajo (ej: `S`, `A`, `NP`, `VP`) |
| Terminales | T | Símbolos del alfabeto final que forman las frases del lenguaje |
| Símbolo inicial | S | No terminal desde el que arrancan todas las derivaciones (`S ∈ V`) |
| Producciones | P | Reglas de la forma `A → α`, con `A ∈ V` y `α ∈ (V ∪ T)*` |

### Funciones implementadas (`gramatica_module.py`)

#### `construir_gramatica(no_terminales, terminales, S, producciones)`

Recibe los cuatro campos de texto del usuario y construye el diccionario interno de la gramática. Cada producción se representa como una lista de símbolos; el no terminal izquierdo es la clave del diccionario `P`. Ejemplo de estructura interna:

```python
{
  'V': {'S', 'A'},
  'T': {'a', 'b'},
  'S': 'S',
  'P': {'S': [['a', 'S', 'b'], ['a', 'b']]}
}
```

#### `validar_gramatica(g)`

Verifica la consistencia de la gramática antes de cualquier operación. Comprueba:
- Que `V` y `T` no estén vacíos.
- Que `S ∈ V`.
- Que `V ∩ T = ∅` (deben ser conjuntos disjuntos).
- Que `S` tenga al menos una producción definida.

Devuelve una tupla `(bool, mensaje_error)`.

#### `pertenece_frase(frase, gramatica, max_profundidad=20)`

Determina si una frase pertenece a `L(G)` mediante **backtracking con derivación izquierda**. El algoritmo siempre expande el no terminal más a la izquierda de la forma sentencial, garantizando una búsqueda sistemática. El parámetro `max_profundidad` limita la recursión para evitar ciclos infinitos en gramáticas con producciones recursivas.

**Algoritmo paso a paso:**
1. Parte de la forma sentencial `[S]`.
2. Encuentra el primer no terminal en la sentencia actual.
3. Prueba cada producción disponible para ese no terminal (backtracking).
4. Si la sentencia resultante es igual al objetivo y solo contiene terminales → **éxito**.
5. Si la sentencia tiene solo terminales pero no coincide con el objetivo → **falla**.
6. Si se supera `max_profundidad` → **falla** (evita bucles).

#### `generar_frases(gramatica, n=10, max_profundidad=20)`

Genera hasta `n` frases **únicas** del lenguaje `L(G)` mediante derivaciones aleatorias. En cada paso usa `random.choice()` para seleccionar una producción al azar, lo que introduce variedad. Utiliza un `set` para eliminar duplicados automáticamente. Devuelve la lista ordenada alfabéticamente.

---

## Parte 2 — Máquina de Estados Finita (FSM)

### Descripción del problema

El protocolo TCP/IP académico utiliza tramas de **32 bits** (reducidas de 64 bits por fines pedagógicos). A partir del **bit 14** (notación 1-indexada, equivalente al índice 13 en Python 0-indexada) se ubican **4 bits de control** que deben cumplir dos condiciones para que la trama sea válida.

### Definición formal

```
M = (Q, Σ, δ, q₀, F)
```

| Elemento | Valor |
|---|---|
| **Q** (estados) | `{INICIO, LEYENDO_PREAMBULO, LEYENDO_CONTROL, TRAMA_VALIDA, TRAMA_INVALIDA, FIN_TRAMA}` |
| **Σ** (alfabeto) | `{0, 1}` — un bit individual por transición |
| **q₀** (estado inicial) | `INICIO` |
| **F** (estados de aceptación) | `{TRAMA_VALIDA, TRAMA_INVALIDA}` |
| **δ** (función de transición) | Implementada en `FSM.transicion()` |

### Descripción de los estados

| Estado | Rol | Detalles |
|---|---|---|
| `INICIO` | Estado inicial q₀ | Espera el primer bit de una nueva trama. Se vuelve a este estado entre tramas. |
| `LEYENDO_PREAMBULO` | Descarte de preámbulo | Consume los bits en posiciones 0–12 (irrelevantes para la validación). |
| `LEYENDO_CONTROL` | Captura del campo de control | Acumula los 4 bits de control (índices 13, 14, 15, 16 en 0-indexado). |
| `TRAMA_VALIDA` | Estado de aceptación | C1 y C2 se cumplen. El resultado se guarda en `_resultado_actual = True`. |
| `TRAMA_INVALIDA` | Estado de rechazo | Al menos una condición falla. Se guarda `_resultado_actual = False`. |
| `FIN_TRAMA` | Cola de trama | Consume los bits 17–31 restantes sin modificar el veredicto ya registrado. |

### Tabla de transiciones δ(q, evento) → q'

| Estado actual | Condición / Evento | Estado siguiente |
|---|---|---|
| `INICIO` | Cualquier bit (primer bit de trama) | `LEYENDO_PREAMBULO` |
| `LEYENDO_PREAMBULO` | `bit_pos < 13` | `LEYENDO_PREAMBULO` |
| `LEYENDO_PREAMBULO` | `bit_pos == 13` | `LEYENDO_CONTROL` |
| `LEYENDO_CONTROL` | bits acumulados `< 4` | `LEYENDO_CONTROL` |
| `LEYENDO_CONTROL` | 4 bits y `C1 ∧ C2` verdaderas | `TRAMA_VALIDA` |
| `LEYENDO_CONTROL` | 4 bits y `¬(C1 ∧ C2)` | `TRAMA_INVALIDA` |
| `TRAMA_VALIDA` | Cualquier bit | `FIN_TRAMA` |
| `TRAMA_INVALIDA` | Cualquier bit | `FIN_TRAMA` |
| `FIN_TRAMA` | `bit_pos < 31` | `FIN_TRAMA` |
| `FIN_TRAMA` | `bit_pos == 31` | `INICIO` (nueva trama) |

### Condiciones de validez de una trama

Sea `B` el valor entero de `trama[13:17]` (4 bits de control) y `L` el valor de la lista de validación para la trama `i`:

- **C1:** `B mod 2 = 0` → B es par (múltiplo de 2).  
  Ejemplo: bits `1100` → B = 12 → `12 mod 2 = 0` ✓
- **C2:** `(B + L) mod 5 = 0` → la suma es múltiplo de 5.  
  Ejemplo: B = 12, L = 3 → `15 mod 5 = 0` ✓
- **Trama válida ⟺ C1 ∧ C2** (ambas deben cumplirse simultáneamente).
- **Transmisión correcta ⟺** `(tramas_inválidas / total) × 100 < 20` (umbral **estrictamente** menor al 20%).

### Métodos principales de la clase `FSM`

| Método | Descripción |
|---|---|
| `__init__(lista_validacion)` | Inicializa la FSM en q₀ con todos los contadores en cero. |
| `transicion(bit)` | Implementa δ. Recibe un bit (0 ó 1) y actualiza el estado actual. |
| `_evaluar_condiciones()` | Evalúa C1 y C2 sobre los 4 bits acumulados; transita a `TRAMA_VALIDA` o `TRAMA_INVALIDA`. |
| `_fin_trama()` | Registra el veredicto usando `_resultado_actual` y reinicia contadores para la siguiente trama. |
| `procesar_bit_a_bit(trama_str)` | Alimenta la FSM bit a bit con una trama de 32 caracteres `'0'`/`'1'`. |
| `obtener_resumen()` | Devuelve total, válidas, inválidas, porcentaje de error y veredicto final. |

> **Nota sobre `_resultado_actual`:** Cuando la FSM llega al bit 31 y ejecuta `_fin_trama()`, el estado ya es `FIN_TRAMA` (la transición `TRAMA_VALIDA → FIN_TRAMA` ocurrió en el bit 17). Por eso no se puede inferir el resultado del estado en ese momento; se usa `_resultado_actual` que fue guardado en `_evaluar_condiciones()` en el momento correcto.

---

## Casos de prueba

### Gramática — Caso 1: Lenguaje natural

```
V = {S, NP, VP}
T = {America, es, un, continente}
S = S
Producciones:
  S  → NP VP
  NP → America
  VP → es NP
  NP → un continente
```

| Frase evaluada | Resultado esperado | Resultado obtenido |
|---|---|---|
| `America es un continente` | ✅ Pertenece | ✅ Pertenece |
| `America es America` | ❌ No pertenece | ❌ No pertenece |
| `es un continente` | ❌ No pertenece | ❌ No pertenece |

Frases generadas: lenguaje finito de 1 elemento → `"America es un continente"`.

---

### Gramática — Caso 2: Lenguaje aⁿbⁿ

```
V = {S}
T = {a, b}
S = S
Producciones:
  S → a S b
  S → a b
```

| Frase evaluada | Resultado esperado | Resultado obtenido |
|---|---|---|
| `a b` | ✅ Pertenece | ✅ Pertenece |
| `a a b b` | ✅ Pertenece | ✅ Pertenece |
| `a a b` | ❌ No pertenece | ❌ No pertenece |

Frases generadas: `"a b"`, `"a a b b"`, `"a a a b b b"`, etc.

---

### Gramática — Caso 3: Lenguaje aⁿb

```
V = {S, A}
T = {a, b}
S = S
Producciones:
  S → a A
  A → a A
  A → b
```

| Frase evaluada | Resultado esperado | Resultado obtenido |
|---|---|---|
| `a b` | ✅ Pertenece | ✅ Pertenece |
| `a a a b` | ✅ Pertenece | ✅ Pertenece |
| `a a b b` | ❌ No pertenece | ❌ No pertenece |

Frases generadas: `"a b"`, `"a a b"`, `"a a a b"`, `"a a a a b"`, etc.

---

### Tramas FSM — Caso 1: 5 tramas (transmisión incorrecta)

| Trama | Lista valid. | Bits ctrl `[13:16]` | B (dec) | L (dec) | B+L | C1 (par) | C2 (×5) | Estado |
|---|---|---|---|---|---|---|---|---|
| T1 | `0001` (1) | `0010` | 2 | 1 | 3 | ✓ | ✗ | ❌ INVÁLIDA |
| T2 | `0011` (3) | `0110` | 6 | 3 | 9 | ✓ | ✗ | ❌ INVÁLIDA |
| T3 | `0100` (4) | `0011` | 3 | 4 | 7 | ✗ | ✗ | ❌ INVÁLIDA |
| T4 | `0000` (0) | `0101` | 5 | 0 | 5 | ✗ | ✓ | ❌ INVÁLIDA |
| T5 | `1000` (8) | `0001` | 1 | 8 | 9 | ✗ | ✗ | ❌ INVÁLIDA |

**Resultado:** 0 válidas / 5 tramas → error = 100% → ⚠️ **TRANSMISIÓN INCORRECTA**

---

### Tramas FSM — Caso 2: 5 tramas (mix de condiciones)

| Trama | Lista valid. | Bits ctrl `[13:16]` | B (dec) | L (dec) | B+L | C1 | C2 | Estado |
|---|---|---|---|---|---|---|---|---|
| T1 | `0001` (1) | `0010` | 2 | 1 | 3 | ✓ | ✗ | ❌ INVÁLIDA |
| T2 | `0010` (2) | `0011` | 3 | 2 | 5 | ✗ | ✓ | ❌ INVÁLIDA |
| T3 | `0001` (1) | `0000` | 0 | 1 | 1 | ✓ | ✗ | ❌ INVÁLIDA |
| T4 | `0010` (2) | `0100` | 4 | 2 | 6 | ✓ | ✗ | ❌ INVÁLIDA |
| T5 | `0001` (1) | `0001` | 1 | 1 | 2 | ✗ | ✗ | ❌ INVÁLIDA |

**Resultado:** 0 válidas / 5 tramas → error = 100% → ⚠️ **TRANSMISIÓN INCORRECTA**

---

### Tramas FSM — Caso 3: Ejemplo de trama válida

Para que una trama sea válida, sus 4 bits de control deben cumplir simultáneamente C1 y C2. Ejemplo:

| Bits control | B (dec) | Lista valid. | L (dec) | B+L | C1 `B%2=0` | C2 `(B+L)%5=0` | Estado |
|---|---|---|---|---|---|---|---|
| `0100` | 4 | `0001` | 1 | 5 | ✓ | ✓ | ✅ VÁLIDA |
| `1010` | 10 | `0000` | 0 | 10 | ✓ | ✓ | ✅ VÁLIDA |

Para una **transmisión correcta** (error < 20%) en 10 tramas, al menos 8 deben ser válidas.

---

## Análisis de cumplimiento del enunciado

### Módulo de Gramática

| Requisito | ¿Cumplido? | Dónde |
|---|---|---|
| Ingreso de V, T, S y P | ✅ | Campos `Entry`/`ScrolledText` en `main()` de `gramatica_module.py` |
| Modificación de datos | ✅ | Botón "Limpiar todo" + todos los campos son editables en cualquier momento |
| Verificar si una frase pertenece a la gramática | ✅ | Función `pertenece_frase()` con backtracking de derivación izquierda |
| Generar entre 10 y 50 frases | ✅ | Función `generar_frases()`; rango forzado con `max(10, min(50, n))` |
| Mínimo 3 casos de prueba | ✅ | Archivos `#1.txt`, `#2.txt`, `#3.txt` en `EJEMPLOS DATOS GRAMATICA/` |

### Módulo de Tramas FSM

| Requisito | ¿Cumplido? | Dónde |
|---|---|---|
| Definición formal de la FSM (Q, Σ, δ, q₀, F) | ✅ | Comentario de cabecera en `tramas_module.py` + clase `Estados` + clase `FSM` |
| Ingreso de tramas y lista de validación | ✅ | Campos generados dinámicamente en `main()` de `tramas_module.py` |
| Tramas de 5 a 20 | ✅ | `max(5, min(20, n))` en `generar_campos()` |
| Trama de 32 bits con validación en bit 14 | ✅ | `BIT_INICIO_CONTROL = 13` (0-indexado); extracción `trama[13:17]` |
| 4 bits de control | ✅ | `NUM_BITS_CONTROL = 4`; acumulados en `bits_control` |
| C1: bits de control son múltiplo de 2 | ✅ | `condicion1 = (valor_control % 2 == 0)` |
| C2: suma con lista de validación es múltiplo de 5 | ✅ | `condicion2 = ((valor_control + valor_lista) % 5 == 0)` |
| Error < 20% para transmisión correcta | ✅ | `correcta = porcentaje_error < 20.0` (umbral estricto) |
| Datos ingresados bit a bit | ✅ | Método `procesar_bit_a_bit()` — itera carácter a carácter |
| Diseño de la máquina de estados en el informe | ✅ | Tabla de transiciones completa en este README |
| Mínimo 3 casos de prueba | ✅ | Archivos `#1.txt`, `#2.txt`, `#3.txt` en `EJEMPLOS DATOS TRAMA/` |

> **Sobre la autenticidad de la FSM:** El enunciado advierte que muchos grupos resuelven los requerimientos sin implementar una FSM real. En este proyecto la clase `FSM` mantiene un estado explícito (`self.estado`) que se actualiza **bit a bit** en `transicion()`, siguiendo exactamente la función δ definida formalmente. No se usa procesamiento directo de cadenas ni se omite la estructura de estados.

---

## Librerías utilizadas

| Librería | Origen | Uso |
|---|---|---|
| `tkinter` | Estándar Python 3 | Construcción de toda la interfaz gráfica (ventanas, campos, botones, scroll). |
| `random` | Estándar Python 3 | `random.choice()` en `generar_frases()` para seleccionar producciones al azar. |
| `tkinter.simpledialog` | Estándar Python 3 | Cuadro de diálogo modal para ingresar la frase a verificar. |
| `tkinter.scrolledtext` | Estándar Python 3 | Widget de texto con barra de desplazamiento para mostrar resultados. |

Todas las librerías pertenecen a la **librería estándar de Python 3**. No se requiere instalación de dependencias externas.

---

## Cómo ejecutar

```bash
# Desde la carpeta raíz del proyecto
cd "Proyecto discretas II MAIN"
python main.py
```

El menú principal ofrece dos opciones:
- **Módulo Gramática** → ingresa G = (V, T, S, P), verifica frases y genera el lenguaje.
- **Módulo Tramas (FSM)** → ingresa tramas de 32 bits y lista de validación, evalúa la transmisión.
