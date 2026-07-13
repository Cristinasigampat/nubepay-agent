# Registro de Fuentes y Gobierno de Documentos — NubePay

**Proyecto:** Agente de IA Corporativo NubePay
**Etapa:** 1 — Recolección y organización de documentos
**Última actualización:** julio 2026 · **Responsable del registro:** Equipo de Datos y Sistemas

---

## 1. Mapeo de las fuentes

En una empresa real como NubePay, los documentos que alimentan al agente no nacen todos en un mismo lugar. Para este proyecto simulamos la dispersión real que tendría la información en la organización, mapeando cada categoría de negocio a su sistema de origen típico:

| Categoría de negocio | Fuente de origen (simulada) | Interlocutor entrevistado (rol) |
|---|---|---|
| Legal y Compliance | Carpeta compartida SharePoint — "Legal/Vigentes" | Oficial de Cumplimiento |
| Financiero y Contable | Sistema contable interno + SharePoint Finanzas | Gerente de Finanzas |
| Recursos Humanos | Sistema de RRHH (HRIS) + Google Drive RH | Gerente de RRHH |
| Estratégico | Google Drive — carpeta del Comité Ejecutivo | VP de Estrategia |
| Operacional | Confluence técnico (equipo de Producto/Ingeniería) | Líder de Operaciones |
| Datos y Sistemas | Repositorio de código (Confluence + repos internos) | Líder de Ingeniería de Plataforma |
| Calidad | Google Drive — carpeta compartida del equipo de QA | Líder de QA |
| Comunicación Interna | Intranet corporativa + correos archivados de RRHH | Gerente de RRHH |
| Marketing y Comercial | Google Drive — carpeta de Marketing | Gerente de Marketing |
| Investigación y Desarrollo | Confluence — carpeta de Estrategia/I+D | Líder de I+D |

> **Nota metodológica:** este mapeo es el resultado de una ronda de "entrevistas" simuladas con cada área, replicando el ejercicio real que haría un equipo de Datos antes de construir un agente de este tipo: preguntar a cada dueño de proceso dónde vive *su* versión oficial de la información.

---

## 2. Categorías definidas

Se adoptaron las 10 categorías de negocio sugeridas en el desafío. Cada categoría es un metadato de primer nivel (`categoria`) que acompañará a cada documento —y luego a cada *chunk*— durante la indexación, permitiendo filtrar búsquedas (ej. "buscar solo en Legal y Compliance") y determinar a quién escalar una actualización.

Estructura adoptada en el repositorio:

```
docs/
├── legal_compliance/
├── financiero/
├── rh/
├── estrategico/
├── operacional/
├── datos_sistemas/
├── calidad/
├── comunicacion_interna/
├── marketing_comercial/
└── investigacion_desarrollo/
```

---

## 3. Curaduría de calidad

Criterios aplicados antes de que un documento entre a la base de conocimiento:

- **Vigencia:** solo se incluye la versión oficial vigente de cada política o procedimiento (identificada por número de versión y fecha de vigencia en el propio documento). Los 20 documentos de este proyecto están marcados como versión vigente única; no conviven versiones obsoletas en el repositorio.
- **No duplicidad:** se verifica que no existan dos documentos cubriendo el mismo tema con información contradictoria (ej. dos tablas de tarifas distintas).
- **Relevancia para preguntas de colaboradores:** se excluye contenido que no aporte a responder preguntas reales (notas personales, borradores de trabajo, archivos de prueba, versiones "draft_v2_final_FINAL").
- **Consistencia cruzada:** se validó que los datos que se repiten entre documentos coincidan entre sí (por ejemplo, los límites de transacciones del FAQ de Operaciones coinciden con los del Procedimiento de Apertura de Cuenta y con los códigos de error del Manual Técnico de la API).

Todo documento que no cumpla estos criterios se descarta en esta etapa y **no llega al pipeline de procesamiento** (Etapa 2).

---

## 4. Responsables (ownership) por categoría

| Categoría | Responsable (owner) | Rol de aprobación |
|---|---|---|
| Legal y Compliance | Oficial de Cumplimiento | Aprueba ingreso y actualización de políticas legales |
| Financiero y Contable | Gerente de Finanzas | Aprueba estados financieros y tarifas |
| Recursos Humanos | Gerente de RRHH | Aprueba políticas de beneficios, onboarding y comunicados |
| Estratégico | VP de Estrategia | Aprueba roadmaps y planes estratégicos |
| Operacional | Líder de Operaciones | Aprueba procedimientos operativos y FAQ de soporte |
| Datos y Sistemas | Líder de Ingeniería de Plataforma | Aprueba manuales técnicos y configuraciones de API |
| Calidad | Líder de QA | Aprueba reportes de auditoría y planes correctivos |
| Comunicación Interna | Gerente de RRHH | Aprueba comunicados internos |
| Marketing y Comercial | Gerente de Marketing | Aprueba pitch decks y tablas de precios públicas |
| Investigación y Desarrollo | Líder de I+D | Aprueba casos de negocio |

Cada owner es quien: (a) aprueba que un documento nuevo entre a la base, y (b) recibe la notificación cuando el agente detecta que un documento bajo su categoría podría estar desactualizado (por ejemplo, por antigüedad superior a 12 meses sin revisión).

---

## 5. Acceso y permisos

El agente es de **acceso abierto a todos los colaboradores de NubePay** para *consulta* — no se restringe quién puede preguntar. El control de acceso se aplica, en cambio, del lado de la **lectura de las fuentes**:

- El agente (o el proceso de ingesta) tiene permisos de **solo lectura** sobre las carpetas y sistemas de origen listados en la sección 1.
- El agente **no tiene permisos de escritura** sobre ninguna fuente: no modifica, aprueba ni reemplaza documentos por sí mismo. Toda actualización de contenido sigue pasando por el owner correspondiente (sección 4).
- No se aplican restricciones por rol o área a nivel de *respuesta* del agente, ya que toda la documentación incluida es de carácter interno-general (no se indexan, en esta fase, documentos con restricciones especiales como contratos individuales de empleados o información de clientes identificable).

---

## 6. Proceso de ingesta inicial

Para esta primera fase del proyecto se adopta un **enfoque combinado**:

### Fase actual (manual)
Los 20 documentos de la base de conocimiento se cargan **manualmente** al repositorio (`docs/`) y desde ahí al bucket de OCI Object Storage. Esto permite arrancar el proyecto sin depender de integraciones que tomarían más tiempo de desarrollo, y es consistente con el alcance de este desafío.

### Fase futura (integración automática) — Roadmap de referencia
Una vez validado el agente con la carga manual, la evolución natural del proceso de ingesta sería:

| Fuente | Mecanismo de integración futuro |
|---|---|
| SharePoint / Google Drive | Conexión vía API oficial (Microsoft Graph API / Google Drive API), sincronización periódica de carpetas designadas por cada owner |
| Confluence | Conector vía API REST de Confluence, indexando solo espacios marcados como "oficiales" |
| Sistema de RRHH (HRIS) | Exportación programada (batch) de políticas publicadas, sin exponer datos personales de colaboradores |
| Repositorios de código | Webhook que dispara re-indexación cuando se actualiza un archivo Markdown en la carpeta `/docs` de un repositorio designado |

Mientras no se implemente la integración automática, el **owner de cada categoría es responsable de notificar** al equipo de Datos y Sistemas cuando un documento nuevo deba incorporarse o uno existente deba actualizarse, para repetir la carga manual.

---

## 7. Registro maestro de documentos (Etapa 1 — resultado final)

| Documento | Categoría | Formato | Fuente de origen (simulada) | Responsable (owner) | Estado | Ingesta |
|---|---|---|---|---|---|---|
| Política de privacidad y protección de datos | Legal y Compliance | PDF | SharePoint — Legal/Vigentes | Oficial de Cumplimiento | Vigente | Manual |
| Política de seguridad y prevención de fraude | Legal y Compliance | PDF | SharePoint — Legal/Vigentes | Oficial de Cumplimiento | Vigente | Manual |
| Términos y condiciones de uso | Legal y Compliance | Word | SharePoint — Legal/Vigentes | Oficial de Cumplimiento | Vigente | Manual |
| Tarifas y comisiones del servicio | Financiero | Excel | SharePoint Finanzas | Gerente de Finanzas | Vigente | Manual |
| Estado de resultados anual | Financiero | Excel | Sistema contable interno | Gerente de Finanzas | Vigente | Manual |
| Balance general | Financiero | PDF | Sistema contable interno | Gerente de Finanzas | Vigente | Manual |
| Manual de onboarding | Recursos Humanos | Word | Google Drive RH | Gerente de RRHH | Vigente | Manual |
| Política de beneficios y vacaciones | Recursos Humanos | PDF | Sistema de RRHH (HRIS) | Gerente de RRHH | Vigente | Manual |
| Roadmap estratégico 2026 | Estratégico | PowerPoint | Google Drive — Comité Ejecutivo | VP de Estrategia | Vigente | Manual |
| FAQ transacciones y límites | Operacional | Markdown | Confluence técnico | Líder de Operaciones | Vigente | Manual |
| Procedimiento de apertura de cuenta | Operacional | Markdown | Confluence técnico | Líder de Operaciones | Vigente | Manual |
| Manual técnico: integración API de pagos | Operacional | HTML | Repositorio de código interno | Líder de Ingeniería de Plataforma | Vigente | Manual |
| Base de clientes simulada | Datos y Sistemas | CSV | Repositorio de código interno | Líder de Ingeniería de Plataforma | Vigente (datos sintéticos) | Manual |
| Configuración de endpoints API | Datos y Sistemas | JSON | Repositorio de código interno | Líder de Ingeniería de Plataforma | Vigente | Manual |
| Reporte de auditoría de calidad Q1 | Calidad | PDF | Google Drive QA | Líder de QA | Vigente | Manual |
| Plan de acción correctivo | Calidad | Word | Google Drive QA | Líder de QA | Vigente | Manual |
| Comunicado: política de home office | Comunicación Interna | Markdown | Intranet / correo archivado RRHH | Gerente de RRHH | Vigente | Manual |
| Pitch deck para inversores | Marketing y Comercial | PowerPoint | Google Drive Marketing | Gerente de Marketing | Vigente | Manual |
| Tabla de precios de planes | Marketing y Comercial | Excel | Google Drive Marketing | Gerente de Marketing | Vigente | Manual |
| Caso de negocio: expansión a Perú | Investigación y Desarrollo | Word | Confluence I+D | Líder de I+D | Vigente | Manual |

---

## 8. Limitaciones conocidas del pipeline de extracción

Decisiones de alcance tomadas conscientemente durante la Etapa 2 (procesamiento y extracción de contenido), documentadas aquí en vez de implementadas, dado el alcance de este proyecto:

- **OCR para PDFs escaneados:** el parser de PDF (`leer_pdf()`) extrae texto directo, asumiendo que el PDF es nativo (generado digitalmente). No se implementó reconocimiento óptico de caracteres (OCR) para PDFs que sean imágenes escaneadas, ya que los 20 documentos de este proyecto son todos generados digitalmente. Si en el futuro se incorporan documentos escaneados a la base de conocimiento, este es el punto del pipeline a extender.
- **Ubicación exacta dentro del documento (página, sección, diapositiva):** actualmente `leer_documento()` devuelve el texto completo de un documento como un único string, sin conservar en qué página, sección o diapositiva se originó cada fragmento. Esto significa que un chunk no puede citar "página 3" o "diapositiva 2" como fuente exacta, solo el nombre del documento de origen. Resolverlo requeriría rediseñar los parsers para devolver una lista de fragmentos con su ubicación, en vez de un string único — se dejó fuera del alcance actual por la complejidad que agrega frente al beneficio para un corpus de 20 documentos.
- **Tablas dentro de archivos PDF pierden su estructura de columnas.** A diferencia de Excel/CSV (donde usamos pandas para leer cada fila con sus columnas) y de tablas escritas en Markdown (donde `reformatear_tablas_markdown()` detecta el patrón y reconstruye "Columna: valor"), las tablas dentro de un PDF se extraen con `pypdf` como texto plano, en el orden visual de la página, **sin ningún separador que indique qué valor corresponde a qué fila o columna**. Confirmado en la práctica: en la Política de Beneficios y Vacaciones, la tabla de "antigüedad → días de vacaciones" se extrae como una lista de etiquetas seguida de una lista de valores, y un LLM (especialmente uno chico, corriendo localmente) puede asociar mal qué valor corresponde a qué antigüedad. Resolverlo de raíz requeriría reemplazar `pypdf` por una librería con detección de tablas (ej. `pdfplumber`), lo cual se evaluó y se decidió posponer — impacta un número acotado de documentos (los que tienen tablas dentro de un PDF: Balance General, Reporte de Auditoría, Política de Beneficios).

## 9. Próxima revisión

Este registro debe revisarse cada vez que se incorpore un documento nuevo a `docs/`, y como mínimo trimestralmente junto con los owners de cada categoría, para confirmar que ningún documento haya quedado desactualizado.
