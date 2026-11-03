# Runtime

Runtime ejecuta los planes generados por Engine mediante Executor y ActionManager.

## Checkpoints locales de ejecución

Bootstrap configura `SQLiteExecutionStore` en:

- `%USERPROFILE%\\.nexus\\executions.sqlite3` en Windows.
- `~/.nexus/executions.sqlite3` en otros sistemas.
- La ruta puede cambiarse con `NEXUS_EXECUTIONS_DB_PATH`.

Executor registra:
- Inicio del objetivo y solicitud original.
- Snapshot del plan, actor, paso actual, resultados, artifacts y evidencia.
- Checkpoint antes de invocar cada acción y después de su resultado.
- Estado final completado o fallido.

Si NEXUS vuelve a iniciar y encuentra ejecuciones que seguían en estado `running`, las marca como `interrupted`. **No reejecuta acciones ni intenta reanudar automáticamente**, porque una acción externa pudo haber producido efectos antes de una caída y repetirla podría duplicarlos. El snapshot conserva el paso que estaba en curso para inspección manual.

## API local

- `GET /api/executions`: últimas 50 ejecuciones.
- `GET /api/executions/{id}`: detalle y snapshot de una ejecución.
