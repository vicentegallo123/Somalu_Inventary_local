
import os
import sys


sys.path.insert(0, os.path.dirname(__file__))

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from modules import db
from modules import productos, movimientos, proveedores, exportar, importar

console = Console()
def _importar_interactivo():
    ruta = Prompt.ask("📂 Ruta completa del archivo Excel a importar")
    ruta = ruta.strip().strip('"')
    if not os.path.exists(ruta):
        console.print(f"[red]❌ Archivo no encontrado: {ruta}[/red]")
        return
    ok, msg = importar.cargar_excel(ruta)
    console.print(f"[green]{msg}[/green]" if ok else f"[red]{msg}[/red]")

def limpiar():
    os.system("cls" if os.name == "nt" else "clear")


MENU = """[bold cyan]
  1.[/bold cyan] 🔍  Consultar productos / stock
  [bold cyan]2.[/bold cyan] 🚨  Ver stock crítico / bajo
  [bold cyan]3.[/bold cyan] ➕  Agregar producto nuevo
  [bold cyan]4.[/bold cyan] ✏️   Editar producto (precio, categoría, alerta)
  [bold cyan]5.[/bold cyan] 🗑️   Eliminar producto
  ──────────────────────────────────────
  [bold cyan]6.[/bold cyan] 📥  Registrar Entrada  (factura / folio)
  [bold cyan]7.[/bold cyan] 📉  Registrar Merma   (rotura / caducidad)
  [bold cyan]8.[/bold cyan] 🔧  Ajuste manual de stock (conteo físico)
  [bold cyan]9.[/bold cyan] 📋  Historial de movimientos
  ──────────────────────────────────────
  [bold cyan]10.[/bold cyan] 📞  Directorio de proveedores
  [bold cyan]11.[/bold cyan] ➕  Agregar proveedor
  [bold cyan]12.[/bold cyan] 🛒  Generar orden de compra
  [bold cyan]13.[/bold cyan] 🗑️   Eliminar proveedor
  ──────────────────────────────────────
  [bold cyan]14.[/bold cyan] 📂  Importar/actualizar desde Excel
  [bold cyan]15.[/bold cyan] 🖨️   Exportar reporte Excel
  ──────────────────────────────────────
  [bold cyan] 0.[/bold cyan] 🚪  Salir"""

ACCIONES = {
    "1":  productos.consultar,
    "2":  productos.stock_critico,
    "3":  productos.agregar,
    "4":  productos.editar,
    "5":  productos.eliminar,
    "6":  movimientos.entrada,
    "7":  movimientos.merma,
    "8":  movimientos.ajuste,
    "9":  movimientos.historial,
    "10": proveedores.listar,
    "11": proveedores.agregar,
    "12": proveedores.orden_compra,
    "13": proveedores.eliminar,
    "14": _importar_interactivo,
    "15": exportar.exportar_excel,
}


def _importar_interactivo():
    ruta = Prompt.ask("📂 Ruta completa del archivo Excel a importar")
    ruta = ruta.strip().strip("'\"")
    if not os.path.exists(ruta):
        console.print(f"[red]❌ Archivo no encontrado: {ruta}[/red]")
        return
    ok, msg = importar.cargar_excel(ruta)
    console.print(f"[green]{msg}[/green]" if ok else f"[red]{msg}[/red]")


ACCIONES["14"] = _importar_interactivo

def menu_agregar_stock():
    nombre = Prompt.ask("Nombre del producto a buscar (ej. Coca Cola)")
    cantidad = int(Prompt.ask("Cantidad a sumar"))
    
    exito, mensaje = productos.agregar_stock(nombre, cantidad)
    if exito:
        console.print(f"[green]{mensaje}[/green]")
    else:
        console.print(f"[red]{mensaje}[/red]")


def main():
    db.inicializar()
    limpiar()

    while True:
        console.print(Panel(MENU, title="[bold white]📦 SISTEMA INVENTARIO SOMALU[/bold white]",
                            border_style="cyan", padding=(0, 2)))
        opcion = Prompt.ask("\n[bold]Selecciona una opción[/bold]",
                            choices=[str(i) for i in range(16)], show_choices=False)
        
        limpiar()

        if opcion == "0":
            console.print("[bold cyan]¡Hasta luego![/bold cyan]")
            break

        accion = ACCIONES.get(opcion)
        if accion:
            accion()

        input("\n[Presiona ENTER para continuar...]")
        limpiar()


if __name__ == "__main__":
    main()
