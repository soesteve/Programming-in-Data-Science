#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import html
import subprocess
from pathlib import Path
from bs4 import BeautifulSoup

CARPETA = Path(".")

notebooks_corregidos = 0
html_generados = 0
celdas_corregidas = 0


def anadir_indice_numerado(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    main = soup.find("main")
    if main is None:
        return

    encabezados = main.find_all(["h1", "h2", "h3", "h4"])

    if not encabezados:
        return

    # ----- Crear la caja del índice -----

    toc = soup.new_tag("div", attrs={"class": "tabla-contenidos"})

    titulo = soup.new_tag("h2")
    titulo.string = "Índice"
    toc.append(titulo)

    ol_raiz = soup.new_tag("ol")
    toc.append(ol_raiz)

    # Contadores de numeración
    contadores = [0, 0, 0, 0]

    # Pila de listas ordenadas
    pila_ol = [ol_raiz]
    ultimo_li = None

    for h in encabezados:

        nivel = int(h.name[1])

        if not h.get("id"):
            continue

        # Actualizar contadores
        contadores[nivel - 1] += 1

        for i in range(nivel, 4):
            contadores[i] = 0

        numero = ".".join(str(x) for x in contadores[:nivel] if x)

        texto = h.get_text(" ", strip=True).replace("¶", "").strip()

        # Numerar el encabezado
        h.clear()
        h.append(f"{numero} {texto}")

        enlace = soup.new_tag(
            "a",
            attrs={
                "class": "anchor-link",
                "href": "#" + h["id"]
            }
        )
        enlace.string = "¶"
        h.append(enlace)

        # Ajustar la pila según el nivel
        while len(pila_ol) > nivel:
            pila_ol.pop()

        while len(pila_ol) < nivel:
            if ultimo_li is None:
                break
            nuevo_ol = soup.new_tag("ol")
            ultimo_li.append(nuevo_ol)
            pila_ol.append(nuevo_ol)

        # Crear elemento del índice
        li = soup.new_tag("li")

        a = soup.new_tag("a", href="#" + h["id"])
        a.string = f"{numero} {texto}"

        li.append(a)

        pila_ol[-1].append(li)

        ultimo_li = li

    # Eliminar listas vacías
    for ol in toc.find_all("ol"):
        if not ol.find_all("li", recursive=False):
            ol.decompose()

    # Insertar al principio del documento
    main.insert(0, toc)

    # Estilos
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


# ------------------------------------------------------------------
# Recorrer todos los notebooks
# ------------------------------------------------------------------

for archivo in CARPETA.rglob("*.ipynb"):

    print(f"\nProcesando: {archivo}")

    with open(archivo, "r", encoding="utf-8") as f:
        nb = json.load(f)

    cambiado = False

    for celda in nb["cells"]:

        if celda["cell_type"] == "markdown":

            original = "".join(celda["source"])
            corregido = html.unescape(original)

            if original != corregido:
                celda["source"] = corregido.splitlines(keepends=True)
                cambiado = True
                celdas_corregidas += 1

    if cambiado:

        with open(archivo, "w", encoding="utf-8") as f:
            json.dump(nb, f, ensure_ascii=False, indent=1)

        notebooks_corregidos += 1
        print("  ✔ Notebook corregido")

    else:
        print("  • Sin cambios")

    try:

        subprocess.run(
            [
                "jupyter",
                "nbconvert",
                "--to", "html",
                "--execute",
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

        html_path = archivo.with_suffix(".html")
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