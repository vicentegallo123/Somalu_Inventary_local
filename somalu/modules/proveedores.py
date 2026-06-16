"""
proveedores.py — Directorio de proveedores y generación de órdenes de compra
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from modules import db

console = Console()


def listar():
    rows = db.get_proveedores()
    if not rows:
        console.print("[yellow]Sin proveedores registrados. Usa 'Agregar proveedor'.[/yellow]")
        return
    table = Table(title="📞 Directorio de Proveedores")
    table.add_column("#",           style="dim", justify="right", width=4)
    table.add_column("Proveedor",   style="magenta", min_width=22)
    table.add_column("Teléfono",    style="green",   min_width=14)
    table.add_column("Email",       style="cyan",    min_width=18)
    table.add_column("Comentarios", style="dim")
    for i, (pid, nombre, tel, email, com) in enumerate(rows, 1):
        table.add_row(str(i), nombre, tel or "-", email or "-", com or "-")
    console.print(table)


def agregar():
    console.print("\n[bold cyan]➕ Nuevo proveedor[/bold cyan]")
    nombre = Prompt.ask("Nombre de la empresa o contacto")
    tel    = Prompt.ask("Teléfono", default="")
    email  = Prompt.ask("Email",    default="")
    com    = Prompt.ask("Comentarios (opcional)", default="")
    ok, msg = db.agregar_proveedor(nombre, tel, email, com)
    console.print(f"[green]{msg}[/green]" if ok else f"[red]{msg}[/red]")


def eliminar():
    listar()
    nombre = Prompt.ask("\nNombre EXACTO del proveedor a eliminar")
    if Confirm.ask(f"¿Eliminar a '{nombre}'?"):
        db.eliminar_proveedor(nombre)
        console.print(f"[red]🗑️  Proveedor '{nombre}' eliminado.[/red]")


def orden_compra():
    rows = db.get_proveedores()
    if not rows:
        console.print("[red]❌ Primero registra un proveedor.[/red]")
        return

    listar()
    idx = int(Prompt.ask("\n# del proveedor para la orden")) - 1
    if idx < 0 or idx >= len(rows):
        console.print("[red]Número inválido.[/red]")
        return

    _, nombre, tel, email, _ = rows[idx]

    console.print("\n[cyan]Escribe los artículos a pedir. ENTER vacío para terminar.[/cyan]")
    items = []
    while True:
        item = Prompt.ask("Artículo y cantidad")
        if not item.strip():
            break
        items.append(item)

    if not items:
        console.print("[yellow]Orden cancelada.[/yellow]")
        return

    lista = "\n".join(f"  • {i}" for i in items)
    resumen = (
        f"[bold]Para:[/bold]     {nombre}\n"
        f"[bold]Teléfono:[/bold] {tel or 'N/D'}\n"
        f"[bold]Email:[/bold]    {email or 'N/D'}\n\n"
        f"[bold]Artículos:[/bold]\n{lista}"
    )
    console.print(Panel(resumen, title="🛒 Orden de Compra", border_style="green"))
    console.print("[dim](Copia el texto de arriba para enviarla por WhatsApp/correo)[/dim]")
