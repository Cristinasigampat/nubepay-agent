"""
reranking.py

Reordena los candidatos recuperados por la búsqueda semántica (vectorstore.py),
usando un modelo cross-encoder: un modelo que evalúa la pregunta y cada
candidato JUNTOS (a diferencia de los embeddings, que los evalúan por
separado). Es más lento, pero más preciso -- se usa sobre un conjunto
chico de candidatos, no sobre toda la colección.
"""

from sentence_transformers import CrossEncoder

NOMBRE_MODELO_RERANKER = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"

print(f"Cargando modelo de reranking ({NOMBRE_MODELO_RERANKER})...")
modelo_reranker = CrossEncoder(NOMBRE_MODELO_RERANKER)
print("Modelo de reranking cargado.")


def rerank(pregunta: str, candidatos: list, top_n: int = 3) -> list:
    """
    Reordena una lista de candidatos (los diccionarios que devuelve
    vectorstore.buscar(), cada uno con una clave "texto") según su
    relevancia REAL respecto a la pregunta.

    Devuelve los "top_n" mejores, ya reordenados, con un campo nuevo:
    "score_rerank".
    """
    if not candidatos:
        return []

    # Armamos una lista de pares [pregunta, texto_del_candidato],
    # uno por cada candidato -- así es como el cross-encoder espera la entrada.
    pares = [[pregunta, candidato["texto"]] for candidato in candidatos]

    # .predict() evalúa TODOS los pares de una vez, y devuelve
    # un score por cada uno (más alto = más relevante).
    scores = modelo_reranker.predict(pares)

    # Le agregamos el score nuevo a cada candidato (mismo diccionario de antes,
    # con un campo extra).
    for candidato, score in zip(candidatos, scores):
        candidato["score_rerank"] = float(score)

    # Ordenamos la lista de mayor a menor score de reranking
    # (no el score de distancia que ya traían de Chroma).
    candidatos_ordenados = sorted(candidatos, key=lambda c: c["score_rerank"], reverse=True)

    return candidatos_ordenados[:top_n]


# --- Prueba rápida del módulo ---
if __name__ == "__main__":
    from pathlib import Path
    import sys

    sys.path.append(str(Path(__file__).parent))
    from vectorstore import obtener_coleccion, indexar_documento, buscar

    raiz_del_proyecto = Path(__file__).parent.parent.parent
    coleccion = obtener_coleccion(raiz_del_proyecto / "chroma_db")

    # Reutilizamos la colección ya indexada en la Clase 6
    # (si está vacía, indexamos los mismos 3 documentos de prueba)
    if coleccion.count() == 0:
        documentos_de_prueba = [
            ("docs/operacional/FAQ_transacciones_y_limites.md", "operacional"),
            ("docs/legal_compliance/Politica_de_privacidad_y_proteccion_de_datos.pdf", "legal_compliance"),
            ("docs/rh/Politica_de_beneficios_y_vacaciones.pdf", "rh"),
        ]
        for doc_relativo, categoria in documentos_de_prueba:
            ruta_doc = raiz_del_proyecto / doc_relativo
            indexar_documento(coleccion, ruta_doc, categoria)

    pregunta = "¿Cuánto puedo transferir por día?"

    print(f"Pregunta: {pregunta}")
    print()

    # Paso 1: traemos MÁS candidatos que los que realmente queremos usar
    # (10 en vez de 3) -- esto le da material al reranker para elegir mejor.
    candidatos = buscar(coleccion, pregunta, n_results=10)

    print("--- ANTES del reranking (orden de la búsqueda semántica) ---")
    for c in candidatos[:5]:
        print(f"[distancia {c['distancia']:.4f}] ({c['categoria']}) {c['texto'][:80]}...")
    print()

    # Paso 2: reordenamos esos candidatos con el cross-encoder,
    # y nos quedamos con los 3 mejores según el reranker.
    mejores = rerank(pregunta, candidatos, top_n=3)

    print("--- DESPUÉS del reranking (orden real de relevancia) ---")
    for c in mejores:
        print(f"[score {c['score_rerank']:.4f}] ({c['categoria']}) {c['texto'][:80]}...")
