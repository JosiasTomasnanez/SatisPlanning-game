#!/bin/bash
echo "===== Instalador de SatisPlanning (Linux/macOS) ====="

# Ir al directorio raíz
cd ..

# Crear entorno virtual si no existe
if [ ! -d "env" ]; then
    python3 -m venv env
fi

# Activar entorno virtual
source env/bin/activate

# Instalar dependencias
pip install --upgrade pip
pip install .

echo
echo "✅ Instalación completa."

# Preguntar si desea compilar el ejecutable
read -p "¿Querés compilar el ejecutable standalone ahora? (s/n): " compilar

if [ "$compilar" = "s" ] || [ "$compilar" = "S" ]; then
    echo "🔧 Compilando ejecutable..."

    pyinstaller src/SatisPlanning/__main__.py \
      --name SatisPlanning \
      --onefile \
      --paths src/ \
      --add-data "src/SatisPlanning/assets:assets"

    echo
    echo "🎉 Ejecutable generado en dist/SatisPlanning"
fi

echo
echo "🎮 Para jugar desde el entorno:"
echo "    PYTHONPATH=src python -m SatisPlanning"

