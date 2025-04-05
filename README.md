# SatisPlanning-game

## Explicación y uso de Git Flow
1. **Inicializar Git Flow**  
   Si es la primera vez que usas Git Flow en tu repositorio, lo primero que debes hacer es inicializarlo:  
   ```bash
   git flow init
   ```
   Este comando configura las ramas predeterminadas **(master y develop)** y establece cómo se gestionarán las ramas de características **(feature)**, correcciones **(hotfix)** y versiones **(release)**. Durante la configuración, el comando te pedirá que confirmes ciertos valores predeterminados (puedes presionar Enter para aceptar).

2. **Crear una rama de feature (característica)**  
   Para crear una nueva rama de característica (feature) desde develop:  
   ```bash
   git flow feature start nombre-feature
   ```
   Esto crea una rama llamada `feature/nombre-feature` basada en develop.

3. **Trabajar en una rama de feature**  
   Una vez que hayas creado la rama de feature, puedes hacer tus cambios y commits como lo harías normalmente.  
   - Ver el estado de la rama:  
     ```bash
     git status
     ```
   - Agregar cambios:  
     ```bash
     git add .
     ```
   - Hacer commit:  
     ```bash
     git commit -m "Descripción de lo que se cambió"
     ```

4. **Finalizar una rama de feature**  
   Cuando termines de trabajar en tu rama de feature y quieras integrarla a **develop**, usa el siguiente comando:  
   ```bash
   git flow feature finish nombre-feature
   ```
   Esto:  
   - Hace un merge de la rama `feature/nombre-feature` en develop.  
   - Borra la rama `feature/nombre-feature` localmente.  
   - Si hay conflictos, te pedirá resolverlos antes de hacer el merge.

5. **Crear una rama de release (versión)**  
   Cuando estés listo para preparar una nueva versión, puedes crear una rama de release. Esto es útil para hacer pruebas y ajustes antes de la liberación final.  
   ```bash
   git flow release start nombre-release
   ```
   Esto crea una rama basada en develop que será utilizada para hacer las pruebas y ajustes finales antes de la versión.

6. **Finalizar una rama de release**  
   Cuando hayas terminado con la rama de release, necesitas integrarla en master (para la versión final) y en develop (para que los cambios de la rama de release estén disponibles en futuras características).  
   ```bash
   git flow release finish nombre-release
   ```
   Esto:  
   - Hace un merge de la rama `release/nombre-release` en master.  
   - Hace un merge de la rama `release/nombre-release` en develop.  
   - Crea una etiqueta (tag) en master con el nombre de la versión.  
   - Borra la rama `release/nombre-release` localmente.

7. **Crear una rama de hotfix (corrección rápida)**  
   Si necesitas hacer una corrección rápida en producción, por ejemplo, un bug en la rama master, puedes crear una rama de hotfix.  
   ```bash
   git flow hotfix start nombre-hotfix
   ```
   Esto crea una rama basada en master para que puedas hacer una corrección urgente.

8. **Finalizar una rama de hotfix**  
   Cuando termines de trabajar en la corrección, integra los cambios tanto en master (para que la corrección esté en producción) como en develop (para que los cambios estén disponibles en futuras versiones).  
   ```bash
   git flow hotfix finish nombre-hotfix
   ```
   Esto:  
   - Hace un merge de la rama `hotfix/nombre-hotfix` en master.  
   - Hace un merge de la rama `hotfix/nombre-hotfix` en develop.  
   - Crea una etiqueta (tag) en master con el nombre de la versión.  
   - Borra la rama `hotfix/nombre-hotfix` localmente.

9. **Ver el estado de Git Flow**  
   Si en algún momento necesitas ver el estado actual de las ramas gestionadas por Git Flow, usa:  
   ```bash
   git flow status
   ```
   Esto te mostrará en qué rama estás trabajando y las ramas de feature, release y hotfix activas.

### Resumen de Comandos Principales
- Inicializar Git Flow:  
  ```bash
  git flow init
  ```
- Crear una rama de feature:  
  ```bash
  git flow feature start nombre-feature
  ```
- Finalizar una rama de feature:  
  ```bash
  git flow feature finish nombre-feature
  ```
- Crear una rama de release:  
  ```bash
  git flow release start nombre-release
  ```
- Finalizar una rama de release:  
  ```bash
  git flow release finish nombre-release
  ```
- Crear una rama de hotfix:  
  ```bash
  git flow hotfix start nombre-hotfix
  ```
- Finalizar una rama de hotfix:  
  ```bash
  git flow hotfix finish nombre-hotfix
  ```
- Ver el estado de Git Flow:  
  ```bash
  git flow status
  ```

### Pasos adicionales con git push
1. **Después de finalizar una rama de feature**  
   Cuando termines de trabajar en una rama de feature y la hayas integrado a develop con el comando `git flow feature finish`, puedes hacer un push para subir los cambios a develop:  
   ```bash
   git push origin develop
   ```

2. **Después de finalizar una rama de release**  
   Cuando termines la rama de release con el comando `git flow release finish`, los cambios se integran tanto a master como a develop. Asegúrate de hacer push a ambas ramas:  
   ```bash
   git push origin master
   git push origin develop
   ```