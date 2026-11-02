# NEXUS V1 — ejecución y validación

## Ruta modular de desarrollo validada

Desde `C:\Users\cdi40\Desktop\nexus`:

```powershell
uv run python -u .\server.py
```

El runtime modular escucha en `127.0.0.1:8765`. Ejecutar la suite Python:

```powershell
uv run pytest -q --ignore=backups --ignore=dist --ignore=build
uv run python -m compileall -q .\packages .\tests .\server.py .\nexus_http_security.py
```

## Consola React + Electron en desarrollo

Desde la raíz del proyecto, ejecutar:

```powershell
.\start-nexus-desktop-dev.ps1
```

El script comprueba la API en `http://127.0.0.1:8765/api/status`, inicia `apps/console` con Vite en `127.0.0.1:5173` si hace falta y después abre Electron. Los logs quedan en `%TEMP%\NEXUS_V1_DESKTOP_LOGS`.

Para validar Python, las pruebas y la compilación React:

```powershell
.\VERIFICAR_NEXUS_INTEGRACION.ps1
```

El build React no es un instalador comercial. La distribución final todavía requiere empaquetar el runtime Python, verificar instalación limpia, actualización, desinstalación y recuperación.

## Otras líneas del repositorio

`backend/` + `dashboard/` y `desktop/` son rutas distintas/legadas y no se fusionan con el runtime modular en esta fase. El objetivo de este parche es dejar una ruta de desarrollo coherente: `server.py` + `apps/console` + `electron`.

## Seguridad

El runtime debe permanecer en loopback. No exponerlo en una red ni publicar el servidor sin diseñar autenticación, autorización y una política de seguridad de producción.
