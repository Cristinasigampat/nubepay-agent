# Procedimiento Operativo: Apertura de Cuenta — NubePay

**Área:** Operaciones / Onboarding
**Tipo de documento:** Procedimiento Operativo Estándar (POE)
**Código:** POE-OPS-004 · **Versión:** 4.1 · **Vigente desde:** enero 2026

---

## 1. Objetivo

Definir el proceso estandarizado para la apertura de una cuenta digital NubePay, garantizando el cumplimiento de los requisitos regulatorios de Conozca a su Cliente (KYC) y Prevención de Lavado de Activos (PLA/AML) en cada país donde opera la empresa.

## 2. Alcance

Aplica a todas las aperturas de cuenta iniciadas por personas físicas a través de la app móvil o el sitio web de NubePay, en Argentina, México, Colombia y Chile.

## 3. Roles involucrados

| Rol | Responsabilidad |
|-----|-------------------|
| Cliente | Completa el formulario de registro y sube documentación |
| Sistema de Onboarding (automático) | Ejecuta validaciones documentales, biometría y scoring de riesgo |
| Analista KYC (Nivel 1) | Revisa casos marcados como "revisión manual" |
| Oficial de Cumplimiento | Aprueba casos de riesgo alto o PEP (Persona Expuesta Políticamente) |

## 4. Flujo del proceso

### Paso 1 — Registro inicial
El usuario ingresa: nombre completo, número de documento, fecha de nacimiento, país de residencia, correo electrónico y número de teléfono. El sistema valida formato y duplicidad (un documento no puede asociarse a más de una cuenta activa).

### Paso 2 — Verificación de identidad (KYC)
1. Captura de foto del documento de identidad (frente y dorso).
2. Prueba de vida (*liveness check*) mediante selfie con detección de movimiento.
3. Comparación biométrica automática entre la foto del documento y la selfie (umbral mínimo de coincidencia: 92%).

> Si la coincidencia biométrica es menor al 92% pero mayor al 80%, el caso pasa a **revisión manual** por un Analista KYC. Por debajo del 80%, se rechaza automáticamente y se solicita reintentar.

### Paso 3 — Screening de listas restrictivas
El sistema consulta automáticamente:
- Listas de sanciones internacionales (OFAC, ONU, UE).
- Listas de Personas Expuestas Políticamente (PEP).
- Listas negras internas de NubePay (fraude previo).

Si hay coincidencia parcial o total, el caso se congela y se escala al Oficial de Cumplimiento, quien decide en un plazo máximo de 48 horas hábiles.

### Paso 4 — Scoring de riesgo
El motor de riesgo asigna un nivel (Bajo / Medio / Alto) según: país de residencia, monto declarado de ingresos, patrón de uso esperado y resultado del screening. Este nivel determina el límite inicial de transacciones (ver FAQ de Transacciones y Límites).

### Paso 5 — Activación de la cuenta
Si todas las validaciones son exitosas, la cuenta se activa automáticamente y el cliente recibe una notificación push y un correo de bienvenida. Tiempo objetivo del proceso completo: **menos de 5 minutos** en el 90% de los casos (SLA interno).

## 5. Casos de rechazo

| Motivo | Acción |
|--------|--------|
| Documento vencido o ilegible | Rechazo automático, se solicita nuevo intento |
| Coincidencia en lista de sanciones | Congelamiento + escalamiento a Compliance |
| Menor de 18 años | Rechazo automático, sin excepción |
| Documento ya asociado a otra cuenta | Rechazo automático, se sugiere recuperación de cuenta existente |

## 6. Indicadores de control (KPIs del proceso)

- Tasa de aprobación automática (objetivo: >85%).
- Tiempo promedio de revisión manual (objetivo: <24 h).
- Tasa de falsos rechazos reportados por el cliente (objetivo: <2%).

## 7. Referencias relacionadas

- Política de Privacidad y Protección de Datos.
- Política de Seguridad y Prevención de Fraude.
- Manual Técnico: Integración con API de Pagos.

*Documento de uso interno. Cualquier modificación al flujo descrito requiere aprobación conjunta de Operaciones y Compliance.*
