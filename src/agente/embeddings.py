"""
embeddings.py

Funciones para convertir texto en embeddings (vectores numéricos),
usando un modelo local de sentence-transformers
"""

from sentence_transformers import SentenceTransformer, util

NOMBRE_MODELO = "paraphrase-multilingual-MiniLM-L12-v2"

# Esta línea se ejecuta UNA SOLA VEZ, apenas se importa este módulo
# por primera vez en el programa -- no cada vez que se llama a una función.
print(f"Cargando modelo de embeddings ({NOMBRE_MODELO})...")
modelo = SentenceTransformer(NOMBRE_MODELO)
print("Modelo cargado.")


def generar_embedding(texto: str):
    """
    Genera el embedding de UN SOLO texto (por ejemplo, la pregunta
    de un colaborador). Devuelve un vector.
    """
    return modelo.encode(texto)


def generar_embeddings_en_lote(textos: list) -> list:
    """
    Genera los embeddings de una LISTA de textos a la vez (por ejemplo,
    todos los chunks de un documento). 
    """
    return modelo.encode(textos)


def calcular_similitud(embedding_a, embedding_b) -> float:
    """
    Calcula la similitud coseno entre dos embeddings.
    Devuelve un número (float) entre 0 y 1 -- más alto significa
    más parecido en significado.
    """
    resultado = util.cos_sim(embedding_a, embedding_b)
    return resultado.item()


# --- Prueba rápida del módulo ---
if __name__ == "__main__":
    from pathlib import Path
    import sys

    sys.path.append(str(Path(__file__).parent))
    from parsers import leer_documento
    from chunking import trocear_documento

    raiz_del_proyecto = Path(__file__).parent.parent.parent

    ruta_doc = raiz_del_proyecto / "docs" / "operacional" / "FAQ_transacciones_y_limites.md"
    texto = leer_documento(ruta_doc)
    chunks = trocear_documento(texto, categoria="operacional")

    print()
    print(f"Documento: {ruta_doc.name}")
    print(f"Cantidad de chunks: {len(chunks)}")

    #devuelve un vector por cada chunk
    embeddings_de_chunks = generar_embeddings_en_lote(chunks)
    print(f"Cantidad de embeddings generados: {len(embeddings_de_chunks)}")
    print(f"Dimensión de cada embedding: {len(embeddings_de_chunks[0])}")

    print()
    pregunta_usuario = "¿Cuánto puedo transferir por día?"
    embedding_pregunta = generar_embedding(pregunta_usuario)

    print(f"Pregunta: {pregunta_usuario}")
    print()
    print("Similitud contra cada chunk del documento:")
    for i, embedding_chunk in enumerate(embeddings_de_chunks):
        similitud = calcular_similitud(embedding_pregunta, embedding_chunk)
        print(f"  Chunk {i}: {similitud:.4f}")
    print("--- Chunk 1 ---")
    print(chunks[1])
    print()
    print("--- Chunk 4 ---")
    print(chunks[4])