import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

USUARIO_CORRECTO = "Javier"
PASSWORD_CORRECTO = "Javier12345"

# ==========================
# LOGIN (ÚNICA VENTANA INICIAL)
# ==========================

def verificar_login():
    usuario = entry_usuario.get()
    password = entry_password.get()

    if usuario == USUARIO_CORRECTO and password == PASSWORD_CORRECTO:
        login_window.destroy()   # Cerramos login
        abrir_sistema()          # Abrimos sistema
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")


login_window = tk.Tk()
login_window.title("Inicio de Sesión")
login_window.geometry("350x250")
login_window.configure(bg="#1e1e1e")

tk.Label(login_window, text="Inicio de Sesión",
         font=("Arial", 16, "bold"),
         fg="white", bg="#1e1e1e").pack(pady=15)

tk.Label(login_window, text="Usuario", fg="white", bg="#1e1e1e").pack()
entry_usuario = tk.Entry(login_window)
entry_usuario.pack(pady=5)

tk.Label(login_window, text="Contraseña", fg="white", bg="#1e1e1e").pack()
entry_password = tk.Entry(login_window, show="*")
entry_password.pack(pady=5)

tk.Button(login_window, text="Ingresar",
          bg="#4CAF50", fg="white",
          width=15, command=verificar_login).pack(pady=15)


# ==========================
# SISTEMA PRINCIPAL
# ==========================

def abrir_sistema():

    ventana = tk.Tk()
    ventana.title("Sistema de Finanzas Personales")
    ventana.geometry("950x600")
    ventana.configure(bg="#1e1e1e")

    conexion = sqlite3.connect("finanzas.db")
    cursor = conexion.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transacciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        monto REAL NOT NULL,
        fecha TEXT NOT NULL
    )
    """)

    cursor.execute("PRAGMA table_info(transacciones)")
    columnas = [columna[1] for columna in cursor.fetchall()]

    if "descripcion" not in columnas:
        cursor.execute("ALTER TABLE transacciones ADD COLUMN descripcion TEXT")

    conexion.commit()

    # -------- FUNCIONES --------

    def calcular_saldo():
        cursor.execute("""
            SELECT 
            SUM(CASE WHEN tipo='Ingreso' THEN monto ELSE 0 END) -
            SUM(CASE WHEN tipo='Gasto' THEN monto ELSE 0 END)
            FROM transacciones
        """)

        resultado = cursor.fetchone()[0]
        if resultado is None:
            resultado = 0

        saldo_label.config(text=f"Saldo Total: ${resultado:,.2f}")

    def registrar_transaccion():
        tipo = tipo_var.get()
        monto = monto_entry.get()
        descripcion = descripcion_entry.get()

        if monto == "":
            messagebox.showwarning("Error", "Ingrese un monto")
            return

        try:
            monto = float(monto)
        except:
            messagebox.showwarning("Error", "Ingrese un número válido")
            return

        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(
            "INSERT INTO transacciones (tipo, monto, descripcion, fecha) VALUES (?, ?, ?, ?)",
            (tipo, monto, descripcion, fecha)
        )
        conexion.commit()

        monto_entry.delete(0, tk.END)
        descripcion_entry.delete(0, tk.END)

        mostrar_transacciones()
        calcular_saldo()

    def mostrar_transacciones():
        for fila in tabla.get_children():
            tabla.delete(fila)

        cursor.execute("SELECT id, tipo, monto, descripcion, fecha FROM transacciones ORDER BY fecha DESC")
        registros = cursor.fetchall()

        for registro in registros:
            tabla.insert("", tk.END, values=registro)

    # -------- INTERFAZ --------

    style = ttk.Style()
    style.theme_use("clam")

    style.configure("Treeview",
                    background="#2b2b2b",
                    foreground="white",
                    rowheight=25,
                    fieldbackground="#2b2b2b")

    frame_form = tk.Frame(ventana, bg="#1e1e1e")
    frame_form.pack(fill="x", padx=20, pady=10)

    saldo_label = tk.Label(frame_form,
                           text="Saldo Total: $0.00",
                           font=("Arial", 18, "bold"),
                           fg="#4CAF50",
                           bg="#1e1e1e")
    saldo_label.pack(pady=10)

    tipo_var = tk.StringVar(value="Ingreso")

    tk.Radiobutton(frame_form, text="Ingreso", variable=tipo_var,
                   value="Ingreso", bg="#1e1e1e", fg="white",
                   selectcolor="#1e1e1e").pack()

    tk.Radiobutton(frame_form, text="Gasto", variable=tipo_var,
                   value="Gasto", bg="#1e1e1e", fg="white",
                   selectcolor="#1e1e1e").pack()

    monto_entry = tk.Entry(frame_form)
    monto_entry.pack(pady=5)

    descripcion_entry = tk.Entry(frame_form, width=40)
    descripcion_entry.pack(pady=5)

    tk.Button(frame_form, text="Registrar",
              bg="#4CAF50", fg="white",
              command=registrar_transaccion).pack(pady=5)

    tabla = ttk.Treeview(ventana,
                         columns=("ID", "Tipo", "Monto", "Descripcion", "Fecha"),
                         show="headings")

    for col in ("ID", "Tipo", "Monto", "Descripcion", "Fecha"):
        tabla.heading(col, text=col)

    tabla.pack(fill="both", expand=True, padx=20, pady=10)

    mostrar_transacciones()
    calcular_saldo()

    ventana.mainloop()


login_window.mainloop()

