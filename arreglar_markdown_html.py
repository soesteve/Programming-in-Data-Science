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




from bs4 import BeautifulSoup

def anadir_indice_numerado(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    main = soup.find("main")
    if main is None:
        return

    # Buscar encabezados
    encabezados = main.find_all(["h1", "h2", "h3"])

    if not encabezados:
        return

    toc = soup.new_tag("div")
    toc["class"] = "tabla-contenidos"

    titulo = soup.new_tag("h2")
    titulo.string = "Índice"
    toc.append(titulo)

    ol_principal = soup.new_tag("ol")
    toc.append(ol_principal)

    pila = {1: ol_principal}

    for h in encabezados:
        nivel = int(h.name[1])

        if not h.get("id"):
            continue

        while nivel not in pila and nivel > 1:
            nivel -= 1

        if int(h.name[1]) > max(pila.keys()):
            nuevo = soup.new_tag("ol")
            ultimo = pila[max(pila.keys())].find_all("li")[-1]
            ultimo.append(nuevo)
            pila[int(h.name[1])] = nuevo

        li = soup.new_tag("li")
        a = soup.new_tag("a", href="#" + h["id"])
        a.string = h.get_text(strip=True).replace("¶", "")
        li.append(a)

        pila[int(h.name[1])].append(li)

    # Insertar al principio del documento
    main.insert(0, toc)

    # Estilo
    style = soup.new_tag("style")
    style.string = """
    .tabla-contenidos{
        background:#f8f9fa;
        border:1px solid #ddd;
        border-radius:8px;
        padding:20px;
        margin-bottom:30px;
    }
    .tabla-contenidos ol{
        margin-left:20px;
    }
    .tabla-contenidos a{
        text-decoration:none;
        color:#0b57d0;
    }
    .tabla-contenidos a:hover{
        text-decoration:underline;
    }
    """
    soup.head.append(style)

    with open(html_path, "w", encoding="utf-8") as f:
        f.write(str(soup))



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

    # -------- Exportar a HTML nbconvert --------
    try:
        resultado = subprocess.run(
            [
                "jupyter",
                "nbconvert",
                "--to", "html",
                "--execute",   # ← Ejecuta el notebook
                "--template", "lab",
                "--TemplateExporter.exclude_input_prompt=True",
                "--TemplateExporter.exclude_output_prompt=True",
                "--ExecutePreprocessor.timeout=600",
                "--output-dir", str(archivo.parent),
                str(archivo)
            ],
            check=True,
            capture_output=True,
            text=True
        )
    
        # Ruta del HTML recién generado
        html_path = archivo.with_suffix(".html")
    
        # Añadir la tabla de contenidos
        anadir_indice_numerado(html_path)
    
        html_generados += 1
        print("  ✔ HTML generado con índice")
    
    except subprocess.CalledProcessError as e:
        print("  ✖ Error al generar el HTML")
        print(e.stderr)


print("\n" + "=" * 40)
print(f"Notebooks corregidos : {notebooks_corregidos}")
print(f"Celdas corregidas    : {celdas_corregidas}")
print(f"HTML generados       : {html_generados}")
print("=" * 40)



