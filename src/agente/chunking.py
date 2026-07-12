"""
chunking.py

Funciones para trocear ("chunkear") el texto de un documento en
pedazos más chicos, listos para convertirse en embeddings 
y guardarse en la base vectorial .
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configuración de chunking recomendada por tipo de categoría,
# Formato: "categoria": (chunk_size, chunk_overlap)
CONFIGURACION_POR_CATEGORIA = {
    "legal_compliance": (1000, 100),      # políticas largas, ideas desarrolladas en varias oraciones
    "financiero": (600, 60),               # mezcla de texto y datos de tablas
    "rh": (800, 80),
    "estrategico": (800, 80),
    "operacional": (500, 50),              # incluye FAQ, chunks más chicos
    "datos_sistemas": (500, 50),
    "calidad": (800, 80),
    "comunicacion_interna": (500, 50),
    "marketing_comercial": (600, 60),
    "investigacion_desarrollo": (800, 80),
}

# Si una categoría no está en el diccionario de arriba, usamos esta configuración por defecto.
CONFIGURACION_DEFAULT = (500, 50)


def obtener_configuracion_chunking(categoria: str) -> tuple:
    """
    Devuelve (chunk_size, chunk_overlap) recomendados para una categoría dada.
    Si la categoría no está definida, devuelve la configuración por defecto.
    """
    return CONFIGURACION_POR_CATEGORIA.get(categoria, CONFIGURACION_DEFAULT)


def trocear_texto(texto: str, chunk_size: int = 500, chunk_overlap: int = 50) -> list:
    """
    Trocea un texto en una lista de chunks, usando RecursiveCharacterTextSplitter.
    """
    separador = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    return separador.split_text(texto)


def trocear_documento(texto: str, categoria: str) -> list:
    """
    Trocea un texto usando la configuración recomendada para su categoría.
    Esta es la función que el resto del proyecto va a usar normalmente
    (en vez de llamar a trocear_texto directamente con números a mano).
    """
    chunk_size, chunk_overlap = obtener_configuracion_chunking(categoria)
    return trocear_texto(texto, chunk_size=chunk_size, chunk_overlap=chunk_overlap)


# --- Prueba rápida del módulo ---
if __name__ == "__main__":
    from pathlib import Path
    import sys

    # Sumamos la carpeta "agente" al path para poder importar parsers.py
    sys.path.append(str(Path(__file__).parent))
    from parsers import leer_documento

    raiz_del_proyecto = Path(__file__).parent.parent.parent

    documentos_de_prueba = [
        ("docs/operacional/FAQ_transacciones_y_limites.md", "operacional"),
        ("docs/legal_compliance/Terminos_y_condiciones_de_uso.docx", "legal_compliance"),
    ]

    for doc_relativo, categoria in documentos_de_prueba:
        ruta_doc = raiz_del_proyecto / doc_relativo
        texto = leer_documento(ruta_doc)
        chunks = trocear_documento(texto, categoria)
        chunk_size, chunk_overlap = obtener_configuracion_chunking(categoria)

        print(f"{ruta_doc.name}")
        print(f"  Categoría: {categoria} -> chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
        print(f"  Caracteres totales: {len(texto)} -> {len(chunks)} chunks generados")
        print()
