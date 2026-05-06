# CacaoTrace
# 🍫 CacaoTrace Tumaco

Sistema web para la trazabilidad y control de calidad de lotes de cacao en Tumaco.

---

## 📌 Descripción

**CacaoTrace Tumaco** es una aplicación web que permite gestionar el ciclo completo del cacao desde su recepción hasta su control de calidad, poscosecha, inventario y generación de reportes.

El sistema está diseñado para garantizar la **trazabilidad del producto**, mejorar el control de procesos y facilitar la toma de decisiones.

---

## 🎯 Objetivo

Desarrollar un sistema funcional que permita registrar, controlar y consultar información relacionada con la producción de cacao, asegurando un flujo organizado desde el productor hasta el inventario final.

---

## 🚀 Funcionalidades principales

* 🔐 Autenticación de usuarios (login/logout)
* 👥 Gestión de usuarios y roles
* 👨‍🌾 Registro de productores
* 🌱 Registro de fincas
* 📦 Recepción de cacao
* 🏷️ Generación de lotes con código único
* 📊 Control de calidad (humedad, clasificación, estado)
* 🔄 Procesos de poscosecha (fermentación, secado)
* 📋 Gestión de inventario
* 📈 Generación de reportes
* 🔎 Consulta por código de lote
* 🧪 Pruebas del sistema

---

## 🛠️ Tecnologías utilizadas

* **Frontend:** HTML, CSS, JavaScript
* **Backend:** *(Especificar: PHP / Node.js / Java)*
* **Base de datos:** *(Especificar: PostgreSQL / MySQL)*
* **Control de versiones:** Git y GitHub

---

## 🧱 Arquitectura

El sistema sigue una arquitectura **cliente-servidor**, utilizando el patrón de diseño **MVC (Modelo - Vista - Controlador)**, separando:

* Capa de presentación (Frontend)
* Lógica de negocio (Backend)
* Persistencia de datos (Base de datos)

---

## 📂 Estructura del proyecto

```bash
CacaoTrace/
│
├── src/                # Código fuente
├── docs/               # Documentación Scrum
│   ├── sprint-0.docx
│   ├── sprint-1.docx
│   ├── sprint-2.docx
│   ├── sprint-3.docx
│   └── sprint-4.docx
├── README.md
└── .gitignore
```

---

## ⚙️ Instalación

1. Clonar el repositorio:

```bash
git clone https://github.com/tu-usuario/cacaotrace.git
```

2. Acceder al proyecto:

```bash
cd cacaotrace
```

3. Instalar dependencias:

```bash
# Ejemplo:
npm install
# o
composer install
```

4. Configurar la base de datos:

* Crear la base de datos
* Importar script SQL
* Configurar credenciales en el proyecto

5. Ejecutar el servidor:

```bash
# Ejemplo:
npm start
# o
php artisan serve
```

6. Abrir en el navegador:

```
http://localhost:3000
```

---

## 📊 Metodología de desarrollo

El proyecto fue desarrollado utilizando la metodología ágil **Scrum**, dividido en 4 sprints:

* **Sprint 0:** Planeación, backlog y arquitectura
* **Sprint 1:** Base del sistema (login, usuarios, productores, fincas)
* **Sprint 2:** Recepción de cacao, lotes e inventario
* **Sprint 3:** Control de calidad y poscosecha
* **Sprint 4:** Reportes, pruebas y documentación final

---

## 👥 Equipo de trabajo

* **Product Owner:** Elisa Hurtado
* **Scrum Master:** Alexander Rodriguez
* **Team Lead:** Elisa Hurtado, Alexander Rodriguez
* **Desarrolladores:** Elisa Hurtado, Alexander Rodriguez

---

## 📄 Licencia

Este proyecto es de uso académico para la asignatura **Ingeniería de Software III**.

---

## 📌 Autoría

Proyecto desarrollado por el equipo **CacaoTrace Team**.
