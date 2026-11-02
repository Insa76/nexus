from openpyxl import Workbook
import os


def register(registry):
    registry["create_excel"] = create_excel
    registry["excel_report"] = excel_report


def create_excel(path):

    wb = Workbook()
    wb.save(path)

    os.startfile(path)

    return f"Excel creado: {path}"


def excel_report(path):

    wb = Workbook()
    ws = wb.active

    ws.append(["Producto", "Ventas"])

    data = [
        ("Cerveza", 120),
        ("Vino", 80),
        ("Tragos", 150)
    ]

    for row in data:
        ws.append(row)

    wb.save(path)
    os.startfile(path)

    return "Reporte generado"
