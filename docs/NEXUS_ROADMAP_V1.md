# NEXUS — ROADMAP V1

## VISIÓN

NEXUS es un asistente cognitivo local y adaptable para personas y organizaciones.

Su objetivo es comprender cómo trabaja una persona o empresa, mantener el contexto de su actividad, recordar información relevante, asistir procesos, ejecutar acciones permitidas, verificar resultados y aprender conocimiento reutilizable para maximizar el tiempo de trabajo.

NEXUS no es:

- Solamente una IA local.
- Solamente un chatbot.
- Solamente un agente de PC.
- Solamente un sistema de automatización.
- Un producto rígido igual para todas las empresas.

La IA local es una capacidad tecnológica fundamental para permitir que la información sensible pueda permanecer dentro de la infraestructura de la organización.

---

# ARQUITECTURA OBJETIVO

```text
                         NEXUS
                           │
              ┌────────────┴────────────┐
              │                         │
       COGNITIVE CORE             ASSISTANT LAYER
              │                         │
         Understand                    User
         Context                       Organization
         Decide                        Projects
         Objective                     Documents
         Plan                          Tasks
         Execute                       Processes
         Verify                        Rules
         Learn                         Preferences
              │                        Policies
              │                         │
              └────────────┬────────────┘
                           │
                         MEMORY
                           │
              ┌────────────┼────────────┐
              │            │            │
           Working      Episodic      Semantic
              │            │            │
              └────────────┼────────────┘
                           │
                         RUNTIME
                           │
              ┌────────────┼────────────┐
              │            │            │
            Tools       Providers     Adapters
              │            │            │
              └────────────┼────────────┘
                           │
                     LOCAL SYSTEM
                           │
                         PRESENCE
                           │
                   Reactive + Proactive
```

---

## Validaciones funcionales recientes

### 1. Consulta de hora local (`system.get_time`)

**Estado:** Implementada y validada mediante pruebas unitarias y de integración.

**Fecha de validación:** 15/10/2026.

**Comportamiento validado:**

- Reconocimiento de consultas de hora en español.
- Registro de la hora local en formato HH:MM.
- Generación de una respuesta humana mediante el formateador.
- Ejecución de extremo a extremo a través de `engine.execute(...)`.

**Resultado de regresión relacionada:** 43 pruebas aprobadas, 3 warnings y 0 fallos.

**Alcance del cierre:** Se considera cerrada la incorporación de `system.get_time`. Esta validación no implica el cierre global de NEXUS V1.

### 2. Lanzamiento de aplicaciones de Windows

**Estado:** Corregido y validado mediante pruebas específicas y de regresión.

**Fecha de validación:** 19/10/2026.

**Archivo:** `packages/adapters/src/adapters/windows/app_launcher.py`.

**Corrección aplicada:** Se incorporó la espera del proceso en un hilo en segundo plano, manteniendo la apertura no bloqueante y evitando cerrar automáticamente las aplicaciones.

**Comportamiento validado:**

- Inicio de procesos mediante el lanzador de Windows.
- Gestión del proceso con una espera en segundo plano.
- Manejo de errores al iniciar procesos.
- Validación de rutas absolutas.
- Apertura de Notepad sin `ResourceWarning` en la prueba específica.

**Resultado de las pruebas:**

- 7 pruebas específicas del lanzador aprobadas.
- `tests/test_core_regression.py::test_open_app` aprobada con `-W error::ResourceWarning`.
- Suite completa aprobada sin fallos ni advertencias en la ejecución registrada.

**Resultado de regresión global:** 929 pruebas aprobadas en 6,55 segundos.

**Alcance del cierre:** Se considera corregida la incidencia del `ResourceWarning` en el lanzamiento de aplicaciones, de acuerdo con las pruebas ejecutadas. La validación no implica que todos los alias de aplicaciones hayan sido comprobados mediante aperturas reales.

### 3. Captura de pantalla

**Estado:** Corregida y validada mediante pruebas de regresión.

**Fecha de validación:** 19/10/2026.

**Archivo:** `packages/adapters/src/adapters/windows/screen_capture.py`.

**Problema identificado:** La suite registraba tres advertencias porque `mss.mss()` está obsoleto y será eliminado en una versión futura de la biblioteca.

**Corrección aplicada:** Se reemplazó `mss()` por `MSS()`.

**Comportamiento validado:**

- Captura de pantalla mediante la API `MSS()`.
- Conservación del formato de imagen RGB devuelto por el adaptador.
- Ejecución satisfactoria de la suite completa sin los tres warnings de obsolescencia identificados.

**Resultado de regresión global:** 929 pruebas aprobadas en 6,55 segundos.

**Alcance del cierre:** Se considera corregida la incidencia de obsolescencia en la captura de pantalla. Esta validación no implica el cierre global de NEXUS V1.

---

## Incidencias técnicas pendientes

### Estado de las incidencias registradas

Las dos incidencias técnicas documentadas anteriormente quedan cerradas según las pruebas ejecutadas el 19/10/2026:

1. `ResourceWarning` en el lanzamiento de aplicaciones.
2. `DeprecationWarning` en capturas de pantalla.

No se registran nuevas incidencias pendientes en esta sección a partir de estas dos correcciones. Cualquier nueva incidencia deberá incorporarse con su causa identificada, archivo relacionado, próxima acción y criterio de cierre.

---

## Estado de regresión de NEXUS V1

**Fecha de validación:** 19/10/2026.

**Resultado de la suite completa:** 929 pruebas aprobadas, 0 fallos, en 6,55 segundos.

**Validaciones específicas adicionales:**

- Lanzador de aplicaciones: 7 pruebas aprobadas.
- Prueba de regresión de apertura: 1 aprobada con `-W error::ResourceWarning`.
- Captura de pantalla: validada dentro de la suite completa.

**Criterio de mantenimiento:** Las nuevas modificaciones deben preservar los contratos existentes, mantener la separación entre Cognitive Core, Assistant Layer, Runtime, Providers y Adapters, y superar las pruebas de regresión pertinentes.

**Alcance del estado:** Este resultado confirma el estado de la suite ejecutada. No constituye por sí mismo la aprobación de todas las fases arquitectónicas, funcionales y de producto previstas para NEXUS V1.

---

## Alcance del roadmap

NEXUS V1 continúa orientado a consolidar la arquitectura cognitiva, la gestión de contexto, las capacidades operativas, la memoria, la seguridad y la adaptación organizacional.

Las correcciones técnicas registradas en este documento no modifican la visión ni el alcance de V1, y no autorizan por sí mismas nuevas fases, refactorizaciones generales o cambios de arquitectura.

El siguiente trabajo debe continuar desde el estado real del roadmap y priorizar las capacidades pendientes necesarias para completar V1, preservando las funcionalidades ya validadas.