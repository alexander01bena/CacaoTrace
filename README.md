# CacaoTrace Tumaco — versión Python con diseño mejorado

CacaoTrace Tumaco es una aplicación web académica desarrollada principalmente en **Python con Flask** y base de datos **SQLite**. Su propósito es registrar y consultar la trazabilidad básica de lotes de cacao desde la recepción hasta calidad, poscosecha, inventario y reportes.

> Nota práctica: el sistema funciona con Python en el backend. Los archivos HTML y CSS se usan únicamente para la interfaz visual, porque toda aplicación web necesita una capa de presentación.

## Funcionalidades incluidas

- Inicio de sesión con usuario y contraseña.
- Roles de usuario: administrador, recepción y calidad.
- Panel principal con indicadores generales.
- Gestión de usuarios.
- Registro, edición y eliminación controlada de productores.
- Registro, edición y eliminación controlada de fincas.
- Registro de recepción de cacao.
- Generación automática de códigos de lote, por ejemplo `LOT-2026-0001`.
- Gestión de lotes.
- Control de calidad: humedad, estado del grano, clasificación y observaciones.
- Registro de poscosecha: fermentación, secado y estado del proceso.
- Inventario con entradas, salidas y ajustes.
- Reportes por productor, estado, clasificación y fecha.
- Consulta pública de lote por código.
- Pruebas básicas con pytest.

## Mejoras de esta versión

- Diseño visual más moderno con panel lateral, tarjetas, métricas, botones e íconos.
- Pantalla de inicio de sesión más presentable.
- Panel principal más claro y útil.
- Navegación organizada por módulos.
- Proyecto limpio: no incluye el entorno virtual ni archivos temporales.
- CRUD conectado a rutas Python con Flask.
- Base de datos SQLite creada automáticamente al iniciar.

## Tecnologías

- Python 3.11 o superior.
- Flask.
- Flask-SQLAlchemy.
- Flask-Login.
- SQLite.
- Bootstrap 5 e íconos de Bootstrap para el diseño visual.

## Instalación rápida en Windows

1. Descomprime la carpeta del proyecto.
2. Abre la carpeta en VS Code.
3. Ejecuta el archivo:

```text
1_INSTALAR_TODO.bat
```

4. Luego ejecuta:

```text
2_INICIAR_APP.bat
```

5. Abre el navegador en:

```text
http://127.0.0.1:5000
```

## Instalación manual

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

## Usuario inicial

Al iniciar por primera vez, el sistema crea automáticamente este usuario administrador:

```text
Usuario: admin
Contraseña: admin123
```

En una entrega real o sustentación formal, conviene cambiar esa contraseña desde el módulo de usuarios.

## Ejecutar pruebas

```bash
pytest
```

También puedes usar el archivo:

```text
3_EJECUTAR_PRUEBAS.bat
```

## Estructura del proyecto

```text
cacaotrace_python_mejorado/
│   run.py
│   requirements.txt
│   README.md
│   1_INSTALAR_TODO.bat
│   2_INICIAR_APP.bat
│   3_EJECUTAR_PRUEBAS.bat
│
├── app/
│   │   __init__.py
│   │   config.py
│   │   database.py
│   │   decorators.py
│   │   models.py
│   │   routes.py
│   │   seed.py
│   │   utils.py
│   │
│   ├── static/
│   │   └── css/
│   │       └── styles.css
│   │
│   └── templates/
│       └── archivos HTML del sistema
│
└── tests/
    └── test_app.py
```

## Recomendación para usarlo en clase o sustentación

Para mostrar el sistema, entra con el usuario administrador y registra los datos en este orden:

1. Productor.
2. Finca.
3. Recepción de cacao.
4. Lote creado automáticamente.
5. Control de calidad.
6. Poscosecha.
7. Movimiento de inventario.
8. Reporte o consulta pública por código.

Ese orden evita errores porque los módulos dependen unos de otros.

## Nota sobre eliminar registros

El sistema permite eliminar datos desde la interfaz, pero con control. Algunos registros no se eliminan si tienen información relacionada. Por ejemplo, un productor con fincas, recepciones o lotes asociados no se borra directamente para evitar dañar la trazabilidad. Esta decisión es correcta para un sistema de seguimiento de cacao.


## Uso con XAMPP / MySQL

Esta versión está configurada para trabajar con MySQL de XAMPP.

1. Abrir XAMPP y activar MySQL.
2. Ejecutar `1_INSTALAR_TODO.bat`.
3. Ejecutar `4_CREAR_BASE_XAMPP.bat`.
4. Ejecutar `2_INICIAR_APP.bat`.

Conexión configurada en `app/config.py`:

```python
SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@127.0.0.1:3306/cacaotrace?charset=utf8mb4"
```

Usuario inicial:

- Usuario: `admin`
- Contraseña: `admin123`
