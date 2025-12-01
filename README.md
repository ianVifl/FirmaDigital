FirmaDigital: Sistema de Gestión y Firma Electrónica de Documentos

Descripción del Proyecto

FirmaDigital es una plataforma web desarrollada en Python con Flask que moderniza el flujo de trabajo para la firma de documentos. El sistema permite a los usuarios cargar archivos PDF, solicitar firmas a terceros y generar documentos finales con evidencia criptográfica (Hash SHA-256) y validación mediante código QR, garantizando la integridad, autenticidad y el no repudio del proceso.

Este proyecto fue desarrollado como entrega final para la materia de [[ Ingenieria de Software ]].

Características Principales:

-Gestión de Usuarios: Registro y autenticación segura con contraseñas encriptadas (Bcrypt).

-Panel de Control (Dashboard): Visualización de documentos enviados, pendientes por firmar e historial de firmados.

-Carga Segura: Subida de archivos PDF con generación de nombres únicos (UUID).

-Firma Electrónica: * Estampado digital en el PDF.

-Generación de hoja de evidencia con fecha/hora UTC.

-Cálculo de Hash SHA-256 para integridad.

-Generación dinámica de código QR.

-Validación: Verificación visual y matemática de la firma.

️Tecnologías Utilizadas:


Backend: Python 3.12

Framework Web: Flask (Jinja2 para templates)

Base de Datos: MySQL 8.0

ORM: SQLAlchemy

Librerías Clave:

*Flask-Login: Gestión de sesiones.

*Flask-WTF: Manejo y validación de formularios.

*pypdf & reportlab: Manipulación y generación de PDFs.

*qrcode: Generación de códigos QR.

*Herramienta de IA : Claude.ai

Instalación y Ejecución:

Seguir estos pasos para ejecutar el proyecto en un entorno local:

1. Clonar el repositorio

git clone [[https://github.com/ianVifl/FirmaDigital.git]]
cd FirmaDigital


2. Crear entorno virtual

python -m venv venv
# En Windows:
venv\Scripts\activate
# En Mac/Linux:
source venv/bin/activate


3. Instalar dependencias

pip install -r requirements.txt


4. Configurar la Base de Datos

Abrir cliente SQL.

Ejecuta el script db_schema_final.sql incluido en este repositorio para crear la base de datos y las tablas.

Importante: Verifica que la URI de conexión en app.py coincida con tus credenciales locales:

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:TU_CONTRASEÑA@localhost/FirmaDigital'


5. Ejecutar la aplicación

python app.py


Abre tu navegador en: http://127.0.0.1:5000

Autores

[[ Ian Taillu Villamil Flores]] - Desarrollador

[[ Equipo #3 ]] - Colaboradores

Proyecto Académico Ingenieria de Software - 2025