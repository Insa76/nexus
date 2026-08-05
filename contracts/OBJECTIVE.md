# OBJECTIVE CONTRACT
Versión: 1.0
Estado: Aprobado

--------------------------------------------------

PROPÓSITO

Representa un resultado de negocio que NEXUS debe conseguir.

Un Objective nunca representa una acción individual.

Un Objective siempre representa un resultado esperado.

--------------------------------------------------

RESPONSABILIDADES

✓ Mantener el propósito del trabajo.

✓ Mantener el estado de ejecución.

✓ Mantener el contexto necesario.

✓ Registrar el resultado esperado.

✓ Mantener el historial del objetivo.

--------------------------------------------------

NO ES RESPONSABLE DE

✗ Ejecutar trabajo.

✗ Conocer modelos de IA.

✗ Conocer herramientas.

✗ Conocer proveedores.

✗ Conocer implementaciones.

--------------------------------------------------

CICLO DE VIDA

CREATED

↓

PLANNED

↓

RUNNING

↓

WAITING

↓

VALIDATING

↓

COMPLETED

o

FAILED

o

CANCELLED

--------------------------------------------------

ATRIBUTOS MÍNIMOS

id

Identificador único.

--------------------------------------------------

source

Origen del objetivo.

Ejemplos

Usuario

Evento

API

Sistema

--------------------------------------------------

title

Descripción breve.

Ejemplo

Preparar Orden de Pago.

--------------------------------------------------

expected_result

Qué debe existir al finalizar.

Ejemplo

Orden de Pago lista para aprobación.

--------------------------------------------------

context

Información necesaria para comprender el objetivo.

--------------------------------------------------

priority

LOW

NORMAL

HIGH

CRITICAL

--------------------------------------------------

status

Estado actual.

--------------------------------------------------

constraints

Restricciones del negocio.

Ejemplos

Solo procesamiento local.

Debe aprobar Finanzas.

No enviar información externa.

--------------------------------------------------

plan_reference

Referencia al plan generado.

Nunca contiene el plan.

Solo la referencia.

--------------------------------------------------

execution_history

Historial cronológico.

--------------------------------------------------

created_at

--------------------------------------------------

updated_at