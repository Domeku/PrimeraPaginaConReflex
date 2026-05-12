# 📋 Task Manager — Organizador de Tareas con Reflex

Una aplicación web de gestión de tareas diarias con sistema de prioridades,
modo oscuro, login por usuario y persistencia de datos. Desarrollada con Python
y Reflex como práctica de desarrollo web.

## ✨ Funcionalidades

- 🔐 Login y registro de usuarios
- 📌 Tareas con prioridad Alta / Media / Baja
- 🕐 Horario: Todo el día / Hora específica / Sin fecha
- 💾 Persistencia de datos con SQLite
- 🌙 Modo claro y modo oscuro por usuario
- ✅ Marcar tareas como completadas
- 🗑️ Eliminar tareas

## 🛠️ Tecnologías

- **Python 3.11+**
- **Reflex** — Framework web full-stack en Python
- **Poetry** — Gestión de dependencias
- **SQLite** — Base de datos (incluida con Reflex)

## 📋 Requisitos Previos

Antes de instalar, necesitas tener:

- Python 3.9 o superior
- Node.js 18 o superior
- Poetry

### Instalar Poetry

**Windows (PowerShell):**
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

**Mac/Linux:**
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

## 🚀 Instalación y Ejecución

```bash
# 1. Clonar el repositorio
git clone https://github.com/TU-USUARIO/task-manager.git
cd task-manager

# 2. Instalar dependencias con Poetry
poetry install

# 3. Ejecutar la aplicación
poetry run reflex run
```

Abre tu navegador en: **http://localhost:3000**

## 📁 Estructura del Proyecto

task-manager/
├── task_manager/
│   ├── init.py
│   └── task_manager.py   ← código principal
├── rxconfig.py           ← configuración de Reflex
├── pyproject.toml        ← dependencias (Poetry)
└── README.md

## 👤 Uso

1. Ve a `http://localhost:3000/login`
2. Regístrate con usuario y contraseña
3. Agrega tareas con el botón **"+ Nueva tarea"**
4. Filtra por prioridad con los botones de filtro
5. Marca tareas como completadas con el checkbox
6. Alterna el tema con el botón **☀️ / 🌙**