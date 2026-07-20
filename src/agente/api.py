"""
api.py

Expone el agente RAG de NubePay como un servicio web con FastAPI.
Endpoint principal: POST /preguntar
"""

import sys
import time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

sys.path.append(str(Path(__file__).parent))
from rag_chain import responder
from logging_agente import registrar_ejecucion

#Versión del agente -- subimos este número (siguiendo versionado semántico:
# MAYOR.MENOR.PARCHE) cada vez que hacemos un release importante, y lo
# reflejamos también en un tag de Git (ver Plan_de_clases_RAG.md).
VERSION_AGENTE = "2.0.0"

app = FastAPI(
    title="Agente NubePay ☁️💸​​",
    description="Agente de IA corporativo de NubePay ** Responde preguntas de colaboradores basándose en la documentación interna.",
    version=VERSION_AGENTE,
)


# --- Forma de los datos que recibimos ---
class PreguntaRequest(BaseModel):
    pregunta: str
    categoria: Optional[str] = None  # opcional: filtrar la búsqueda a una sola categoría


# --- Forma de los datos que devolvemos ---
class RespuestaResponse(BaseModel):
    respuesta: str
    fuentes: str
    hubo_fallback: bool


@app.get("/")
def inicio():
    return {"mensaje": "Agente NubePay activo. Visitá /docs para probar los endpoints.", "version": VERSION_AGENTE}


@app.post("/preguntar", response_model=RespuestaResponse)
def preguntar(pedido: PreguntaRequest):
    """
    Recibe una pregunta de un colaborador, la procesa con la cadena RAG
    completa (búsqueda + reranking + LLM), registra la ejecución en el
    log, y devuelve la respuesta con sus fuentes.
    """
    inicio_tiempo = time.time()
    resultado = responder(pedido.pregunta, categoria=pedido.categoria)
    tiempo_ms = (time.time() - inicio_tiempo) * 1000

    registrar_ejecucion(pedido.pregunta, resultado, tiempo_ms)

    return resultado