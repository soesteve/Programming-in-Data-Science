#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 11 11:25:32 2026

@author: soniaestevez
"""

# python corregir_y_exportar.py


# script: recorre todos los .ipynb, corrige las celdas Markdown, 
# guarda el notebook y genera el HTML en la misma carpeta con el mismo nombre.

# Por ejemplo:

# tema1.ipynb → tema1.html

# apuntes/tema2.ipynb → apuntes/tema2.html

import json
import html
import subprocess
from pathlib import Path

# Carpeta donde buscar los notebooks ('.' = carpeta actual)
CARPETA = Path(".")

notebooks_corregidos = 0
html_generados = 0
celdas_corregidas = 0

for archivo in CARPETA.rglob("*.ipynb"):
    print(f"\nProcesando: {archivo}")

    # -------- Corregir el notebook --------
    with open(archivo, "r", encoding="utf-8") as f:
        nb = json.load(f)

    cambiado = False

    for celda in nb["cells"]:
        if celda["cell_type"] == "markdown":
            original = "".join(celda["source"])
            corregido = html.unescape(original)

            if original != corregido:
                celda["source"] = corregido.splitlines(keepends=True)
                celdas_corregidas += 1
                cambiado = True

    if cambiado:
        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)
        notebooks_corregidos += 1
        print("  ✔ Notebook corregido")
    else:
        print("  • Sin cambios")

    # -------- Exportar a HTML --------
    try:
        subprocess.run(
            [
                "jupyter",
                "nbconvert",
                "--to", "html",
                "--template", "lab",
                "--TemplateExporter.exclude_input_prompt=True",
                "--TemplateExporter.exclude_output_prompt=True",
                "--output-dir", str(archivo.parent),
                str(archivo)
            ],
            check=True
        )
        html_generados += 1
        print("  ✔ HTML generado")
    except subprocess.CalledProcessError:
        print("  ✖ Error al generar el HTML")

print("\n" + "=" * 40)
print(f"Notebooks corregidos : {notebooks_corregidos}")
print(f"Celdas corregidas    : {celdas_corregidas}")
print(f"HTML generados       : {html_generados}")
print("=" * 40)



