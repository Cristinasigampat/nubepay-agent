"""
parsers.py

Funciones para leer documentos de distintos formatos y devolver siempre
lo mismo: un string con el texto plano del documento.

Uso típico desde otro archivo:
    from agente.parsers import leer_documento
    texto = leer_documento(Path("docs/rh/Politica_de_beneficios_y_vacaciones.pdf"))
"""

from pathlib import Path
from pypdf import PdfReader
from docx import Document
import pandas as pd
from pptx import Presentation
from bs4 import BeautifulSoup
import json

#Recibe un parámetro ruta y retorna un string
#abrís el archivo en modo lectura ("r"), con codificación UTF-8 (para las tildes), y el with se encarga de cerrarlo solo.
def leer_texto_plano(ruta: Path) -> str:
    """Lee archivos que ya son texto plano: Markdown (.md), texto (.txt)."""
    with open(ruta, "r", encoding="utf-8") as archivo:
        return archivo.read()


def leer_pdf(ruta: Path) -> str:
    """Extrae el texto de todas las páginas de un PDF."""
    lector = PdfReader(ruta)
    texto = ""
    for pagina in lector.pages:
        texto += pagina.extract_text() + "\n"
    return texto



#abrís el documento, acumulás texto recorriendo cada párrafo, devolvés el total
def leer_word(ruta: Path) -> str:
    """Extrae el texto de todos los párrafos de un documento Word."""
    documento = Document(ruta)
    texto = ""
    for parrafo in documento.paragraphs:
        texto += parrafo.text + "\n"
    return texto


#tabla.to_string(index=False) es un método de pandas que convierte toda la tabla en un string de texto (en vez de mostrarla como tabla visual)
def leer_excel(ruta: Path) -> str:
    """Convierte una hoja de Excel a texto, fila por fila."""
    tabla = pd.read_excel(ruta)
    return tabla.to_string(index=False)


def leer_csv(ruta: Path) -> str:
    """Convierte un CSV a texto, fila por fila."""
    tabla = pd.read_csv(ruta)
    return tabla.to_string(index=False)


def leer_powerpoint(ruta: Path) -> str:
    """Extrae el texto de todas las cajas de texto de todas las diapositivas."""
    presentacion = Presentation(ruta)
    texto = ""
    for diapositiva in presentacion.slides:
        for forma in diapositiva.shapes:
            if forma.has_text_frame:
                texto += forma.text_frame.text + "\n"
    return texto


def leer_html(ruta: Path) -> str:
    """Lee un HTML y devuelve solo el texto legible, sin etiquetas."""
    with open(ruta, "r", encoding="utf-8") as archivo:
        contenido = archivo.read()
    sopa = BeautifulSoup(contenido, "html.parser")
    return sopa.get_text()

#json.load(archivo) →  convierte el JSON en un diccionario de Python.
#json.dumps() — es literalmente lo opuesto de json.load(): agarra un diccionario de Python y lo convierte en un string con formato JSON.
def leer_json(ruta: Path) -> str:
    """Lee un JSON y lo devuelve como texto legible (no como diccionario)."""
    with open(ruta, "r", encoding="utf-8") as archivo:
        datos = json.load(archivo)
    # json.dumps convierte el diccionario de vuelta a texto, pero prolijo e indentado
    return json.dumps(datos, indent=2, ensure_ascii=False)


# --- El "router": decide qué función usar según la extensión del archivo ---

def leer_documento(ruta: Path) -> str:
    """
    Función principal: recibe la ruta de CUALQUIER documento soportado
    y devuelve su texto, sin que quien la llama tenga que saber de qué
    formato se trata.
    """
    extension = ruta.suffix.lower()  # .lower() para que no importe si es .PDF o .pdf

    if extension == ".pdf":
        return leer_pdf(ruta)
    elif extension == ".docx":
        return leer_word(ruta)
    elif extension == ".xlsx":
        return leer_excel(ruta)
    elif extension == ".csv":
        return leer_csv(ruta)
    elif extension == ".pptx":
        return leer_powerpoint(ruta)
    elif extension == ".html":
        return leer_html(ruta)
    elif extension == ".json":
        return leer_json(ruta)
    elif extension == ".md":
        return leer_texto_plano(ruta)
    else:
        raise ValueError(f"Formato no soportado: {extension} (archivo: {ruta.name})")


# --- Prueba rápida del módulo ---
# Esto SOLO se ejecuta si corrés este archivo directamente
# (python src/agente/parsers.py). Si otro archivo hace "import",
# este bloque no se ejecuta -- es la forma estándar de dejar una
# mini demostración dentro de un módulo sin que moleste al importarlo.
if __name__ == "__main__":
    raiz_del_proyecto = Path(__file__).parent.parent.parent

    documentos_de_prueba = [
        "docs/operacional/FAQ_transacciones_y_limites.md",
        "docs/rh/Politica_de_beneficios_y_vacaciones.pdf",
        "docs/legal_compliance/Terminos_y_condiciones_de_uso.docx",
        "docs/financiero/Tarifas_y_comisiones_del_servicio.xlsx",
        "docs/datos_sistemas/base_clientes_simulada.csv",
        "docs/estrategico/Roadmap_estrategico_2026.pptx",
        "docs/operacional/Manual_tecnico_integracion_api_pagos.html",
        "docs/datos_sistemas/configuracion_endpoints_api.json",
    ]

    for doc_relativo in documentos_de_prueba:
        ruta_doc = raiz_del_proyecto / doc_relativo
        texto = leer_documento(ruta_doc)
        print(f"{ruta_doc.name}: {len(texto)} caracteres extraídos")
