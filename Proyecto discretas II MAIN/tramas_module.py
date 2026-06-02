import tkinter as tk

def ingresar_lista_validacion(entries, output):
    lista = []
    for i, entry in enumerate(entries):
        bits = entry.get().strip()
        if len(bits) != 4 or any(b not in '01' for b in bits):
            output.insert('end', f"⚠️ Línea {i+1} inválida: '{bits}' no es un grupo de 4 bits.\n")
            continue
        lista.append(int(bits, 2))
    return lista

def ingresar_tramas(entries, output):
    tramas = []
    for i, entry in enumerate(entries):
        bits = entry.get().strip()
        if len(bits) != 32 or any(b not in '01' for b in bits):
            output.insert('end', f"⚠️ Trama {i+1} inválida: debe tener 32 bits.\n")
            continue
        tramas.append(bits)
    return tramas

def validar_trama(trama, valor_lista):
    # Extrae bits 10-14 según rúbrica (índices 9 a 13)
    sub = trama[9:14]
    valor = int(sub, 2)
    suma = valor + valor_lista
    valido = (valor % 3 == 0) and (suma % 5 == 0)
    return valido, sub, valor, suma

def procesar(valid_entries, trama_entries, output):
    output.delete('1.0', 'end')
    lista = ingresar_lista_validacion(valid_entries, output)
    tramas = ingresar_tramas(trama_entries, output)
    if not lista or not tramas:
        output.insert('end', "⚠️ Datos insuficientes para evaluar.\n")
        return

    output.insert('end', "🔍 Resultados por trama:\n" + "-"*40 + "\n")
    resultados = []
    for i, trama in enumerate(tramas):
        if i < len(lista):
            valido, sub, val, suma = validar_trama(trama, lista[i])
            estado = 'Valida' if valido else 'Invalida'
            icono = '✅' if valido else '❌'
            output.insert('end',
                f"Trama {i+1}: {icono} {estado} | bits[10–14]='{sub}' ({val}) + {lista[i]} = {suma}\n")
            resultados.append(valido)
        else:
            output.insert('end', f"Trama {i+1}: ❌ Invalida (sin valor de lista)\n")
            resultados.append(False)

    total = len(resultados)
    invalidas = resultados.count(False)
    error = (invalidas / total) * 100
    output.insert('end', "-"*40 + "\n")
    output.insert('end', f"📊 Total tramas: {total}\n")
    output.insert('end', f"❌ Inválidas: {invalidas} ({error:.2f}%)\n")
    if error < 20:
        output.insert('end', "✅ Transmisión correcta.\n")
    else:
        output.insert('end', "⚠️ Transmisión con errores (>20%).\n")

def main():
    root = tk.Tk()
    root.title("🧪 Evaluador de Tramas (FSM)")
    root.geometry("720x820")
    root.configure(bg="#f4f4f4")

    tk.Label(root, text="🔢 Lista validación (5 valores de 4 bits)",
             font=('Arial', 12, 'bold'), bg="#f4f4f4").pack(pady=5)
    valid_entries = []
    for _ in range(5):
        e = tk.Entry(root, width=10, font=('Consolas', 12), justify='center')
        e.pack(pady=2)
        valid_entries.append(e)

    tk.Label(root, text="💾 Tramas (5 tramas de 32 bits)",
             font=('Arial', 12, 'bold'), bg="#f4f4f4").pack(pady=(15, 0))
    trama_entries = []
    for _ in range(5):
        e = tk.Entry(root, width=45, font=('Consolas', 12), justify='center')
        e.pack(pady=2)
        trama_entries.append(e)

    output = tk.Text(root, height=20, width=85, bg='#ffffff',
                     font=('Consolas', 11), bd=2, relief='solid')
    output.pack(padx=10, pady=10)

    tk.Button(root, text="🧾 Evaluar Transmisión",
              font=('Arial', 11, 'bold'), bg="#d0f0c0",
              command=lambda: procesar(valid_entries, trama_entries, output)).pack(pady=10)
    tk.Button(root, text="⏹️ Salir", font=('Arial', 11), bg="#ffcccc",
              command=lambda: [root.destroy(), __import__('main').main()]).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
