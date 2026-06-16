"""
db.py — Capa de base de datos SQLite persistente para SOMALU
"""
import sqlite3
import os
from datetime import datetime

from streamlit import json

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "somalu.db")

DB_FILE = "inventario.json"

def cargar_datos():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {} 

def guardar_datos(datos):
    with open(DB_FILE, "w") as f:
        json.dump(datos, f, indent=4)
        
def conectar():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    return sqlite3.connect(DB_PATH)

def inicializar():
    """Crea las tablas si no existen."""
    con = conectar()
    cur = con.cursor()

    cur.executescript("""
        CREATE TABLE IF NOT EXISTS productos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            categoria   TEXT NOT NULL,
            producto    TEXT NOT NULL UNIQUE,
            cantidad    REAL NOT NULL DEFAULT 0,
            unidad      TEXT,
            costo_unit  REAL DEFAULT 0,
            alerta_min  REAL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS movimientos (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha       TEXT NOT NULL,
            tipo        TEXT NOT NULL,       -- ENTRADA / MERMA / AJUSTE
            folio       TEXT,
            proveedor   TEXT,
            producto    TEXT NOT NULL,
            cantidad    REAL NOT NULL,
            costo_unit  REAL DEFAULT 0,
            notas       TEXT
        );

        CREATE TABLE IF NOT EXISTS proveedores (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre      TEXT NOT NULL UNIQUE,
            telefono    TEXT,
            email       TEXT,
            comentarios TEXT
        );
    """)
    con.commit()
    con.close()

# ── Productos ──────────────────────────────────────────────
def get_todos_productos(termino=""):
    con = conectar()
    cur = con.cursor()
    if termino:
        cur.execute(
            "SELECT id, categoria, producto, cantidad, unidad, costo_unit FROM productos "
            "WHERE producto LIKE ? OR categoria LIKE ? ORDER BY categoria, producto",
            (f"%{termino}%", f"%{termino}%")
        )
    else:
        cur.execute(
            "SELECT id, categoria, producto, cantidad, unidad, costo_unit FROM productos "
            "ORDER BY categoria, producto"
        )
    rows = cur.fetchall()
    con.close()
    return rows

def get_producto(nombre):
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT * FROM productos WHERE producto = ?", (nombre,))
    row = cur.fetchone()
    con.close()
    return row

def agregar_producto(categoria, producto, cantidad, unidad, costo_unit, alerta_min=1):
    con = conectar()
    cur = con.cursor()
    try:
        cur.execute(
            "INSERT INTO productos (categoria, producto, cantidad, unidad, costo_unit, alerta_min) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (categoria, producto, cantidad, unidad, costo_unit, alerta_min)
        )
        con.commit()
        return True, "Producto agregado."
    except sqlite3.IntegrityError:
        return False, f"El producto '{producto}' ya existe."
    finally:
        con.close()

def actualizar_cantidad(producto, delta):
    con = conectar()
    cur = con.cursor()
    cur.execute("UPDATE productos SET cantidad = cantidad + ? WHERE producto = ?", (delta, producto))
    con.commit()
    con.close()

def actualizar_producto(producto, **campos):
    permitidos = {"categoria", "cantidad", "unidad", "costo_unit", "alerta_min"}
    sets = ", ".join(f"{k} = ?" for k in campos if k in permitidos)
    vals = [v for k, v in campos.items() if k in permitidos]
    if not sets:
        return False, "Sin campos válidos para actualizar."
    vals.append(producto)
    con = conectar()
    cur = con.cursor()
    cur.execute(f"UPDATE productos SET {sets} WHERE producto = ?", vals)
    con.commit()
    con.close()
    return True, "Actualizado."

def eliminar_producto(producto):
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM productos WHERE producto = ?", (producto,))
    con.commit()
    con.close()

def get_stock_critico():
    con = conectar()
    cur = con.cursor()
    cur.execute(
        "SELECT categoria, producto, cantidad, unidad, alerta_min FROM productos "
        "WHERE cantidad <= alerta_min ORDER BY cantidad"
    )
    rows = cur.fetchall()
    con.close()
    return rows

# ── Movimientos ────────────────────────────────────────────
def registrar_movimiento(tipo, producto, cantidad, folio="", proveedor="", costo_unit=0, notas=""):
    con = conectar()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO movimientos (fecha, tipo, folio, proveedor, producto, cantidad, costo_unit, notas) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        (datetime.now().strftime("%Y-%m-%d %H:%M"), tipo, folio, proveedor, producto, cantidad, costo_unit, notas)
    )
    con.commit()
    con.close()

def get_movimientos(limite=50, producto=""):
    con = conectar()
    cur = con.cursor()
    if producto:
        cur.execute(
            "SELECT fecha, tipo, folio, proveedor, producto, cantidad, costo_unit, notas "
            "FROM movimientos WHERE producto LIKE ? ORDER BY id DESC LIMIT ?",
            (f"%{producto}%", limite)
        )
    else:
        cur.execute(
            "SELECT fecha, tipo, folio, proveedor, producto, cantidad, costo_unit, notas "
            "FROM movimientos ORDER BY id DESC LIMIT ?",
            (limite,)
        )
    rows = cur.fetchall()
    con.close()
    return rows

# ── Proveedores ────────────────────────────────────────────
def get_proveedores():
    con = conectar()
    cur = con.cursor()
    cur.execute("SELECT id, nombre, telefono, email, comentarios FROM proveedores ORDER BY nombre")
    rows = cur.fetchall()
    con.close()
    return rows

def agregar_proveedor(nombre, telefono="", email="", comentarios=""):
    con = conectar()
    cur = con.cursor()
    try:
        cur.execute(
            "INSERT INTO proveedores (nombre, telefono, email, comentarios) VALUES (?, ?, ?, ?)",
            (nombre, telefono, email, comentarios)
        )
        con.commit()
        return True, "Proveedor registrado."
    except sqlite3.IntegrityError:
        return False, f"El proveedor '{nombre}' ya existe."
    finally:
        con.close()

def eliminar_proveedor(nombre):
    con = conectar()
    cur = con.cursor()
    cur.execute("DELETE FROM proveedores WHERE nombre = ?", (nombre,))
    con.commit()
    con.close()
