### EVALUACIÓN 2 - Programación de Aplicaciones
## Backend y Django REST Framework

El siguiente es el repositorio que aloja el proyecto de API REST para la evaluación 2 de Programación de Aplicaciones.

# Clonar repositorio

Para clonar el repositorio, asegúrese de que Git esté instalado en su computador. De no ser así, puede descargarlo e instalarlo desde sus páginas oficiales.

Luego, en CMD o terminal, escriba:

```
git clone https://github.com/MatiasValencia/prufodis-ucen-apirest.git
```

Una vez realizado esto, diríjase a la carpeta donde está el proyecto. Debe llamarse "prufodis-ucen-apirest", y dentro de la carpeta está el proyecto mismo "prufodisucen".

# Verificar instalación de Python

Luego, verifique que Python esté instalado en su computador. Su versión de Python puede ser distinta, así que los comandos pueden cambiar. Verifique su versión probando estos siguientes ejemplos:
```
python3 --version
python --version
py --version
```

Si uno de ellos o todos funcionan, use esos comandos. Si no funciona, puede descargar Python desde sus páginas oficiales, e instalarlo.

# Verificar e instalar MySQL y herramientas

Luego, verifique que MySQL Community Server y MySQL Workbench estén instalados, de no ser así, puede instalarlos desde las páginas oficiales.

**IMPORTANTE:** La versión de MySQL Server debe ser 8.4 o posterior, para que pueda funcionar con Django.

En MySQL Workbench, cree una nueva conexión llamada:
```
prufodisucen
```
Los nombres de usuario y contraseña, para este proyecto, van a ser "root" y "123456", respectivamente. Verifique la conexión haciendo clic en "Test Connection". Si todo resulta bien, puede apretar en OK para crear la conexión.

Dentro de la DB, debe aparecer el esquema "prufodis". De no ser así, créela haciendo clic derecho en el espacio de las esquemas, luego en "Create Schema", y asígnele el nombre "prufodis", y luego haga clic en OK.

# Instalar paquetes

Una vez dentro del proyecto en "prufodis-ucen-apirest/prufodisucen", abra una terminal. En Windows, haga clic en la barra de ruta del proyecto, y escriba "cmd", y luego presione Enter.

Después, en la terminal, ejecute:
```
pip install -r requirements.txt
```
Esto descargará e instalará todos los paquetes necesarios para que el proyecto funcione.

# Migrar modelos a la base y ejecutar proyecto

Luego, si las tablas dentro del esquema "prufodis" no están, en esa misma terminal, ejecute:
```
python3 manage.py makemigrations
python3 manage.py migrate
```
Esto creará las tablas en la base de datos.

Y luego, para levantar el proyecto, ejecute:
```
python3 manage.py runserver
```
Esto le mostrará un link donde usted podrá acceder haciendo clic en él, mientras presiona Ctrl en su teclado. Usted deberá acceder a la interfaz de Django REST Framework.