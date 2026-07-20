"""
app_chat.py

Frontend de chat del agente NubePay, construido con Streamlit.
Las burbujas de conversación se arman con HTML/CSS propio (en vez de
un componente externo), para tener control total de los colores y
lograr la alineación estilo WhatsApp (usuario a la derecha, agente
a la izquierda).

Se conecta al backend FastAPI (api.py) por HTTP. Requiere que el
backend esté corriendo:
    uvicorn src.agente.api:app --reload

Se corre con:
    streamlit run src/agente/app_chat.py
"""

from pathlib import Path
import base64
import sys
import re
import time
import streamlit as st
from html import escape as escapar_html

sys.path.append(str(Path(__file__).parent))
from logging_agente import registrar_feedback, registrar_ejecucion
from rag_chain import responder

#URL_API = "http://localhost:8000/preguntar"
RAIZ_DEL_PROYECTO = Path(__file__).parent.parent.parent

# Versión del agente -- mismo número que en api.py y en el tag de Git.
VERSION_AGENTE = "2.0.0"

CATEGORIAS = [
    "Todas las áreas", "legal_compliance", "financiero", "rh", "estrategico",
    "operacional", "datos_sistemas", "calidad", "comunicacion_interna",
    "marketing_comercial", "investigacion_desarrollo",
]

st.set_page_config(page_title="NubePay - Agente interno", page_icon="assets/logo_transparente.png")

# --- Cargar los estilos desde el archivo CSS externo ---
ruta_css = RAIZ_DEL_PROYECTO / "assets" / "estilos.css"
with open(ruta_css, "r", encoding="utf-8") as archivo_css:
    css = archivo_css.read()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def cargar_icono_base64(ruta_relativa: str) -> str:
    """
    Lee un archivo de imagen (PNG o SVG) y lo convierte a un string
    base64 -- la forma de "meter" una imagen local dentro de HTML
    crudo, sin necesitar que Streamlit la sirva como una URL aparte.
    Si el archivo no existe, devuelve None (usamos emoji como respaldo).
    """
    ruta_completa = RAIZ_DEL_PROYECTO / ruta_relativa
    if not ruta_completa.exists():
        return None
    with open(ruta_completa, "rb") as archivo:  # "rb" = leer en modo BINARIO, no texto
        datos_binarios = archivo.read()
    return base64.b64encode(datos_binarios).decode("utf-8")


# Cargamos los íconos UNA SOLA VEZ, al arrancar la app (no en cada burbuja)
ICONO_USUARIO_B64 = cargar_icono_base64("assets/icono_usuario.png")
ICONO_AGENTE_B64 = cargar_icono_base64("assets/icono_agente.png")


def formatear_texto_burbuja(texto: str) -> str:
    """
    Convierte el texto del LLM a HTML seguro, A MANO (sin depender del
    parser de Markdown de Streamlit, que fue justo lo que rompía la
    burbuja antes). Soporta **negrita** y viñetas ("* " o "- " al
    principio de línea) -- los 2 formatos que el LLM usa seguido.
    """
    # 1. Seguridad primero: escapamos HTML y sacamos los backticks
    texto = escapar_html(texto, quote=False).replace("`", "'")

    # 2. **negrita** -> <b>negrita</b>
    texto = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", texto)

    # 3. Líneas que empiezan con "* " o "- " se agrupan en una lista <ul>
    piezas = []
    en_lista = False
    for linea in texto.split("\n"):
        limpia = linea.strip()
        es_vineta = limpia.startswith("* ") or limpia.startswith("- ")

        if es_vineta:
            if not en_lista:
                piezas.append('<ul style="margin:4px 0; padding-left:20px;">')
                en_lista = True
            piezas.append(f"<li>{limpia[2:]}</li>")
        else:
            if en_lista:
                piezas.append("</ul>")
                en_lista = False
            if limpia:
                piezas.append(f"{limpia}<br>")
    if en_lista:
        piezas.append("</ul>")

    return "".join(piezas)


def dibujar_burbuja(texto: str, es_usuario: bool) -> None:
    """
    Dibuja una burbuja de chat con HTML propio, alineada a la derecha
    (usuario) o a la izquierda (agente), con los colores de NubePay.

    --- Para cambiar colores o emojis, modificá estas 4 líneas: ---
    """
    alineacion = "flex-end" if es_usuario else "flex-start"
    color_fondo = "#0C447C" if es_usuario else "#FFFFFF"       # <- color de fondo de la burbuja
    color_texto = "#E6F1FB" if es_usuario else "#1A1A1A"       # <- color del texto de la burbuja
    borde_extra = "12px 12px 2px 12px" if es_usuario else "12px 12px 12px 2px"

    icono_b64 = ICONO_USUARIO_B64 if es_usuario else ICONO_AGENTE_B64
    if icono_b64:
        # Si conseguimos cargar el archivo de imagen, usamos <img> con el
        # base64 embebido directo en el "src" (con el prefijo "data:image/png;base64,")
        icono_html = f'<img src="data:image/png;base64,{icono_b64}" width="86" height="86">'
    else:
        # Si no hay archivo (todavía no lo subiste, o el nombre no coincide), emoji de respaldo
        icono_html = f'<span style="font-size:20px;">{"🧑" if es_usuario else "🤖"}</span>'

    texto_seguro = formatear_texto_burbuja(texto)
    html = f"""
    <div style="display:flex; justify-content:{alineacion}; margin-bottom:6px;">
        <div style="display:flex; gap:8px; max-width:75%; align-items:flex-start;
                    flex-direction:{'row-reverse' if es_usuario else 'row'};">
            {icono_html}
            <div style="background:{color_fondo}; color:{color_texto};
                        padding:10px 14px; border-radius:{borde_extra};
                        font-size:14px; line-height:1.5;">
                {texto_seguro}
            </div>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def dibujar_fuentes(texto_fuentes: str) -> None:
    """
    Muestra la línea de fuentes citadas, con color propio (en vez de
    st.caption(), que trae un gris fijo de Streamlit difícil de cambiar).

    --- Para cambiar el color, modificá esta línea: ---
    """
    color_fuentes = "#3B3939"  # <- color del texto de "Fuentes: ..."

    html = f"""
    <div style="margin:2px 0 10px 30px; font-size:12px; color:{color_fuentes};">
        ℹ️ Fuentes: {texto_fuentes}
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


def mostrar_feedback(indice: int, pregunta: str, respuesta: str) -> None:
    """
    Dibuja los botones de 👍 / 👎 debajo de una respuesta del agente,
    y registra la calificación en el log (logging_agente.py) al
    hacer clic
    """
    columna_like, columna_dislike, _ = st.columns([1, 1, 8])
    with columna_like:
        if st.button("👍", key=f"fb_pos_{indice}"):
            registrar_feedback(pregunta, respuesta, "positivo")
            st.toast("¡Gracias por tu feedback!")
    with columna_dislike:
        if st.button("👎", key=f"fb_neg_{indice}"):
            registrar_feedback(pregunta, respuesta, "negativo")
            st.toast("Gracias, vamos a revisar esta respuesta.")


# --- Barra lateral ---
with st.sidebar:
    st.image("assets/logo_transparente.png")

    st.caption("Agente de conocimiento interno")

    #Filtros 
    categoria_seleccionada = st.selectbox("Filtrar por área", CATEGORIAS)

    if st.button("Nueva conversación", help="Borra el historial del chat y empieza una conversación nueva"):
        st.session_state.historial = []


    with st.sidebar.container(key="sidebar_bottom"):
        st.image("assets/agente_nubepay.png")
        st.caption(f"v{VERSION_AGENTE}")

    st.html("""
    <style>
        .st-key-sidebar_bottom {
            position: absolute;
            bottom: 5px;
            width: 350px !important;
        }
    </style>
    """)





# --- Memoria del chat ---
if "historial" not in st.session_state:
    st.session_state.historial = []

# --- Aviso claro de que esto es un agente de IA, no una persona ---
st.markdown(
    '<div style="font-size:13px; color:#0C447C; background:rgba(255,255,255,0.5); '
    'padding:8px 12px; border-radius:8px; margin-bottom:14px; display:inline-block;">'
    '⚠️ Recuerda que estás conversando con Nuby, un <b>agente de inteligencia artificial</b>, no una persona.'
    '</div>',
    unsafe_allow_html=True,
)

# --- Mostrar el historial, con burbujas propias ---
ultima_pregunta = ""
for i, mensaje in enumerate(st.session_state.historial):
    es_usuario = mensaje["rol"] == "user"
    dibujar_burbuja(mensaje["texto"], es_usuario=es_usuario)
    if es_usuario:
        ultima_pregunta = mensaje["texto"]
    else:
        if mensaje.get("fuentes"):
            dibujar_fuentes(mensaje["fuentes"])
        mostrar_feedback(i, ultima_pregunta, mensaje["texto"])


# --- Caja de chat ---
pregunta_usuario = st.chat_input("Escribí tu pregunta sobre NubePay...")

if pregunta_usuario:
    st.session_state.historial.append({"rol": "user", "texto": pregunta_usuario})
    dibujar_burbuja(pregunta_usuario, es_usuario=True)  # se muestra YA, sin esperar el rerun

    categoria_para_api = None if categoria_seleccionada == "Todas las áreas" else categoria_seleccionada

    with st.spinner("Espera, Nuby está trabajando..."):
        inicio_tiempo = time.time()
        try:
            resultado = responder(pregunta_usuario, categoria=categoria_para_api)
            texto_respuesta = resultado["respuesta"]
            fuentes = resultado["fuentes"]
        except Exception as error:
            texto_respuesta = f"Ocurrió un error al procesar tu pregunta: {error}"
            fuentes = ""
            resultado = {"respuesta": texto_respuesta, "fuentes": "", "hubo_fallback": True}

        tiempo_ms = (time.time() - inicio_tiempo) * 1000
        registrar_ejecucion(pregunta_usuario, resultado, tiempo_ms)

    st.session_state.historial.append({
        "rol": "assistant",
        "texto": texto_respuesta,
        "fuentes": fuentes,
    })
    dibujar_burbuja(texto_respuesta, es_usuario=False)  # se muestra apenas está lista
    if fuentes:
        dibujar_fuentes(fuentes)
    mostrar_feedback(len(st.session_state.historial) - 1, pregunta_usuario, texto_respuesta)