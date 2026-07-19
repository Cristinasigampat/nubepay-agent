"""
indexar_documentos.py

Recorre TODA la carpeta docs/ (las 10 categorías, los 20 documentos)
y los indexa en ChromaDB -- a diferencia de los bloques de prueba de
otros módulos, que solo indexaban 3 documentos de ejemplo.

Se corre UNA VEZ para poblar la base vectorial de punta a punta:
    python src/agente/indexar_documentos.py

Si querés reindexar desde cero, borrá la carpeta chroma_db/ antes.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
from vectorstore import obtener_coleccion, indexar_documento

RAIZ_DEL_PROYECTO = Path(__file__).parent.parent.parent
CARPETA_DOCS = RAIZ_DEL_PROYECTO / "docs"

# Extensiones que sabemos procesar (mismas que soporta parsers.py)
EXTENSIONES_SOPORTADAS = {".pdf", ".docx", ".xlsx", ".csv", ".pptx", ".html", ".json", ".md"}


def indexar_todos_los_documentos():
    coleccion = obtener_coleccion(RAIZ_DEL_PROYECTO / "chroma_db")

    total_documentos = 0
    total_chunks = 0

    # Cada subcarpeta de docs/ es una categoría (coincide con nuestras 10
    # categorías: legal_compliance, financiero, rh, etc.)
    for carpeta_categoria in sorted(CARPETA_DOCS.iterdir()):
        if not carpeta_categoria.is_dir():
            continue

        categoria = carpeta_categoria.name

        for archivo in sorted(carpeta_categoria.iterdir()):
            if archivo.suffix.lower() not in EXTENSIONES_SOPORTADAS:
                continue  # saltamos archivos que no sabemos procesar (por si hay algo suelto)

            try:
                cantidad_chunks = indexar_documento(coleccion, archivo, categoria)
                total_documentos += 1
                total_chunks += cantidad_chunks
                print(f"  {archivo.name} ({categoria}): {cantidad_chunks} chunks")
            except Exception as error:
                print(f"  ERROR indexando {archivo.name}: {error}")

    print()
    print(f"Total: {total_documentos} documentos, {total_chunks} chunks indexados.")
    print(f"Total en la colección: {coleccion.count()}")


if __name__ == "__main__":
    print("--- Indexando TODOS los documentos de docs/ ---")
    print()
    indexar_todos_los_documentos()
