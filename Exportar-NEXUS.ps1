
$ErrorActionPreference = "Stop"

# ============================================================
# NEXUS - EXPORTADOR COMPLETO DE CODIGO FUENTE
# Genera archivos TXT legibles, sin comprimir.
# ============================================================

$Root = (Get-Location).Path
$Out = Join-Path $Root ("_NEXUS_EXPORT_" + (Get-Date -Format "yyyyMMdd_HHmmss"))
$MaxChars = 50000

# Directorios que no deben exportarse
$ExcludeDirs = @(
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "dist",
    "build",
    ".next",
    ".vite",
    "coverage",
    ".turbo",
    "_NEXUS_EXPORT",
    "_NEXUS_EXPORT_20261101"
)

# Extensiones binarias o archivos que no son codigo fuente
$ExcludeExtensions = @(
    ".pyc", ".pyo", ".exe", ".dll", ".so", ".bin",
    ".db", ".sqlite", ".sqlite3",
    ".zip", ".7z", ".rar",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico",
    ".pdf", ".mp4", ".mp3", ".wav",
    ".woff", ".woff2", ".ttf", ".otf",
    ".pt", ".onnx", ".safetensors"
)

# Archivos sensibles o datos locales
$ExcludeFiles = @(
    ".env",
    "state.json",
    "nexus_memory.json",
    "nexus_learning.json",
    "nexus_logs.txt",
    "credentials.json",
    "secrets.json"
)

# Crear carpeta de salida
New-Item -ItemType Directory -Force -Path $Out | Out-Null

Write-Host ""
Write-Host "NEXUS - EXPORTACION DE CODIGO FUENTE"
Write-Host "Proyecto: $Root"
Write-Host "Destino:  $Out"
Write-Host ""

# ============================================================
# 1. RECOPILAR ARCHIVOS
# ============================================================

$Files = @(
    Get-ChildItem -LiteralPath $Root -Recurse -File -Force |
    Where-Object {
        $Relative = $_.FullName.Substring($Root.Length).TrimStart('\')
        $Parts = $Relative -split '[\\/]'

        $DirectoryAllowed = -not (
            $Parts | Where-Object {
                $ExcludeDirs -contains $_
            }
        )

        $ExtensionAllowed = $ExcludeExtensions -notcontains $_.Extension.ToLower()

        $NameAllowed = $ExcludeFiles -notcontains $_.Name

        $EnvironmentAllowed = $_.Name -notlike ".env.*"

        $DirectoryAllowed -and
        $ExtensionAllowed -and
        $NameAllowed -and
        $EnvironmentAllowed
    } |
    Sort-Object FullName
)

# ============================================================
# 2. GENERAR INVENTARIO
# ============================================================

$Manifest = Join-Path $Out "00_INVENTARIO.txt"

$Inventory = @(
    "NEXUS - INVENTARIO DE ARCHIVOS"
    "Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    "Raiz: $Root"
    "Archivos encontrados: $($Files.Count)"
    ""
    "ARCHIVOS:"
    ""
)

$Inventory += @(
    $Files | ForEach-Object {
        $_.FullName.Substring($Root.Length).TrimStart('\')
    }
)

Set-Content -LiteralPath $Manifest -Value $Inventory -Encoding UTF8

Write-Host "Inventario generado: $($Files.Count) archivos"

# ============================================================
# 3. EXPORTAR CODIGO EN PARTES
# ============================================================

$Part = 1
$Buffer = ""
$Exported = 0
$Failed = 0

foreach ($File in $Files) {

    try {

        $Relative = $File.FullName.Substring($Root.Length).TrimStart('\')

        # Leer como texto UTF-8
        $Content = [System.IO.File]::ReadAllText($File.FullName)

        $Block = @"

================================================================================
ARCHIVO: $Relative
================================================================================

$Content

================================================================================
FIN DEL ARCHIVO
================================================================================

"@

        # Si supera el limite, guardar la parte actual
        if (
            ($Buffer.Length + $Block.Length) -gt $MaxChars -and
            $Buffer.Length -gt 0
        ) {

            $Name = "NEXUS_CODIGO_PARTE_{0:D3}.txt" -f $Part

            Set-Content `
                -LiteralPath (Join-Path $Out $Name) `
                -Value $Buffer `
                -Encoding UTF8

            Write-Host "Generada: $Name"

            $Part++
            $Buffer = ""
        }

        $Buffer += $Block
        $Exported++

    }
    catch {

        $Failed++

        $ErrorFile = Join-Path $Out "ERRORES_EXPORTACION.txt"

        Add-Content `
            -LiteralPath $ErrorFile `
            -Value "$($File.FullName): $($_.Exception.Message)" `
            -Encoding UTF8
    }
}

# Guardar ultima parte
if ($Buffer.Length -gt 0) {

    $Name = "NEXUS_CODIGO_PARTE_{0:D3}.txt" -f $Part

    Set-Content `
        -LiteralPath (Join-Path $Out $Name) `
        -Value $Buffer `
        -Encoding UTF8

    Write-Host "Generada: $Name"
}

# ============================================================
# 4. EXPORTAR ESTADO GIT
# ============================================================

Write-Host ""
Write-Host "Recopilando estado de Git..."

Push-Location $Root

try {

    $GitCommands = @(
        @{
            Name = "GIT_ESTADO.txt"
            Args = @("status", "--short", "--branch")
        },
        @{
            Name = "GIT_CAMBIOS_TRACKED.txt"
            Args = @("diff", "--no-ext-diff", "--no-color")
        },
        @{
            Name = "GIT_CAMBIOS_STAGED.txt"
            Args = @("diff", "--no-ext-diff", "--no-color", "--cached")
        }
    )

    foreach ($Command in $GitCommands) {

        $PreviousPreference = $ErrorActionPreference
        $ErrorActionPreference = "Continue"

        $GitOutput = & git @($Command.Args) 2>&1

        $GitOutput |
            ForEach-Object {
                "$_"
            } |
            Set-Content `
                -LiteralPath (Join-Path $Out $Command.Name) `
                -Encoding UTF8

        $ErrorActionPreference = $PreviousPreference
    }

}
catch {

    $ErrorFile = Join-Path $Out "ERRORES_EXPORTACION.txt"

    Add-Content `
        -LiteralPath $ErrorFile `
        -Value "Error al obtener estado Git: $($_.Exception.Message)" `
        -Encoding UTF8
}
finally {

    $ErrorActionPreference = "Stop"
    Pop-Location
}

# ============================================================
# 5. RESUMEN
# ============================================================

$Summary = @"

NEXUS - RESUMEN DE EXPORTACION

Fecha: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Proyecto: $Root

Archivos encontrados: $($Files.Count)
Archivos exportados: $Exported
Errores de lectura: $Failed
Partes de codigo generadas: $Part

Archivos generados:

00_INVENTARIO.txt
NEXUS_CODIGO_PARTE_001.txt ...
GIT_ESTADO.txt
GIT_CAMBIOS_TRACKED.txt
GIT_CAMBIOS_STAGED.txt

Los archivos sensibles y binarios fueron excluidos.

"@

Set-Content `
    -LiteralPath (Join-Path $Out "RESUMEN_EXPORTACION.txt") `
    -Value $Summary `
    -Encoding UTF8

Write-Host ""
Write-Host "============================================"
Write-Host "EXPORTACION TERMINADA"
Write-Host "============================================"
Write-Host "Archivos encontrados: $($Files.Count)"
Write-Host "Archivos exportados:  $Exported"
Write-Host "Errores:              $Failed"
Write-Host "Partes generadas:     $Part"
Write-Host "Destino:              $Out"
Write-Host "============================================"
