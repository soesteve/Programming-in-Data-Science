#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

Este programa quita los bloques de código de un ipynb para 
generar ejercicios para los alumnos en formato html. 


python generar_ejercicios_para_alumnos_en_html.py xxxxxxxxx.ipynb


Por ejemplo:
    
    python generar_ejercicios_para_alumnos_en_html.py 6_SOLUC.ipynb
    
    genera 6_SOLUC_Ejer_Alumnos.html
    

"""


from pathlib import Path
import subprocess
import sys


def generar_html_alumnos(notebook):
    """
    Convierte un notebook de Jupyter en HTML ocultando
    las celdas de código.

    El notebook original no se modifica.

    El HTML generado tendrá el posfijo:
        Alumnos_
    """

    notebook = Path(notebook)

    # Nombre del fichero HTML
    html = notebook.with_name(
        notebook.stem + "_Ejer_Alumnos" + ".html"
    )

    # -------------------------------------------------
    # 1. Convertir el notebook a HTML
    # -------------------------------------------------

    comando = [
        sys.executable,
        "-m",
        "jupyter",
        "nbconvert",
        "--to",
        "html",
        str(notebook),
        "--output",
        html.name,
        "--output-dir",
        str(html.parent)
    ]

    subprocess.run(comando, check=True)

    # -------------------------------------------------
    # 2. Leer el HTML generado
    # -------------------------------------------------

    contenido = html.read_text(encoding="utf-8")

    # -------------------------------------------------
    # 3. CSS para ocultar el código
    # -------------------------------------------------

    css = """
<style>

div.jp-CodeCell .jp-InputArea,
div.input {
    display: none !important;
}

</style>
"""

    # -------------------------------------------------
    # 4. Botón para mostrar/ocultar código
    # -------------------------------------------------

    javascript = """
<div style="
    position: fixed;
    top: 10px;
    right: 10px;
    z-index: 9999;
">

<button onclick="mostrarOcultarCodigo()"
        style="
        padding: 8px 14px;
        font-size: 14px;
        cursor: pointer;
        border: 1px solid #888;
        border-radius: 5px;
        background: white;
        ">
    Mostrar código
</button>

</div>

<script>

let codigoVisible = false;

function mostrarOcultarCodigo() {

    const celdas = document.querySelectorAll(
        'div.jp-CodeCell .jp-InputArea, div.input'
    );

    const boton = document.querySelector('button');

    codigoVisible = !codigoVisible;

    celdas.forEach(function(celda) {

        if (codigoVisible) {
            celda.style.display = '';
        } else {
            celda.style.display = 'none';
        }

    });

    if (codigoVisible) {
        boton.textContent = 'Ocultar código';
    } else {
        boton.textContent = 'Mostrar código';
    }
}

</script>
"""

    # -------------------------------------------------
    # 5. Insertar CSS y JavaScript
    # -------------------------------------------------

    contenido = contenido.replace(
        "</head>",
        css + "\n</head>"
    )

    contenido = contenido.replace(
        "<body>",
        "<body>\n" + javascript
    )

    # -------------------------------------------------
    # 6. Guardar el HTML definitivo
    # -------------------------------------------------

    html.write_text(
        contenido,
        encoding="utf-8"
    )

    print()
    print("HTML generado correctamente:")
    print(html)
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

    generar_html_alumnos(sys.argv[1])