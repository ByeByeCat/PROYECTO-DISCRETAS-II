import tkinter as tk
import gramatica_module as gramatica
import tramas_module as tramas

def ejecutar_gramatica(root):
    root.destroy()
    gramatica.main()

def ejecutar_tramas(root):
    root.destroy()
    tramas.main()

def main():
    root = tk.Tk()
    root.title("📚 Proyecto Final - Menú Principal")
    root.geometry("600x300")
    root.configure(bg="#f4f4f4")

    frame = tk.Frame(root, bg="#f4f4f4")
    frame.place(relx=0.5, rely=0.5, anchor='center')  # centrado

    titulo = tk.Label(
        frame,
        text="🧪 Sistema de Evaluación\nGramáticas & Tramas FSM",
        font=("Arial", 16, "bold"),
        bg="#f4f4f4"
    )
    titulo.pack(pady=(10, 20))

    tk.Button(
        frame,
        text="📖 Módulo Gramática",
        font=("Arial", 12),
        width=30,
        height=2,
        bg="#cce5ff",
        command=lambda: ejecutar_gramatica(root)
    ).pack(pady=5)

    tk.Button(
        frame,
        text="📡 Módulo Tramas (FSM)",
        font=("Arial", 12),
        width=30,
        height=2,
        bg="#d5f5e3",
        command=lambda: ejecutar_tramas(root)
    ).pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main()
