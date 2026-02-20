import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime


USUARIO_CORRECTO = "Javier"
PASSWORD_CORRECTO = "Javier12345"

def verificar_login():
    usuario = entry_usuario.get()
    password = entry_password.get()

    if usuario == USUARIO_CORRECTO and password == PASSWORD_CORRECTO:
        login_window.destroy()
        iniciar_sistema()
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos")

login_window = tk.Tk()
login_window.title("Inicio de Sesión")
login_window.geometry("350x250")
login_window.configure(bg="#1e1e1e")s

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

# Verificar si la columna descripcion existe
cursor.execute("PRAGMA table_info(transacciones)")
columnas = [columna[1] for columna in cursor.fetchall()]

if "descripcion" not in columnas:
    cursor.execute("ALTER TABLE transacciones ADD COLUMN descripcion TEXT")

conexion.commit()


# ---------------------------
# FUNCIONES
# ---------------------------

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


def consultar_por_tipo():
    tipo = tipo_var.get()

    for fila in tabla.get_children():
        tabla.delete(fila)

    cursor.execute("SELECT id, tipo, monto, descripcion, fecha FROM transacciones WHERE tipo = ?", (tipo,))
    registros = cursor.fetchall()

    for registro in registros:
        tabla.insert("", tk.END, values=registro)


def eliminar_transaccion():
    seleccion = tabla.selection()

    if not seleccion:
        messagebox.showwarning("Error", "Seleccione un registro para eliminar")
        return

    confirmar = messagebox.askyesno("Confirmar", "¿Eliminar transacción seleccionada?")
    if confirmar:
        item = tabla.item(seleccion)
        id_transaccion = item["values"][0]

        cursor.execute("DELETE FROM transacciones WHERE id = ?", (id_transaccion,))
        conexion.commit()

        mostrar_transacciones()
        calcular_saldo()


# ---------------------------
# INTERFAZ GRÁFICA
# ---------------------------

ventana = tk.Tk()
ventana.title("Sistema de Finanzas Personales")
ventana.geometry("950x600")
ventana.configure(bg="#1e1e1e")

# Estilos
style = ttk.Style()
style.theme_use("clam")

style.configure("Treeview",
                background="#2b2b2b",
                foreground="white",
                rowheight=25,
                fieldbackground="#2b2b2b")

style.configure("Treeview.Heading",
                background="#3a3a3a",
                foreground="white")

style.map("Treeview",
          background=[("selected", "#4CAF50")])

# ---------------------------
# FRAME FORMULARIO
# ---------------------------

frame_form = tk.Frame(ventana, bg="#1e1e1e")
frame_form.pack(fill="x", padx=20, pady=10)

saldo_label = tk.Label(frame_form,
                       text="Saldo Total: $0.00",
                       font=("Arial", 18, "bold"),
                       fg="#4CAF50",
                       bg="#1e1e1e")
saldo_label.grid(row=0, column=0, columnspan=4, pady=10)

tipo_var = tk.StringVar(value="Ingreso")

tk.Label(frame_form, text="Tipo", fg="white", bg="#1e1e1e").grid(row=1, column=0)
tk.Radiobutton(frame_form, text="Ingreso", variable=tipo_var,
               value="Ingreso", bg="#1e1e1e", fg="white",
               selectcolor="#1e1e1e").grid(row=1, column=1)

tk.Radiobutton(frame_form, text="Gasto", variable=tipo_var,
               value="Gasto", bg="#1e1e1e", fg="white",
               selectcolor="#1e1e1e").grid(row=1, column=2)

tk.Label(frame_form, text="Monto", fg="white", bg="#1e1e1e").grid(row=2, column=0)
monto_entry = tk.Entry(frame_form)
monto_entry.grid(row=2, column=1)

tk.Label(frame_form, text="Descripción", fg="white", bg="#1e1e1e").grid(row=2, column=2)
descripcion_entry = tk.Entry(frame_form, width=30)
descripcion_entry.grid(row=2, column=3)

# Botones
frame_botones = tk.Frame(frame_form, bg="#1e1e1e")
frame_botones.grid(row=3, column=0, columnspan=4, pady=15)

tk.Button(frame_botones, text="Registrar", bg="#4CAF50", fg="white",
          width=15, command=registrar_transaccion).grid(row=0, column=0, padx=5)

tk.Button(frame_botones, text="Mostrar Todas", bg="#2196F3", fg="white",
          width=15, command=mostrar_transacciones).grid(row=0, column=1, padx=5)

tk.Button(frame_botones, text="Consultar por Tipo", bg="#9C27B0", fg="white",
          width=18, command=consultar_por_tipo).grid(row=0, column=2, padx=5)

tk.Button(frame_botones, text="Eliminar Seleccionado", bg="#f44336", fg="white",
          width=20, command=eliminar_transaccion).grid(row=0, column=3, padx=5)

# ---------------------------
# TABLA
# ---------------------------

frame_tabla = tk.Frame(ventana, bg="#1e1e1e")
frame_tabla.pack(fill="both", expand=True, padx=20, pady=10)

tabla = ttk.Treeview(frame_tabla,
                     columns=("ID", "Tipo", "Monto", "Descripcion", "Fecha"),
                     show="headings")

tabla.heading("ID", text="ID")
tabla.heading("Tipo", text="Tipo")
tabla.heading("Monto", text="Monto")
tabla.heading("Descripcion", text="Descripción")
tabla.heading("Fecha", text="Fecha")

tabla.column("ID", width=50)
tabla.column("Tipo", width=100)
tabla.column("Monto", width=100)
tabla.column("Descripcion", width=300)
tabla.column("Fecha", width=200)

tabla.pack(fill="both", expand=True)

mostrar_transacciones()
calcular_saldo()

ventana.mainloop()
conexion.close()

