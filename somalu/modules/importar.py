"""
importar.py — Carga archivo Excel al inventario SQLite
"""
import pandas as pd
from modules import db

def cargar_excel(ruta_excel):
    """
    Lee todas las hojas del Excel de SOMALU (saltando 2 filas de título)
    e inserta/actualiza productos en la BD.
    """
    try:
        xl = pd.ExcelFile(ruta_excel)
    except Exception as e:
        return False, f"No se pudo abrir el archivo: {e}"

    nuevos = 0
    actualizados = 0
    errores = []

    for hoja in xl.sheet_names:
        try:
            df = pd.read_excel(ruta_excel, sheet_name=hoja, skiprows=2)
            df.columns = [str(c).strip() for c in df.columns]

            col_map = {
                "Categoría": "categoria",
                "Producto": "producto",
                "Cantidad Actual": "cantidad",
                "Unidad": "unidad",
                "COSTO UNIDAD": "costo_unit",
            }
            # Renombrar columnas si existen
            df = df.rename(columns={k: v for k, v in col_map.items() if k in df.columns})

            if "producto" not in df.columns:
                continue

            df = df.dropna(subset=["producto"])
            df["cantidad"] = pd.to_numeric(df.get("cantidad", 0), errors="coerce").fillna(0)
            df["costo_unit"] = pd.to_numeric(df.get("costo_unit", 0), errors="coerce").fillna(0)

            for _, row in df.iterrows():
                categoria = str(row.get("categoria", hoja)).strip()
                producto = str(row["producto"]).strip()
                cantidad = float(row["cantidad"])
                unidad = str(row.get("unidad", "")).strip()
                costo = float(row["costo_unit"])

                existente = db.get_producto(producto)
                if existente:
                    db.actualizar_producto(producto, cantidad=cantidad, costo_unit=costo, unidad=unidad)
                    actualizados += 1
                else:
                    ok, _ = db.agregar_producto(categoria, producto, cantidad, unidad, costo)
                    if ok:
                        nuevos += 1
                    else:
                        errores.append(producto)

        except Exception as e:
            errores.append(f"[Hoja {hoja}]: {e}")

    msg = f"✅ Importación completa — {nuevos} nuevos, {actualizados} actualizados."
    if errores:
        msg += f"\n⚠️  Errores en: {', '.join(errores)}"
    return True, msg
