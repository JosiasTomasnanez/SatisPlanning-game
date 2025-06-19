@echo off
echo ===== Instalador de SatisPlanning (Windows) =====

REM Ir al directorio raíz
cd ..

REM Crear entorno virtual si no existe
if not exist env (
    python -m venv env
)

REM Activar entorno virtual
call env\Scripts\activate.bat

REM Instalar dependencias
pip install --upgrade pip
pip install .

echo.
echo ✅ Instalación completa.

REM Preguntar si quiere compilar el ejecutable
set /p COMPILAR=¿Querés compilar el ejecutable standalone ahora? (s/n):

if /I "%COMPILAR%"=="s" (
    echo 🔧 Compilando ejecutable...

    pyinstaller src\SatisPlanning\__main__.py ^
        --name SatisPlanning ^
        --onefile ^
        --paths src\ ^
        --add-data "src\SatisPlanning\assets;assets"

    echo.
    echo 🎉 Ejecutable generado en dist\SatisPlanning.exe
)

echo.
echo 🎮 Para jugar desde el entorno virtual:
echo     set PYTHONPATH=src
echo     python -m SatisPlanning

pause

