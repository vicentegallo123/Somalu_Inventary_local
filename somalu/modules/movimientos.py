"""
movimientos.py — Entradas, mermas y ajustes de inventario
"""
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt
from modules import db

console = Console()


def _pedir_producto():
    nombre = Prompt.ask("Nombre EXACTO del producto")
    row = db.get_producto(nombre)
    if not row:
        console.print(f"[red]❌ '{nombre}' no existe. Búscalo con opción 1.[/red]")
        return None, None
    return nombre, row


def entrada():
    console.print("\n[bold green]📥 Registrar Entrada[/bold green]")
    nombre, row = _pedir_producto()
    if not nombre:
        return

    pid, cat, prod, stock_actual, unidad, costo, alerta = row
    console.print(f"Stock actual de [bold]{prod}[/bold]: [cyan]{stock_actual} {unidad}[/cyan]")

    cantidad = float(Prompt.ask("¿Cuántas unidades entran?"))
    folio    = Prompt.ask("Folio / # Factura")
    proveedor = Prompt.ask("Proveedor")
    notas    = Prompt.ask("Notas (opcional)", default="")

    db.actualizar_cantidad(prod, cantidad)
    db.registrar_movimiento("ENTRADA", prod, cantidad, folio, proveedor, costo, notas)
    nuevo = stock_actual + cantidad
    console.print(f"[green]✅ Entrada registrada. Stock actualizado: {nuevo} {unidad}[/green]")


def merma():
    console.print("\n[bold yellow]📉 Registrar Merma / Salida[/bold yellow]")
    nombre, row = _pedir_producto()
    if not nombre:
        return

    pid, cat, prod, stock_actual, unidad, costo, alerta = row
    console.print(f"Stock actual de [bold]{prod}[/bold]: [cyan]{stock_actual} {unidad}[/cyan]")

    cantidad = float(Prompt.ask("¿Cuántas unidades se dan de baja?"))
    motivo   = Prompt.ask("Motivo (rotura, caducidad, consumo, etc.)")
    notas    = Prompt.ask("Notas adicionales (opcional)", default="")

    db.actualizar_cantidad(prod, -cantidad)
    db.registrar_movimiento("MERMA", prod, cantidad, "S/F", motivo, costo, notas)
    nuevo = stock_actual - cantidad
    color = "red" if nuevo <= alerta else "yellow"
    console.print(f"[{color}]⚠️  Merma registrada. Stock actualizado: {nuevo} {unidad}[/{color}]")


def ajuste():
    console.print("\n[bold blue]🔧 Ajuste Manual de Stock[/bold blue]")
    nombre, row = _pedir_producto()
    if not nombre:
        return

    pid, cat, prod, stock_actual, unidad, costo, alerta = row
    console.print(f"Stock actual: [cyan]{stock_actual} {unidad}[/cyan]")

    nuevo_stock = float(Prompt.ask("Nuevo stock real (conteo físico)"))
    motivo = Prompt.ask("Motivo del ajuste")
    delta = nuevo_stock - stock_actual

    db.actualizar_cantidad(prod, delta)
    tipo_mov = "AJUSTE+" if delta >= 0 else "AJUSTE-"
    db.registrar_movimiento(tipo_mov, prod, abs(delta), "S/F", motivo, costo, f"Ajuste: {stock_actual} → {nuevo_stock}")
    console.print(f"[blue]✅ Stock ajustado a {nuevo_stock} {unidad} (Δ {delta:+})[/blue]")


def historial():
    console.print("\n[bold]📋 Historial de Movimientos[/bold]")
    filtro  = Prompt.ask("Filtrar por producto (vacío = todos)").strip()
    limite  = int(Prompt.ask("Cuántos registros mostrar", default="30"))
    rows    = db.get_movimientos(limite, filtro)

    if not rows:
        console.print("[yellow]Sin movimientos registrados.[/yellow]")
        return

    table = Table(title=f"Últimos {len(rows)} movimientos")
    table.add_column("Fecha",      style="dim",    min_width=14)
    table.add_column("Tipo",       min_width=9)
    table.add_column("Producto",   style="magenta", min_width=20)
    table.add_column("Cant.",      justify="right")
    table.add_column("Folio",      style="dim")
    table.add_column("Proveedor/Motivo")
    table.add_column("Notas",      style="dim")

    colores = {"ENTRADA": "green", "MERMA": "red", "AJUSTE+": "blue", "AJUSTE-": "yellow"}
    for fecha, tipo, folio, prov, prod, cant, costo, notas in rows:
        color = colores.get(tipo, "white")
        table.add_row(
            fecha, f"[{color}]{tipo}[/{color}]", prod,
            str(cant), folio or "-", prov or "-", notas or "-"
        )
    console.print(table)
