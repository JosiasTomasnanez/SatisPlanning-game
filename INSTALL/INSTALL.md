# 🎮 Instalación de SatisPlanning

Bienvenido/a al instalador de **SatisPlanning**, un juego de aventura 2D hecho en Python con Pygame.

Este proyecto no incluye aún un instalador `.exe`, pero podés instalarlo fácilmente desde los scripts incluidos.

---

## 📁 Estructura del proyecto relevante

SatisPlanning-game/
├── install/
│ ├── install.sh # Script para Linux/macOS
│ ├── install.bat # Script para Windows
│ └── INSTALL.md # Este archivo
├── dist/
│ └── SatisPlanning # Ejecutable generado por PyInstaller
├── run.sh # Script para lanzar el juego
├── pyproject.toml
├── src/
│ └── SatisPlanning/

---

## ✅ Requisitos

- Python **3.10 o superior**
- pip
- (Linux/macOS) Bash
- (Windows) CMD o PowerShell

---

## 🐧 Instalación en Linux/macOS

Desde la carpeta `install/`
podes optar por ejecutar en la terminal:
```bash
./INSTALL_LINUX_MAC.sh
```
o sino ejecutar el archivo directamante con doble click y luego "ejecutar".
Durante el proceso podés elegir si querés compilar el ejecutable (dist/SatisPlanning).

##🪟 Instalación en Windows

Desde la carpeta `install/`, ejecutar:

`INSTALL_WINDOWS.bat`

Durante la instalación podrás elegir si querés compilar el .exe (dist\SatisPlanning.exe).


##🎮 Cómo ejecutar el juego

**✅ Si generaste el ejecutable**

En la carpeta principal:

- En Linux/macOS:
```bash
   ./Ejecutar_Linux_Mac.sh
```
o doble click en Ejecutar_Linux_Mac.sh

- En Windows ejecuta:

`Ejecutar_Windows.bat`
o tambien podrias ejecutar
`dist\SatisPlanning.exe`

- 🐍 Si preferís correrlo con Python (sin ejecutable):

`set PYTHONPATH=src` # En Windows
o
`export PYTHONPATH=src`  # En Linux/macOS

`python -m SatisPlanning`

##💡 Notas adicionales

- El ejecutable funciona sin necesidad de Python instalado (ideal para usuarios finales).

- El entorno virtual es opcional, pero recomendado para desarrolladores.

¡Gracias por jugar SatisPlanning! 🙌

---

