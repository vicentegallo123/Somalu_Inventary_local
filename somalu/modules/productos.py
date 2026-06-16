
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from modules import db

console = Console()

def agregar_stock(nombre_producto, cantidad_a_sumar):
    datos = db.cargar_datos()
    

    producto_encontrado = None
    for clave, info in datos.items():
        if info['nombre'].lower() == nombre_producto.lower():
            producto_encontrado = clave
            break
            
    if producto_encontrado:
  
        datos[producto_encontrado]['stock'] += cantidad_a_sumar
        db.guardar_datos(datos)
        return True, f"Stock actualizado. Nuevo total: {datos[producto_encontrado]['stock']}"
    else:
        return False, "Producto no encontrado."


def _tabla_productos(rows, titulo="📦 Inventario SOMALU"):
    table = Table(title=titulo, show_lines=False)
    table.add_column("#",           style="dim",     justify="right", width=4)
    table.add_column("Categoría",   style="cyan",    min_width=22)
    table.add_column("Producto",    style="magenta", min_width=22)
    table.add_column("Stock",       justify="right", min_width=7)
    table.add_column("Unidad",      style="dim",     min_width=8)
    table.add_column("Costo/U",     justify="right", min_width=9)
    table.add_column("Total",       justify="right", min_width=10)

    for i, (pid, cat, prod, cant, unidad, costo) in enumerate(rows, 1):
        total = cant * costo
        stock_str = f"[bold red]{cant}[/bold red]" if cant <= 1 else f"[green]{cant}[/green]"
        table.add_row(
            str(i), cat, prod, stock_str,
            unidad or "-",
            f"${costo:,.2f}",
            f"${total:,.2f}"
        )
    console.print(table)


def consultar():
    termino = Prompt.ask("🔍 Buscar producto/categoría (vacío = todos)").strip()
    rows = db.get_todos_productos(termino)
    if not rows:
        console.print("[yellow]Sin resultados.[/yellow]")
        return
    _tabla_productos(rows, f"📦 Inventario — {len(rows)} productos")


def stock_critico():
    rows = db.get_stock_critico()
    if not rows:
        console.print("[green]✅ Ningún producto en stock crítico.[/green]")
        return
    table = Table(title="🚨 Stock Crítico / Bajo")
    table.add_column("Categoría",  style="cyan")
    table.add_column("Producto",   style="red bold")
    table.add_column("Stock",      justify="right")
    table.add_column("Unidad",     style="dim")
    table.add_column("Alerta mín", justify="right")
    for cat, prod, cant, unidad, alerta in rows:
        table.add_row(cat, prod, str(cant), unidad or "-", str(alerta))
    console.print(table)


def agregar():
    console.print("\n[bold cyan]➕ Agregar nuevo producto[/bold cyan]")
    categoria = Prompt.ask("Categoría")
    producto  = Prompt.ask("Nombre del producto")
    cantidad  = float(Prompt.ask("Cantidad inicial", default="0"))
    unidad    = Prompt.ask("Unidad (Piezas/OZ/etc.)", default="Piezas/Botellas")
    costo     = float(Prompt.ask("Costo por unidad", default="0"))
    alerta    = float(Prompt.ask("Alerta mínima de stock", default="1"))

    ok, msg = db.agregar_producto(categoria, producto, cantidad, unidad, costo, alerta)
    console.print(f"[green]{msg}[/green]" if ok else f"[red]{msg}[/red]")


def editar():
    console.print("\n[bold cyan]✏️  Editar producto[/bold cyan]")
    nombre = Prompt.ask("Nombre EXACTO del producto a editar")
    row = db.get_producto(nombre)
    if not row:
        console.print(f"[red]❌ Producto '{nombre}' no encontrado.[/red]")
        return

    pid, cat, prod, cant, unidad, costo, alerta = row
    console.print(f"\nProducto: [bold]{prod}[/bold] | Cat: {cat} | Stock: {cant} | Costo: ${costo}")

    nueva_cat   = Prompt.ask("Nueva categoría", default=cat)
    nuevo_costo = float(Prompt.ask("Nuevo costo/unidad", default=str(costo)))
    nuevo_min   = float(Prompt.ask("Nueva alerta mínima", default=str(alerta)))

    ok, msg = db.actualizar_producto(prod, categoria=nueva_cat, costo_unit=nuevo_costo, alerta_min=nuevo_min)
    console.print(f"[green]{msg}[/green]" if ok else f"[red]{msg}[/red]")


def eliminar():
    nombre = Prompt.ask("Nombre EXACTO del producto a eliminar")
    if not db.get_producto(nombre):
        console.print(f"[red]❌ Producto '{nombre}' no encontrado.[/red]")
        return
    if Confirm.ask(f"¿Eliminar definitivamente '{nombre}'?"):
        db.eliminar_producto(nombre)
        console.print(f"[bold red]🗑️  '{nombre}' eliminado.[/bold red]")
