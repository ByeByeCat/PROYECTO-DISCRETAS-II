import tkinter as tk
from tkinter import simpledialog, scrolledtext
import random

def construir_gramatica(no_terminales_str, terminales_str, S_str, producciones_str):
    V = set(no_terminales_str.split())
    T = set(terminales_str.split())
    S = S_str.strip()
    P = {}
    for line in producciones_str.splitlines():
        line = line.strip()
        if not line or '->' not in line:
            continue
        left, right = line.split('->', 1)
        NT = left.strip()
        cuerpo = right.strip().split()
        P.setdefault(NT, []).append(cuerpo)
    return {'V': V, 'T': T, 'S': S, 'P': P}

def pertenece_frase(frase_str, gramatica, max_profundidad=10):
    target = frase_str.split()
    def backtrack(sentencia, profundidad):
        if profundidad > max_profundidad:
            return False
        if sentencia == target and all(sym in gramatica['T'] for sym in sentencia):
            return True
        if all(sym in gramatica['T'] for sym in sentencia):
            return False
        for idx, sym in enumerate(sentencia):
            if sym in gramatica['V']:
                for prod in gramatica['P'].get(sym, []):
                    nueva = sentencia[:idx] + prod + sentencia[idx+1:]
                    if backtrack(nueva, profundidad + 1):
                        return True
                return False
        return False
    return backtrack([gramatica['S']], 0)

def generar_frases(gramatica, n=10, max_profundidad=10):
    frases = []
    intentos = 0
    while len(frases) < n and intentos < n * 5:
        intentos += 1
        sentencia = [gramatica['S']]
        profundidad = 0
        while any(sym in gramatica['V'] for sym in sentencia) and profundidad < max_profundidad:
            idx = next(i for i, s in enumerate(sentencia) if s in gramatica['V'])
            nt = sentencia[idx]
            prods = gramatica['P'].get(nt, [])
            if not prods:
                break
            prod = random.choice(prods)
            sentencia = sentencia[:idx] + prod + sentencia[idx+1:]
            profundidad += 1
        if all(sym in gramatica['T'] for sym in sentencia):
            frases.append(' '.join(sentencia))
    return frases

def main():
    root = tk.Tk()
    root.title("📚 Módulo Gramática")
    root.geometry("720x740")
    root.configure(bg="#f4f4f4")

    tk.Label(root, text="🔤 No terminales (separados por espacio)", font=('Arial', 11), bg="#f4f4f4").pack(padx=10, anchor='w', pady=(10, 0))
    nt_entry = tk.Entry(root, width=60, font=('Consolas', 12), justify='center')
    nt_entry.pack(padx=10)

    tk.Label(root, text="🔡 Terminales (separados por espacio)", font=('Arial', 11), bg="#f4f4f4").pack(padx=10, anchor='w', pady=(10, 0))
    t_entry = tk.Entry(root, width=60, font=('Consolas', 12), justify='center')
    t_entry.pack(padx=10)

    tk.Label(root, text="🎯 Símbolo inicial", font=('Arial', 11), bg="#f4f4f4").pack(padx=10, anchor='w', pady=(10, 0))
    s_entry = tk.Entry(root, width=20, font=('Consolas', 12), justify='center')
    s_entry.pack(padx=10)

    tk.Label(root, text="📐 Producciones (una por línea: A -> a B)", font=('Arial', 11), bg="#f4f4f4").pack(padx=10, anchor='w', pady=(10, 0))
    prod_text = scrolledtext.ScrolledText(root, width=60, height=6, font=('Consolas', 10))
    prod_text.pack(padx=10, pady=(0, 10))

    output = scrolledtext.ScrolledText(root, width=85, height=15, font=('Consolas', 11), bg='#ffffff')
    output.pack(padx=10, pady=(10, 10))

    def load_and_process(mode):
        output.delete('1.0', 'end')
        g = construir_gramatica(nt_entry.get(), t_entry.get(), s_entry.get(), prod_text.get('1.0', 'end'))
        if mode == 'verify':
            frase = simpledialog.askstring("Verificación de frase", "Ingrese la frase separada por espacios:")
            if frase:
                res = pertenece_frase(frase, g)
                output.insert('end', f"📥 Frase: \"{frase}\"\nResultado: {'✅ PERTENECE' if res else '❌ NO PERTENECE'}\n")
        else:
            frases = generar_frases(g, n=10)
            output.insert('end', "📝 Frases generadas:\n-------------------------\n")
            for i, f in enumerate(frases, 1):
                output.insert('end', f"{i}. {f}\n")

    btn_frame = tk.Frame(root, bg="#f4f4f4")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="🧪 Verificar frase", command=lambda: load_and_process('verify'), font=('Arial', 11), bg="#d0eaff").pack(side='left', padx=5)
    tk.Button(btn_frame, text="🎲 Generar frases", command=lambda: load_and_process('generate'), font=('Arial', 11), bg="#c1f0c1").pack(side='left', padx=5)
    tk.Button(btn_frame, text="⏹️ Salir", command=lambda: [root.destroy(), __import__('main').main()], font=('Arial', 11), bg="#ffcccc").pack(side='left', padx=5)

    root.mainloop()
