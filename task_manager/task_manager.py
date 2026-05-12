"""
Task Manager - Aplicación de gestión de tareas con Reflex
Práctica 1 - Desarrollo Web
"""

import reflex as rx
from datetime import datetime
import hashlib
from typing import Optional


# ─────────────────────────────────────────
#  MODELOS DE BASE DE DATOS
# ─────────────────────────────────────────

class User(rx.Model, table=True):
    """Tabla de usuarios en la base de datos."""
    username: str
    password_hash: str
    dark_mode: bool = False


class Task(rx.Model, table=True):
    """Tabla de tareas en la base de datos."""
    user_id: int
    title: str
    description: str = ""
    priority: str = "Media"      # Alta, Media, Baja
    schedule_type: str = "Todo el día"  # Todo el día, Hora específica, Sin fecha
    task_time: str = ""          # "14:30" si tiene hora
    task_date: str = ""          # "2024-12-25"
    completed: bool = False
    created_at: str = ""


# ─────────────────────────────────────────
#  FUNCIONES AUXILIARES
# ─────────────────────────────────────────

def hash_password(password: str) -> str:
    """Convierte la contraseña en un hash seguro."""
    return hashlib.sha256(password.encode()).hexdigest()


# ─────────────────────────────────────────
#  ESTADO DE LA APLICACIÓN
# ─────────────────────────────────────────

class AppState(rx.State):
    """
    Estado global de la aplicación.
    Todas las variables aquí son reactivas: cuando cambian,
    la interfaz se actualiza automáticamente.
    """

    # ── Sesión ──
    current_user_id: int = 0
    current_username: str = ""
    is_logged_in: bool = False

    # ── Formulario de login/registro ──
    login_username: str = ""
    login_password: str = ""
    login_error: str = ""
    show_register: bool = False

    # ── Tareas ──
    tasks: list[dict] = []

    # ── Formulario nueva tarea ──
    new_title: str = ""
    new_description: str = ""
    new_priority: str = "Media"
    new_schedule_type: str = "Todo el día"
    new_time: str = ""
    new_date: str = ""
    show_task_form: bool = False

    # ── UI ──
    dark_mode: bool = False
    filter_priority: str = "Todas"

    # ────────── AUTENTICACIÓN ──────────

    def handle_login(self):
        """Inicia sesión con el usuario y contraseña dados."""
        if not self.login_username or not self.login_password:
            self.login_error = "Por favor completa todos los campos"
            return

        pwd_hash = hash_password(self.login_password)
        with rx.session() as session:
            user = session.exec(
                User.select().where(
                    User.username == self.login_username,
                    User.password_hash == pwd_hash
                )
            ).first()

        if user:
            self.current_user_id = user.id
            self.current_username = user.username
            self.dark_mode = user.dark_mode
            self.is_logged_in = True
            self.login_error = ""
            self.login_username = ""
            self.login_password = ""
            self._load_tasks()
            return rx.redirect("/")
        else:
            self.login_error = "Usuario o contraseña incorrectos"

    def handle_register(self):
        """Registra un nuevo usuario."""
        if not self.login_username or not self.login_password:
            self.login_error = "Por favor completa todos los campos"
            return

        if len(self.login_password) < 4:
            self.login_error = "La contraseña debe tener al menos 4 caracteres"
            return

        with rx.session() as session:
            existing = session.exec(
                User.select().where(User.username == self.login_username)
            ).first()

            if existing:
                self.login_error = "Ese nombre de usuario ya existe"
                return

            new_user = User(
                username=self.login_username,
                password_hash=hash_password(self.login_password),
                dark_mode=False,
            )
            session.add(new_user)
            session.commit()
            session.refresh(new_user)
            self.current_user_id = new_user.id
            self.current_username = new_user.username
            self.dark_mode = False
            self.is_logged_in = True
            self.login_error = ""
            self.login_username = ""
            self.login_password = ""
            self.tasks = []
            return rx.redirect("/")

    def logout(self):
        """Cierra la sesión del usuario actual."""
        self.current_user_id = 0
        self.current_username = ""
        self.is_logged_in = False
        self.tasks = []
        self.dark_mode = False
        return rx.redirect("/login")

    def toggle_register_form(self):
        """Alterna entre el formulario de login y el de registro."""
        self.show_register = not self.show_register
        self.login_error = ""

    # ────────── TAREAS ──────────

    def _load_tasks(self):
        """Carga las tareas del usuario actual desde la base de datos."""
        with rx.session() as session:
            db_tasks = session.exec(
                Task.select().where(Task.user_id == self.current_user_id)
            ).all()
            self.tasks = [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "priority": t.priority,
                    "schedule_type": t.schedule_type,
                    "task_time": t.task_time,
                    "task_date": t.task_date,
                    "completed": t.completed,
                    "created_at": t.created_at,
                }
                for t in db_tasks
            ]

    def add_task(self):
        """Agrega una nueva tarea a la base de datos."""
        if not self.new_title.strip():
            return

        with rx.session() as session:
            task = Task(
                user_id=self.current_user_id,
                title=self.new_title.strip(),
                description=self.new_description.strip(),
                priority=self.new_priority,
                schedule_type=self.new_schedule_type,
                task_time=self.new_time if self.new_schedule_type == "Hora específica" else "",
                task_date=self.new_date,
                completed=False,
                created_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            )
            session.add(task)
            session.commit()

        self._load_tasks()
        self.new_title = ""
        self.new_description = ""
        self.new_priority = "Media"
        self.new_schedule_type = "Todo el día"
        self.new_time = ""
        self.new_date = ""
        self.show_task_form = False

    def toggle_complete(self, task_id: int):
        """Marca o desmarca una tarea como completada."""
        with rx.session() as session:
            task = session.get(Task, task_id)
            if task:
                task.completed = not task.completed
                session.add(task)
                session.commit()
        self._load_tasks()

    def delete_task(self, task_id: int):
        """Elimina una tarea de la base de datos."""
        with rx.session() as session:
            task = session.get(Task, task_id)
            if task:
                session.delete(task)
                session.commit()
        self._load_tasks()

    # ────────── UI ──────────

    def toggle_dark_mode(self):
        """Alterna el tema claro/oscuro y lo guarda en la base de datos."""
        self.dark_mode = not self.dark_mode
        with rx.session() as session:
            user = session.get(User, self.current_user_id)
            if user:
                user.dark_mode = self.dark_mode
                session.add(user)
                session.commit()

    def toggle_task_form(self):
        """Muestra u oculta el formulario de nueva tarea."""
        self.show_task_form = not self.show_task_form

    def set_filter(self, priority: str):
        """Cambia el filtro de prioridad activo."""
        self.filter_priority = priority

    # ── Setters para los campos del formulario ──
    def set_login_username(self, val: str):
        self.login_username = val

    def set_login_password(self, val: str):
        self.login_password = val

    def set_new_title(self, val: str):
        self.new_title = val

    def set_new_description(self, val: str):
        self.new_description = val

    def set_new_priority(self, val: str):
        self.new_priority = val

    def set_new_schedule_type(self, val: str):
        self.new_schedule_type = val

    def set_new_time(self, val: str):
        self.new_time = val

    def set_new_date(self, val: str):
        self.new_date = val

    # ── Propiedades computadas ──
    @rx.var
    def filtered_tasks(self) -> list[dict]:
        """Devuelve las tareas filtradas por prioridad."""
        if self.filter_priority == "Todas":
            return self.tasks
        return [t for t in self.tasks if t["priority"] == self.filter_priority]

    @rx.var
    def pending_count(self) -> int:
        return sum(1 for t in self.tasks if not t["completed"])

    @rx.var
    def completed_count(self) -> int:
        return sum(1 for t in self.tasks if t["completed"])


# ─────────────────────────────────────────
#  COLORES Y ESTILOS
# ─────────────────────────────────────────

PRIORITY_COLORS = {
    "Alta": "#ef4444",
    "Media": "#f59e0b",
    "Baja": "#22c55e",
}

PRIORITY_BG = {
    "Alta": "#fef2f2",
    "Media": "#fffbeb",
    "Baja": "#f0fdf4",
}

PRIORITY_BG_DARK = {
    "Alta": "#3b1111",
    "Media": "#3b2f00",
    "Baja": "#0f2a1a",
}


def get_theme(dark: bool) -> dict:
    """Devuelve los colores del tema actual."""
    if dark:
        return {
            "bg": "#0f172a",
            "surface": "#1e293b",
            "card": "#1e293b",
            "border": "#334155",
            "text": "#f1f5f9",
            "text_muted": "#94a3b8",
            "accent": "#6366f1",
            "accent_hover": "#818cf8",
            "btn_text": "#ffffff",
        }
    return {
        "bg": "#f8fafc",
        "surface": "#ffffff",
        "card": "#ffffff",
        "border": "#e2e8f0",
        "text": "#1e293b",
        "text_muted": "#64748b",
        "accent": "#6366f1",
        "accent_hover": "#4f46e5",
        "btn_text": "#ffffff",
    }


# ─────────────────────────────────────────
#  COMPONENTES DE LA INTERFAZ
# ─────────────────────────────────────────

def login_page() -> rx.Component:
    """Página de login y registro."""
    theme = get_theme(False)  # login siempre en claro

    return rx.box(
        rx.center(
            rx.vstack(
                # Logo / título
                rx.vstack(
                    rx.text("📋", font_size="3em"),
                    rx.heading("Task Manager", size="7", color=theme["accent"]),
                    rx.text(
                        "Organiza tu día, prioriza tu vida",
                        color=theme["text_muted"],
                        font_size="0.95em",
                    ),
                    align="center",
                    spacing="1",
                ),

                # Tarjeta del formulario
                rx.box(
                    rx.vstack(
                        rx.heading(
                            rx.cond(AppState.show_register, "Crear cuenta", "Iniciar sesión"),
                            size="5",
                            color=theme["text"],
                        ),
                        rx.input(
                            placeholder="Nombre de usuario",
                            value=AppState.login_username,
                            on_change=AppState.set_login_username,
                            width="100%",
                        ),
                        rx.input(
                            placeholder="Contraseña",
                            type="password",
                            value=AppState.login_password,
                            on_change=AppState.set_login_password,
                            width="100%",
                        ),
                        rx.cond(
                            AppState.login_error != "",
                            rx.text(
                                AppState.login_error,
                                color="#ef4444",
                                font_size="0.85em",
                            ),
                        ),
                        rx.button(
                            rx.cond(AppState.show_register, "Registrarme", "Entrar"),
                            on_click=rx.cond(
                                AppState.show_register,
                                AppState.handle_register,
                                AppState.handle_login,
                            ),
                            width="100%",
                            background=theme["accent"],
                            color="white",
                            _hover={"background": theme["accent_hover"]},
                        ),
                        rx.divider(),
                        rx.button(
                            rx.cond(
                                AppState.show_register,
                                "¿Ya tienes cuenta? Inicia sesión",
                                "¿No tienes cuenta? Regístrate",
                            ),
                            on_click=AppState.toggle_register_form,
                            variant="ghost",
                            color=theme["accent"],
                            width="100%",
                            font_size="0.9em",
                        ),
                        spacing="3",
                        width="100%",
                    ),
                    padding="2em",
                    background=theme["card"],
                    border_radius="12px",
                    border=f"1px solid {theme['border']}",
                    box_shadow="0 4px 24px rgba(0,0,0,0.08)",
                    width="360px",
                ),
                spacing="5",
                align="center",
            ),
            min_height="100vh",
        ),
        background=theme["bg"],
        min_height="100vh",
    )


def task_card(task: dict) -> rx.Component:
    """Tarjeta visual para una tarea individual."""
    priority = task["priority"]

    return rx.box(
        rx.hstack(
            # Checkbox
            rx.checkbox(
                checked=task["completed"],
                on_change=lambda _: AppState.toggle_complete(task["id"]),
            ),
            # Contenido
            rx.vstack(
                rx.hstack(
                    rx.text(
                        task["title"],
                        font_weight="600",
                        font_size="0.95em",
                        text_decoration=rx.cond(task["completed"], "line-through", "none"),
                        color=rx.cond(AppState.dark_mode, "#f1f5f9", "#1e293b"),
                    ),
                    rx.badge(
                        priority,
                        color_scheme=rx.cond(
                            priority == "Alta", "red",
                            rx.cond(priority == "Media", "yellow", "green")
                        ),
                        variant="soft",
                        font_size="0.7em",
                    ),
                    align="center",
                    spacing="2",
                    wrap="wrap",
                ),
                rx.cond(
                    task["description"] != "",
                    rx.text(
                        task["description"],
                        font_size="0.82em",
                        color=rx.cond(AppState.dark_mode, "#94a3b8", "#64748b"),
                    ),
                ),
                rx.hstack(
                    rx.text(
                        "🕐 " + task["schedule_type"],
                        font_size="0.75em",
                        color=rx.cond(AppState.dark_mode, "#94a3b8", "#64748b"),
                    ),
                    rx.cond(
                        task["task_time"] != "",
                        rx.text(
                            task["task_time"],
                            font_size="0.75em",
                            color=rx.cond(AppState.dark_mode, "#94a3b8", "#64748b"),
                        ),
                    ),
                    rx.cond(
                        task["task_date"] != "",
                        rx.text(
                            "📅 " + task["task_date"],
                            font_size="0.75em",
                            color=rx.cond(AppState.dark_mode, "#94a3b8", "#64748b"),
                        ),
                    ),
                    spacing="3",
                    wrap="wrap",
                ),
                spacing="1",
                align_items="start",
                flex="1",
            ),
            # Botón eliminar
            rx.button(
                "🗑️",
                on_click=lambda: AppState.delete_task(task["id"]),
                variant="ghost",
                color="#ef4444",
                _hover={"background": "#fef2f2"},
                size="1",
            ),
            align="center",
            spacing="3",
            width="100%",
        ),
        padding="1em",
        border_radius="10px",
        border=f"1px solid",
        border_color=rx.cond(AppState.dark_mode, "#334155", "#e2e8f0"),
        background=rx.cond(AppState.dark_mode, "#1e293b", "#ffffff"),
        margin_bottom="0.5em",
        _hover={"box_shadow": "0 2px 8px rgba(0,0,0,0.08)"},
        transition="all 0.15s ease",
    )


def new_task_form() -> rx.Component:
    """Formulario para agregar una nueva tarea."""
    return rx.box(
        rx.vstack(
            rx.heading("Nueva tarea", size="4", color=rx.cond(AppState.dark_mode, "#f1f5f9", "#1e293b")),
            rx.input(
                placeholder="Título de la tarea *",
                value=AppState.new_title,
                on_change=AppState.set_new_title,
                width="100%",
            ),
            rx.text_area(
                placeholder="Descripción (opcional)",
                value=AppState.new_description,
                on_change=AppState.set_new_description,
                width="100%",
                rows="2",
            ),
            rx.hstack(
                rx.vstack(
                    rx.text("Prioridad", font_size="0.82em", color=rx.cond(AppState.dark_mode, "#94a3b8", "#64748b")),
                    rx.select(
                        ["Alta", "Media", "Baja"],
                        value=AppState.new_priority,
                        on_change=AppState.set_new_priority,
                    ),
                    spacing="1",
                    flex="1",
                ),
                rx.vstack(
                    rx.text("Horario", font_size="0.82em", color=rx.cond(AppState.dark_mode, "#94a3b8", "#64748b")),
                    rx.select(
                        ["Todo el día", "Hora específica", "Sin fecha"],
                        value=AppState.new_schedule_type,
                        on_change=AppState.set_new_schedule_type,
                    ),
                    spacing="1",
                    flex="1",
                ),
                spacing="3",
                width="100%",
            ),
            rx.hstack(
                rx.cond(
                    AppState.new_schedule_type != "Sin fecha",
                    rx.vstack(
                        rx.text("Fecha", font_size="0.82em", color=rx.cond(AppState.dark_mode, "#94a3b8", "#64748b")),
                        rx.input(type="date", value=AppState.new_date, on_change=AppState.set_new_date),
                        spacing="1",
                        flex="1",
                    ),
                ),
                rx.cond(
                    AppState.new_schedule_type == "Hora específica",
                    rx.vstack(
                        rx.text("Hora", font_size="0.82em", color=rx.cond(AppState.dark_mode, "#94a3b8", "#64748b")),
                        rx.input(type="time", value=AppState.new_time, on_change=AppState.set_new_time),
                        spacing="1",
                        flex="1",
                    ),
                ),
                spacing="3",
                width="100%",
            ),
            rx.hstack(
                rx.button(
                    "Cancelar",
                    on_click=AppState.toggle_task_form,
                    variant="outline",
                    flex="1",
                ),
                rx.button(
                    "Agregar tarea ✓",
                    on_click=AppState.add_task,
                    background="#6366f1",
                    color="white",
                    flex="1",
                    _hover={"background": "#4f46e5"},
                ),
                spacing="2",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        padding="1.5em",
        background=rx.cond(AppState.dark_mode, "#1e293b", "#ffffff"),
        border_radius="12px",
        border="1px solid",
        border_color=rx.cond(AppState.dark_mode, "#334155", "#e2e8f0"),
        box_shadow="0 4px 24px rgba(0,0,0,0.10)",
        margin_bottom="1.5em",
    )


def index_page() -> rx.Component:
    """Página principal — dashboard de tareas."""
    return rx.cond(
        AppState.is_logged_in,
        # ── Usuario logueado: mostrar dashboard ──
        rx.box(
            # Barra superior (navbar)
            rx.hstack(
                rx.hstack(
                    rx.text("📋", font_size="1.4em"),
                    rx.heading("Task Manager", size="5", color="#6366f1"),
                    spacing="2",
                    align="center",
                ),
                rx.hstack(
                    rx.text(
                        "👤 " + AppState.current_username,
                        font_size="0.9em",
                        color=rx.cond(AppState.dark_mode, "#94a3b8", "#64748b"),
                    ),
                    rx.button(
                        rx.cond(AppState.dark_mode, "☀️ Claro", "🌙 Oscuro"),
                        on_click=AppState.toggle_dark_mode,
                        variant="outline",
                        size="2",
                        font_size="0.8em",
                    ),
                    rx.button(
                        "Salir",
                        on_click=AppState.logout,
                        variant="ghost",
                        color="#ef4444",
                        size="2",
                        font_size="0.8em",
                    ),
                    spacing="3",
                    align="center",
                ),
                justify="between",
                align="center",
                padding="1em 1.5em",
                background=rx.cond(AppState.dark_mode, "#1e293b", "#ffffff"),
                border_bottom="1px solid",
                border_color=rx.cond(AppState.dark_mode, "#334155", "#e2e8f0"),
                position="sticky",
                top="0",
                z_index="100",
                box_shadow="0 1px 8px rgba(0,0,0,0.06)",
            ),

            # Contenido principal
            rx.box(
                rx.vstack(
                    # Estadísticas
                    rx.hstack(
                        rx.box(
                            rx.vstack(
                                rx.text(AppState.pending_count, font_size="2em", font_weight="700", color="#6366f1"),
                                rx.text("Pendientes", font_size="0.8em", color=rx.cond(AppState.dark_mode, "#94a3b8", "#64748b")),
                                align="center", spacing="0",
                            ),
                            padding="1em 1.5em",
                            background=rx.cond(AppState.dark_mode, "#1e293b", "#ffffff"),
                            border_radius="10px",
                            border="1px solid",
                            border_color=rx.cond(AppState.dark_mode, "#334155", "#e2e8f0"),
                            flex="1",
                            text_align="center",
                        ),
                        rx.box(
                            rx.vstack(
                                rx.text(AppState.completed_count, font_size="2em", font_weight="700", color="#22c55e"),
                                rx.text("Completadas", font_size="0.8em", color=rx.cond(AppState.dark_mode, "#94a3b8", "#64748b")),
                                align="center", spacing="0",
                            ),
                            padding="1em 1.5em",
                            background=rx.cond(AppState.dark_mode, "#1e293b", "#ffffff"),
                            border_radius="10px",
                            border="1px solid",
                            border_color=rx.cond(AppState.dark_mode, "#334155", "#e2e8f0"),
                            flex="1",
                            text_align="center",
                        ),
                        spacing="3",
                        width="100%",
                    ),

                    # Botón agregar + filtros
                    rx.hstack(
                        rx.button(
                            "+ Nueva tarea",
                            on_click=AppState.toggle_task_form,
                            background="#6366f1",
                            color="white",
                            _hover={"background": "#4f46e5"},
                        ),
                        rx.hstack(
                            rx.foreach(
                                ["Todas", "Alta", "Media", "Baja"],
                                lambda p: rx.button(
                                    p,
                                    on_click=lambda: AppState.set_filter(p),
                                    variant=rx.cond(AppState.filter_priority == p, "solid", "outline"),
                                    size="2",
                                    font_size="0.8em",
                                    color_scheme=rx.cond(
                                        p == "Alta", "red",
                                        rx.cond(p == "Media", "yellow",
                                            rx.cond(p == "Baja", "green", "indigo"))
                                    ),
                                ),
                            ),
                            spacing="2",
                            wrap="wrap",
                        ),
                        justify="between",
                        align="center",
                        wrap="wrap",
                        gap="2",
                    ),

                    # Formulario nueva tarea (condicional)
                    rx.cond(AppState.show_task_form, new_task_form()),

                    # Lista de tareas
                    rx.cond(
                        AppState.filtered_tasks.length() == 0,
                        rx.center(
                            rx.vstack(
                                rx.text("✅", font_size="3em"),
                                rx.text(
                                    "No hay tareas aquí. ¡Agrega una!",
                                    color=rx.cond(AppState.dark_mode, "#94a3b8", "#64748b"),
                                    font_size="0.95em",
                                ),
                                spacing="2",
                                align="center",
                            ),
                            padding="3em",
                        ),
                        rx.vstack(
                            rx.foreach(AppState.filtered_tasks, task_card),
                            width="100%",
                            spacing="1",
                        ),
                    ),

                    spacing="4",
                    width="100%",
                    max_width="720px",
                    margin="0 auto",
                    padding="1.5em",
                ),
            ),
            background=rx.cond(AppState.dark_mode, "#0f172a", "#f8fafc"),
            min_height="100vh",
        ),
        # ── No logueado: redirigir a login ──
        rx.script("window.location.href='/login'"),
    )


# ─────────────────────────────────────────
#  CONFIGURACIÓN DE LA APP
# ─────────────────────────────────────────

app = rx.App()
app.add_page(login_page, route="/login")
app.add_page(index_page, route="/", on_load=AppState.is_logged_in)