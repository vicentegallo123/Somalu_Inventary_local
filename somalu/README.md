# 📦 Sistema de Inventario SOMALU

Sistema de inventario local para terminal, con base de datos **SQLite persistente**.
Todos los cambios (entradas, mermas, ajustes) quedan guardados permanentemente en `data/somalu.db`.

## ▶️ Cómo correr

```bash
cd somalu
python3 main.py
```

## 📁 Estructura
```
somalu/
├── main.py                  ← Punto de entrada (menú principal)
├── data/
│   └── somalu.db            ← Base de datos SQLite (se crea automáticamente)
├── exports/                 ← Reportes Excel generados
└── modules/
    ├── db.py                ← Toda la lógica de SQLite
    ├── productos.py         ← Consulta, alta, edición, eliminación
    ├── movimientos.py       ← Entradas, mermas, ajustes, historial
    ├── proveedores.py       ← Directorio y órdenes de compra
    ├── importar.py          ← Carga archivo Excel → SQLite
    └── exportar.py          ← Genera reporte Excel desde SQLite
```

## 🗄️ Base de datos

SQLite en `data/somalu.db` — 3 tablas:

| Tabla         | Contenido |
|---------------|-----------|
| `productos`   | Catálogo con stock, costo y alerta mínima |
| `movimientos` | Historial completo de entradas/mermas/ajustes |
| `proveedores` | Directorio de contactos |

## 📋 Requisitos

```bash
pip install rich pandas openpyxl
```
Python 3.8+. SQLite viene incluido con Python.

## 📥 Importar Excel

Opción **14** del menú. Acepta tu archivo `inventario.xlsx` (con el formato de múltiples hojas de SOMALU).
- Si el producto ya existe → actualiza stock y costo
- Si es nuevo → lo agrega al catálogo

## 🖨️ Exportar reporte

Opción **15** del menú. Genera un `.xlsx` en la carpeta `exports/` con 3 hojas:
- **Inventario** — stock actual con totales
- **Movimientos** — historial completo
- **Proveedores** — directorio
