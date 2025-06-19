@echo off
if not exist dist\SatisPlanning.exe (
    echo ❌ Ejecutable no encontrado en dist\SatisPlanning.exe
    echo Asegurate de haber corrido install.bat y elegido compilar el ejecutable.
    pause
    exit /b
)

echo 🎮 Ejecutando SatisPlanning...
dist\SatisPlanning.exe
pause

