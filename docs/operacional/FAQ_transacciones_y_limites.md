# Preguntas Frecuentes: Transacciones y Límites — NubePay

**Documento interno de soporte** · Área: Atención al Cliente / Operaciones
**Última actualización:** marzo 2026 · **Versión:** 2.3

---

## 1. Límites de transacciones

### ¿Cuáles son los límites de envío de dinero por plan?

| Plan | Límite diario | Límite mensual | Límite por transacción |
|------|---------------|-----------------|--------------------------|
| Básico (sin verificación) | USD 150 | USD 1.000 | USD 100 |
| Verificado (KYC nivel 1) | USD 1.500 | USD 15.000 | USD 1.000 |
| Verificado (KYC nivel 2) | USD 5.000 | USD 60.000 | USD 5.000 |
| Business | USD 25.000 | USD 300.000 | USD 25.000 |

> **Nota interna:** los límites de "Básico" existen para cumplir con umbrales de debida diligencia simplificada (SDD) exigidos por los reguladores locales. No deben modificarse sin aprobación de Compliance.

### ¿Qué pasa si un cliente supera su límite?

La transacción es rechazada automáticamente por el motor de riesgo (`risk-engine`) y se muestra el mensaje: *"Superaste tu límite disponible. Aumentá tu nivel de verificación para continuar."* El equipo de soporte no puede levantar el límite manualmente; el cliente debe completar la verificación KYC correspondiente desde la app.

### ¿Los límites se resetean a qué hora?

Los límites diarios se resetean a las 00:00 hora local del país del usuario. Los límites mensuales se resetean el día 1 de cada mes calendario.

---

## 2. Estados de una transacción

| Estado | Significado | Acción del agente de soporte |
|--------|--------------|-------------------------------|
| `pendiente` | En procesamiento, esperando confirmación del rail de pago | Informar que puede tardar hasta 2 horas hábiles |
| `completada` | Fondos acreditados en destino | Ninguna |
| `rechazada` | Fallo en validación (fondos insuficientes, límite excedido, cuenta destino inválida) | Explicar motivo específico del código de error |
| `en revisión` | Retenida por el motor antifraude para revisión manual | Escalar a equipo de Prevención de Fraude, no dar ETA fijo |
| `revertida` | Fondos devueltos al origen tras fallo posterior a la confirmación inicial | Confirmar que el cliente verá el reintegro en 24–48 h |

### Una transacción está "pendiente" hace más de 2 horas, ¿qué hago?

1. Verificar el estado real en el panel interno (Ops Dashboard → Transacciones).
2. Si el rail de pago external (ACH, SPEI, PIX, etc.) reporta demora, informar al cliente el tiempo estimado del rail correspondiente.
3. Si no hay registro en el rail después de 4 horas, escalar a Nivel 2 (Equipo de Pagos).

---

## 3. Reversas y disputas

### ¿Cuánto tiempo tiene un cliente para disputar una transacción no reconocida?

60 días corridos desde la fecha de la transacción, según lo establecido en la Política de Seguridad y Prevención de Fraude.

### ¿Quién autoriza una reversa manual?

Solo el equipo de Prevención de Fraude, tras abrir un caso en el sistema de casos (`fraud-case-mgmt`). Soporte de primera línea nunca ejecuta reversas manuales.

---

## 4. Errores comunes y su causa

| Código de error | Causa probable |
|------------------|-----------------|
| `ERR-101` | Fondos insuficientes en la cuenta origen |
| `ERR-204` | Límite diario o mensual excedido |
| `ERR-317` | Cuenta destino no válida o inactiva |
| `ERR-450` | Transacción bloqueada por el motor antifraude |
| `ERR-502` | Timeout del proveedor de rail de pago (reintentar en 15 min) |

---

## 5. Escalamiento

Si una consulta no está cubierta en este FAQ, escalar según el árbol:

1. **Dudas sobre límites o verificación KYC** → Equipo de Onboarding.
2. **Transacciones en revisión o posible fraude** → Equipo de Prevención de Fraude.
3. **Errores técnicos del rail de pago** → Equipo de Pagos (Ingeniería).
4. **Reclamos formales o disputas legales** → Legal y Compliance.

*Este documento es de uso interno y no debe compartirse directamente con clientes; para comunicación externa usar las plantillas aprobadas por Marketing.*
