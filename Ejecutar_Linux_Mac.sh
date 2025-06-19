#!/bin/bash
echo "==============================="
echo "🎮 Ejecutar SatisPlanning"
echo "==============================="

# Verificar si el binario existe
if [ ! -f dist/SatisPlanning ]; then
    echo
    echo "❌ No se encontró el ejecutable: dist/SatisPlanning"
    echo
    echo "🧾 Asegurate de haber ejecutado el instalador con:"
    echo "    ./install/install.sh"
    echo
    echo "🔧 Durante la instalación, seleccioná 's' cuando se te pregunte si querés compilar el ejecutable."
    echo
    exit 1
fi

# Darle permiso de ejecución por si acaso
chmod +x dist/SatisPlanning

# Ejecutar el binario
echo "✅ Ejecutable encontrado. Iniciando el juego..."
echo
./dist/SatisPlanning

