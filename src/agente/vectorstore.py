"""
vectorstore.py

Funciones para indexar documentos en ChromaDB y hacer búsquedas
semánticas (con o sin filtro por categoría) sobre lo ya indexado.
"""

from pathlib import Path
import chromadb

from parsers import leer_documento
from chunking import trocear_documento
from embeddings import generar_embeddings_en_lote, generar_embedding

NOMBRE_COLECCION = "documentos_nubepay"

OWNER_POR_CATEGORIA = {
    "legal_compliance": "Oficial de Cumplimiento",
    "financiero": "Gerente de Finanzas",
    "rh": "Gerente de RRHH",
    "estrategico": "VP de Estrategia",
    "operacional": "Líder de Operaciones",
    "datos_sistemas": "Líder de Ingeniería de Plataforma",
    "calidad": "Líder de QA",
    "comunicacion_interna": "Gerente de RRHH",
    "marketing_comercial": "Gerente de Marketing",
    "investigacion_desarrollo": "Líder de I+D",
}


def obtener_coleccion(ruta_persistencia: Path):
    """
    Conecta con ChromaDB (creando la carpeta de persistencia si no existe)
    y devuelve la colección lista para usar.
    """
    cliente = chromadb.PersistentClient(path=str(ruta_persistencia))
    return cliente.get_or_create_collection(
        name=NOMBRE_COLECCION,
        metadata={"hnsw:space": "cosine"},
    )


def indexar_documento(coleccion, ruta_doc: Path, categoria: str) -> int:
    """
    Procesa un documento completo (leer -> trocear -> generar embeddings)
    y lo guarda en la colección. Devuelve la cantidad de chunks indexados.
    """
    nombre_archivo = ruta_doc.name

    texto = leer_documento(ruta_doc)
    chunks = trocear_documento(texto, categoria)
    embeddings_de_chunks = generar_embeddings_en_lote(chunks)

    ids = [f"{ruta_doc.stem}_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "categoria": categoria,
            "documento_origen": nombre_archivo,
            "owner": OWNER_POR_CATEGORIA[categoria],
        }
        for _ in chunks
    ]

    coleccion.add(
        ids=ids,
        embeddings=embeddings_de_chunks.tolist(),
        documents=chunks,
        metadatas=metadatas,
    )

    return len(chunks)


def buscar(coleccion, pregunta: str, n_results: int = 3, categoria: str = None) -> list:
    """
    Busca los chunks más relevantes para una pregunta.
    Si se pasa "categoria", filtra la búsqueda solo a esa categoría.

    Devuelve una lista de diccionarios simples, uno por resultado, con
    las claves: texto, categoria, documento_origen, owner, distancia.
    (En vez del diccionario anidado que devuelve Chroma directamente.)
    """
    embedding_pregunta = generar_embedding(pregunta)

    if categoria is not None:
        resultado = coleccion.query(
            query_embeddings=[embedding_pregunta.tolist()],
            n_results=n_results,
            where={"categoria": categoria},
        )
    else:
        resultado = coleccion.query(
            query_embeddings=[embedding_pregunta.tolist()],
            n_results=n_results,
        )

    resultados_aplanados = []
    cantidad_encontrada = len(resultado["documents"][0])
    for i in range(cantidad_encontrada):
        resultados_aplanados.append({
            "texto": resultado["documents"][0][i],
            "categoria": resultado["metadatas"][0][i]["categoria"],
            "documento_origen": resultado["metadatas"][0][i]["documento_origen"],
            "owner": resultado["metadatas"][0][i]["owner"],
            "distancia": resultado["distances"][0][i],
        })

    return resultados_aplanados


# --- Prueba rápida del módulo ---
if __name__ == "__main__":
    raiz_del_proyecto = Path(__file__).parent.parent.parent
    coleccion = obtener_coleccion(raiz_del_proyecto / "chroma_db")

    documentos_de_prueba = [
        ("docs/operacional/FAQ_transacciones_y_limites.md", "operacional"),
        ("docs/legal_compliance/Politica_de_privacidad_y_proteccion_de_datos.pdf", "legal_compliance"),
        ("docs/rh/Politica_de_beneficios_y_vacaciones.pdf", "rh"),
    ]

    print("--- Indexando documentos de prueba ---")
    for doc_relativo, categoria in documentos_de_prueba:
        ruta_doc = raiz_del_proyecto / doc_relativo
        cantidad = indexar_documento(coleccion, ruta_doc, categoria)
        print(f"{ruta_doc.name}: {cantidad} chunks indexados")

    print()
    print("Total en la colección:", coleccion.count())
    print()

    print("--- Búsqueda sin filtro ---")
    resultados = buscar(coleccion, "¿Cuánto puedo transferir por día?", n_results=3)
    for r in resultados:
        print(f"[{r['distancia']:.4f}] ({r['categoria']}) {r['texto'][:100]}...")

    print()
    print("--- Búsqueda con filtro (categoria=rh) ---")
    resultados_rh = buscar(coleccion, "¿Cuántos días de vacaciones tengo?", n_results=3, categoria="rh")
    for r in resultados_rh:
        print(f"[{r['distancia']:.4f}] ({r['categoria']}) {r['texto'][:100]}...")
