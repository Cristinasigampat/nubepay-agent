"""
rag_chain.py

Arma la cadena RAG completa: recibe una pregunta, recupera y rerankea
los chunks relevantes, decide si hay suficiente confianza para responder,
genera la respuesta con el LLM, y arma la lista de fuentes citadas de
forma confiable (en código, sin depender de que el LLM la recuerde bien).
"""

from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate

from vectorstore import obtener_coleccion, buscar
from reranking import rerank

# Umbral de confianza para el score del reranker. Después de varias rondas
# de calibración (Clases 7-8), confirmamos que un solo número no puede
# distinguir con precisión "relevante pero mezclado con otro tema" de
# "totalmente irrelevante" -- ambos casos terminan demasiado cerca en la
# escala del cross-encoder para un corte confiable.
#
# Por eso, el umbral ahora cumple un rol más chico: descartar únicamente
# candidatos con un score MUY negativo (casos extremos, sin relación
# alguna). La decisión fina de "¿esto realmente responde la pregunta?"
# se la delegamos al LLM, reforzando la instrucción del prompt para que
# evalúe el contexto con criterio antes de responder.
# Dos umbrales con propósitos distintos:
# - UMBRAL_CONTEXTO: qué candidatos le mostramos al LLM como contexto (flojo,
#   a propósito -- preferimos darle de más y que el LLM decida, en vez de
#   filtrar nosotras de antemano con un número que ya vimos que es frágil).
# - UMBRAL_CITACION: qué candidatos citamos como fuente en la respuesta final
#   (más estricto -- acá el costo de ser exigentes de más es solo citar de
#   menos, nunca una cita engañosa).
UMBRAL_CONTEXTO = -6.0
UMBRAL_CITACION = -3.5

# Frase exacta que le pedimos al LLM que use cuando el contexto no alcanza
# para responder. La definimos una sola vez acá para no repetirla (y
# arriesgarnos a que quede escrita distinto) en el prompt y en la lógica
# de responder() que la detecta después.
FRASE_SIN_INFO = "No encontré información suficiente en los documentos disponibles para responder esa pregunta."

PLANTILLA_PROMPT = PromptTemplate(
    input_variables=["contexto", "pregunta"],
    template=f"""Sos un asistente interno de NubePay. Tu tarea es responder la
pregunta del colaborador basándote ÚNICAMENTE en el siguiente contexto.

Antes de responder, evaluá con cuidado:
1. ¿El contexto realmente contiene información que responde ESPECÍFICAMENTE
esta pregunta? Si el contexto no tiene relación real con la pregunta, o solo
la roza sin responderla, respondé EXACTAMENTE esta frase, sin agregar nada
más: "{FRASE_SIN_INFO}"
2. Si el contexto incluye rangos o límites numéricos (por ejemplo, "1 a 3
años", "menos de 1 año", distintos límites por plan), fijate con cuidado en
qué rango o categoría corresponde EXACTAMENTE al caso de la pregunta antes
de responder -- no asumas el primer valor que veas.

Si el contexto SÍ tiene la información, respondé de forma clara, amigable y
conversacional, con tus propias palabras -- NO copies el contexto tal cual
ni repitas el formato "Columna: valor". Pero prestá atención: no omitas
NINGÚN detalle relevante del contexto (plazos, montos, requisitos,
condiciones) solo por resumir con tus palabras -- una respuesta
conversacional puede y debe incluir todos los detalles importantes.

NO inventes información que no esté en el contexto, y NO uses conocimiento
externo.

Contexto:
{{contexto}}

Pregunta: {{pregunta}}

Respuesta:"""
)

raiz_del_proyecto = Path(__file__).parent.parent.parent

# Cargamos el LLM y la conexión a Chroma UNA SOLA VEZ, al importar el módulo
# (mismo criterio que ya usamos en embeddings.py y reranking.py).
llm = ChatOpenAI(
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",
    model="gemma-3-4b-it",
    temperature=0.3,
)
coleccion = obtener_coleccion(raiz_del_proyecto / "chroma_db")


def armar_contexto(chunks: list) -> str:
    """Concatena los chunks en un solo texto, cada uno con su fuente."""
    partes = [f"[Fuente: {c['documento_origen']}]\n{c['texto']}" for c in chunks]
    return "\n\n---\n\n".join(partes)


def armar_fuentes(chunks: list) -> str:
    """
    Arma la lista de fuentes citadas EN CÓDIGO (no le pedimos al LLM que
    las recuerde -- así la cita es siempre exacta). Evita repetir el mismo
    documento si aparece en más de un chunk.
    """
    vistos = set()
    lineas = []
    for chunk in chunks:
        clave = (chunk["documento_origen"], chunk["categoria"])
        if clave not in vistos:
            vistos.add(clave)
            lineas.append(f"- {chunk['documento_origen']} (categoría: {chunk['categoria']})")
    return "\n".join(lineas)


def responder(pregunta: str, categoria: str = None, n_candidatos: int = 10, top_n: int = 3) -> dict:
    """
    Función principal del agente: recibe una pregunta y devuelve un
    diccionario con la respuesta final y sus fuentes, o un fallback
    si no se encontró información suficientemente confiable.
    """
    candidatos = buscar(coleccion, pregunta, n_results=n_candidatos, categoria=categoria)

    if not candidatos:
        return {
            "respuesta": "No encontré información relacionada con tu pregunta en la base de conocimiento disponible.",
            "fuentes": "",
            "hubo_fallback": True,
        }

    mejores_chunks = rerank(pregunta, candidatos, top_n=top_n)

    # Filtramos, CHUNK POR CHUNK, cuáles le mostramos al LLM como contexto.
    # Este umbral es flojo A PROPÓSITO -- preferimos darle al LLM material
    # de sobra y que decida él mismo si alcanza para responder.
    chunks_para_contexto = [c for c in mejores_chunks if c["score_rerank"] >= UMBRAL_CONTEXTO]

    if not chunks_para_contexto:
        return {
            "respuesta": (
                "No encontré información relevante en la documentación de NubePay "
                "para responder esa pregunta. Si tu consulta es sobre un tema de la "
                "empresa, te recomiendo contactar al área correspondiente (RRHH, "
                "Legal, Finanzas, Operaciones, etc.) para más detalles."
            ),
            "fuentes": "",
            "hubo_fallback": True,
        }

    contexto = armar_contexto(chunks_para_contexto)
    prompt_final = PLANTILLA_PROMPT.format(contexto=contexto, pregunta=pregunta)
    respuesta_llm = llm.invoke(prompt_final)
    respuesta_texto = respuesta_llm.content

    # Si el LLM decidió, por su propio criterio, que el contexto no alcanza
    # para responder (usando la frase exacta que le pedimos en el prompt),
    # no tiene sentido citar fuentes -- no las usó realmente para responder.
    if FRASE_SIN_INFO in respuesta_texto:
        return {
            "respuesta": respuesta_texto,
            "fuentes": "",
            "hubo_fallback": True,
        }

    # Para CITAR fuentes usamos el umbral más estricto -- un chunk puede
    # haber pasado el filtro flojo de contexto (y haberle servido al LLM
    # de "descarte" para decidir que no era lo que buscaba) sin que eso
    # signifique que merece aparecer como fuente de la respuesta final.
    chunks_para_citar = [c for c in chunks_para_contexto if c["score_rerank"] >= UMBRAL_CITACION]

    return {
        "respuesta": respuesta_texto,
        "fuentes": armar_fuentes(chunks_para_citar) if chunks_para_citar else "",
        "hubo_fallback": False,
    }


# --- Prueba rápida del módulo ---
if __name__ == "__main__":
    from vectorstore import indexar_documento

    # Si la colección está vacía (por ejemplo, después de borrar chroma_db/
    # para reindexar con una nueva configuración de chunking), la volvemos
    # a poblar con los mismos 3 documentos de prueba de las clases anteriores.
    if coleccion.count() == 0:
        print("Colección vacía -- indexando documentos de prueba...")
        documentos_de_prueba = [
            ("docs/operacional/FAQ_transacciones_y_limites.md", "operacional"),
            ("docs/legal_compliance/Politica_de_privacidad_y_proteccion_de_datos.pdf", "legal_compliance"),
            ("docs/rh/Politica_de_beneficios_y_vacaciones.pdf", "rh"),
        ]
        for doc_relativo, categoria in documentos_de_prueba:
            ruta_doc = raiz_del_proyecto / doc_relativo
            indexar_documento(coleccion, ruta_doc, categoria)
        print("Indexación completa.")
        print()

    preguntas_de_prueba = [
        "¿Cuánto puedo transferir por día?",
        "¿NubePay tiene oficinas físicas en Miami?",
        "¿Cuál es la capital de Argentina?",
        "¿Para solicitar vacaciones necesito autorización?",
        "¿Cuantos días de vacaciones me corresponden si tengo 1 año de antigüedad?",
    ]

    for pregunta in preguntas_de_prueba:
        resultado = responder(pregunta)
        print(f"Pregunta: {pregunta}")
        print(f"Respuesta: {resultado['respuesta']}")
        if resultado["fuentes"]:
            print("Fuentes consultadas:")
            print(resultado["fuentes"])
        print(f"(hubo_fallback: {resultado['hubo_fallback']})")
        print()