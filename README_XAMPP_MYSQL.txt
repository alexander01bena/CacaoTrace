CACAOTRACE CON BASE DE DATOS MYSQL EN XAMPP

Pasos para ejecutar:

1. Abre XAMPP.
2. Activa MySQL.
3. Ejecuta 1_INSTALAR_TODO.bat para instalar las librerías.
4. Ejecuta 4_CREAR_BASE_XAMPP.bat para crear/importar la base de datos cacaotrace.
5. Ejecuta 2_INICIAR_APP.bat para iniciar el sistema.

Datos de acceso inicial:
Usuario: admin
Contraseña: admin123

Archivo principal modificado:
app/config.py

La conexión actual está configurada para XAMPP así:
mysql+pymysql://root:@127.0.0.1:3306/cacaotrace?charset=utf8mb4

Si tu MySQL tiene contraseña, cambia MYSQL_PASSWORD en app/config.py o usa una variable de entorno.

Archivo SQL incluido:
cacaotrace_xampp_mysql.sql

Este proyecto ya no usa SQLite como base principal. Ahora trabaja con MySQL/MariaDB de XAMPP.
