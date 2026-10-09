#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Este programa quita los bloques de código de un ipynb para 
generar ejercicios para los alumnos en formato ipynb. 


python generar_ejercicios_para_alumnos_en_ipynb.py xxxxxxxxx.ipynb


Por ejemplo en terminal:
    
    python generar_ejercicios_para_alumnos_en_ipynb.py 6_Ejerc_PEATONES.ipynb
    
    genera 6_SOLUC_Ejer_Alumnos.html
    

"""

import nbformat
from pathlib import Path
import sys


def crear_recuadro():
    """
    Crea una celda Markdown que muestra el recuadro
    'ESCRIBE TU CÓDIGO PYTHON'.
    """

    return nbformat.v4.new_markdown_cell("""
<div style="
    text-align: center;
    font-size: 10px;
">

ESCRIBE TU CÓDIGO PYTHON
</div>
""")


def crear_celda_respuesta(celda_original):
    """
    Crea una celda de código vacía para que el alumno
    escriba su solución, conservando las salidas
    de la celda original.
    """

    celda = nbformat.v4.new_code_cell("")

    # Conservar las salidas de la solución
    celda.outputs = celda_original.outputs.copy()

    # No mostrar número de ejecución
    celda.execution_count = None

    # Marcar como respuesta del alumno
    celda.metadata["tags"] = ["respuesta-alumno"]

    return celda


def generar_notebook_alumnos(nombre_notebook):

    entrada = Path(nombre_notebook)

    # Comprobar que existe
    if not entrada.exists():
        print(f"ERROR: no se encuentra {entrada}")
        return

    # Nombre de salida:
    # 6_SOLUCIÓN.ipynb
    #       ↓
    # 6_SOLUCIÓN_Alumnos.ipynb

    salida = entrada.with_name(
        entrada.stem + "_Alumnos.ipynb"
    )

    # Leer notebook original
    nb_original = nbformat.read(
        entrada,
        as_version=4
    )

    # Crear un notebook nuevo
    nb_alumnos = nbformat.v4.new_notebook()

    # Copiar metadatos del notebook original
    nb_alumnos.metadata = nb_original.metadata.copy()

    # Procesar las celdas
    for celda in nb_original.cells:

        # ---------------------------------------------
        # Celdas Markdown
        # ---------------------------------------------

        if celda.cell_type == "markdown":

            nb_alumnos.cells.append(celda)

        # ---------------------------------------------
        # Celdas de código
        # ---------------------------------------------

        elif celda.cell_type == "code":

            # Añadir recuadro
            nb_alumnos.cells.append(
                crear_recuadro()
            )

            # Añadir celda vacía para el alumno
            nb_alumnos.cells.append(
                crear_celda_respuesta(celda)
            )

    # Guardar notebook
    nbformat.write(
        nb_alumnos,
        salida
    )

    print()
    print("Notebook para alumnos creado correctamente:")
    print()
    print(salida)
    print()


# =====================================================
# PROGRAMA PRINCIPAL
# =====================================================

if __name__ == "__main__":

    if len(sys.argv) != 2:

        print(
            "Uso:\n"
            "python generar_ejercicios_para_alumnos.py "
            "nombre_notebook.ipynb"
        )

        sys.exit(1)

    generar_notebook_alumnos(
        sys.argv[1]
    )