"""
Task Manager - Aplicación de gestión de tareas con Reflex
Práctica 1 - Desarrollo Web
Diseño: Dark minimalist dashboard
"""

import reflex as rx
from datetime import datetime

# ─────────────────────────────────────────
#  PALETA DE COLORES
# ─────────────────────────────────────────
BG_DARK      = "#0d1117"
BG_CARD      = "#161b27"
BG_CARD2     = "#1c2333"
BORDER       = "#21293a"
ACCENT       = "#7c83fd"
ACCENT_SOFT  = "#2a2d5e"
TEXT_PRI     = "#e8edf5"
TEXT_SEC     = "#7b8597"
TEXT_MUTED   = "#4a5568"
RED          = "#f87171"
AMBER        = "#fbbf24"
GREEN        = "#34d399"
SUCCESS_BG   = "#0d2b1f"
DANGER_BG    = "#2b0d0d"

BG_LIGHT     = "#f4f6fb"
BG_CARD_L    = "#ffffff"
BG_CARD2_L   = "#f0f4ff"
BORDER_L     = "#dde3f0"
TEXT_PRI_L   = "#1a1f2e"
TEXT_SEC_L   = "#5a6480"
TEXT_MUTED_L = "#a0aec0"


# ─────────────────────────────────────────
#  ESTADO
# ─────────────────────────────────────────

class AppState(rx.State):

    tasks: list[dict] = []

    new_title: str = ""
    new_description: str = ""
    new_priority: str = "Media"
    new_schedule_type: str = "Todo el día"
    new_time: str = ""
    new_date: str = ""
    show_task_form: bool = False

    dark_mode: bool = True
    filter_priority: str = "Todas"

    def add_task(self):
        if not self.new_title.strip():
            return
        self.tasks = self.tasks + [
            {
                "id": len(self.tasks),
                "title": self.new_title.strip(),
                "description": self.new_description.strip(),
                "priority": self.new_priority,
                "schedule_type": self.new_schedule_type,
                "task_time": self.new_time if self.new_schedule_type == "Hora específica" else "",
                "task_date": self.new_date,
                "completed": False,
                "created_at": datetime.now().strftime("%d/%m %H:%M"),
            }
        ]
        self.new_title = ""
        self.new_description = ""
        self.new_priority = "Media"
        self.new_schedule_type = "Todo el día"
        self.new_time = ""
        self.new_date = ""
        self.show_task_form = False

    def toggle_complete(self, task_id: int):
        self.tasks = [
            {**t, "completed": not t["completed"]} if t["id"] == task_id else t
            for t in self.tasks
        ]

    def delete_task(self, task_id: int):
        self.tasks = [t for t in self.tasks if t["id"] != task_id]

    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode

    def toggle_task_form(self):
        self.show_task_form = not self.show_task_form

    def set_filter(self, priority: str):
        self.filter_priority = priority

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

    @rx.var
    def filtered_tasks(self) -> list[dict]:
        if self.filter_priority == "Todas":
            return self.tasks
        return [t for t in self.tasks if t["priority"] == self.filter_priority]

    @rx.var
    def pending_count(self) -> int:
        return sum(1 for t in self.tasks if not t["completed"])

    @rx.var
    def completed_count(self) -> int:
        return sum(1 for t in self.tasks if t["completed"])

    @rx.var
    def high_count(self) -> int:
        return sum(1 for t in self.tasks if t["priority"] == "Alta" and not t["completed"])


# ─────────────────────────────────────────
#  HELPERS DE COLOR SEGÚN MODO
# ─────────────────────────────────────────

def bg():
    return rx.cond(AppState.dark_mode, BG_DARK, BG_LIGHT)

def card_bg():
    return rx.cond(AppState.dark_mode, BG_CARD, BG_CARD_L)

def card2_bg():
    return rx.cond(AppState.dark_mode, BG_CARD2, BG_CARD2_L)

def border_color():
    return rx.cond(AppState.dark_mode, BORDER, BORDER_L)

def text_pri():
    return rx.cond(AppState.dark_mode, TEXT_PRI, TEXT_PRI_L)

def text_sec():
    return rx.cond(AppState.dark_mode, TEXT_SEC, TEXT_SEC_L)

def priority_color(priority: str):
    return rx.cond(
        priority == "Alta", RED,
        rx.cond(priority == "Media", AMBER, GREEN)
    )

def priority_bg(priority: str):
    return rx.cond(
        priority == "Alta", "#2b1515",
        rx.cond(priority == "Media", "#2b220d", "#0d2b1f")
    )


# ─────────────────────────────────────────
#  COMPONENTES
# ─────────────────────────────────────────

def stat_card(icon: str, value, label: str, accent_color: str) -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text(icon, font_size="1.3em"),
                rx.text(
                    value,
                    font_size="2em",
                    font_weight="700",
                    color=accent_color,
                    line_height="1",
                ),
                align="center",
                spacing="2",
            ),
            rx.text(
                label,
                font_size="0.75em",
                color=text_sec(),
                letter_spacing="0.05em",
                text_transform="uppercase",
                font_weight="500",
            ),
            spacing="2",
            align_items="start",
        ),
        padding="1.2em 1.5em",
        background=card_bg(),
        border=f"1px solid",
        border_color=border_color(),
        border_radius="14px",
        flex="1",
        min_width="120px",
        transition="box-shadow 0.2s",
    )


def priority_dot(priority: str) -> rx.Component:
    return rx.box(
        width="8px",
        height="8px",
        border_radius="50%",
        background=priority_color(priority),
        flex_shrink="0",
    )


def task_card(task: dict) -> rx.Component:
    return rx.box(
        rx.vstack(
            # Header: checkbox + priority dot + delete
            rx.hstack(
                rx.checkbox(
                    checked=task["completed"],
                    on_change=lambda _: AppState.toggle_complete(task["id"]),
                    color_scheme="indigo",
                ),
                priority_dot(task["priority"]),
                rx.spacer(),
                rx.button(
                    "✕",
                    on_click=lambda: AppState.delete_task(task["id"]),
                    variant="ghost",
                    size="1",
                    color=TEXT_MUTED,
                    _hover={"color": RED, "background": "transparent"},
                    padding="0",
                    height="auto",
                    min_width="0",
                    font_size="0.8em",
                ),
                width="100%",
                align="center",
            ),
            # Title
            rx.text(
                task["title"],
                font_weight="600",
                font_size="0.88em",
                color=rx.cond(
                    task["completed"],
                    TEXT_MUTED,
                    text_pri(),
                ),
                text_decoration=rx.cond(task["completed"], "line-through", "none"),
                line_height="1.35",
                no_of_lines=2,
                width="100%",
            ),
            # Description (if any)
            rx.cond(
                task["description"] != "",
                rx.text(
                    task["description"],
                    font_size="0.75em",
                    color=text_sec(),
                    line_height="1.4",
                    no_of_lines=2,
                ),
            ),
            rx.spacer(),
            # Footer: schedule info
            rx.hstack(
                rx.box(
                    rx.text(
                        task["priority"],
                        font_size="0.65em",
                        color=priority_color(task["priority"]),
                        font_weight="600",
                        letter_spacing="0.04em",
                    ),
                    padding="2px 8px",
                    border_radius="20px",
                    background=priority_bg(task["priority"]),
                ),
                rx.cond(
                    task["task_date"] != "",
                    rx.text(
                        task["task_date"],
                        font_size="0.68em",
                        color=TEXT_MUTED,
                    ),
                ),
                rx.cond(
                    task["task_time"] != "",
                    rx.text(
                        task["task_time"],
                        font_size="0.68em",
                        color=TEXT_MUTED,
                    ),
                ),
                spacing="2",
                wrap="wrap",
                align="center",
                width="100%",
            ),
            spacing="2",
            height="100%",
            align_items="start",
        ),
        padding="1em",
        background=rx.cond(
            task["completed"],
            rx.cond(AppState.dark_mode, "#131820", BG_CARD2_L),
            card_bg(),
        ),
        border=f"1px solid",
        border_color=rx.cond(
            task["completed"],
            rx.cond(AppState.dark_mode, "#1a2030", BORDER_L),
            border_color(),
        ),
        border_radius="12px",
        transition="all 0.18s ease",
        min_height="140px",
        display="flex",
        flex_direction="column",
        opacity=rx.cond(task["completed"], "0.6", "1"),
    )


def new_task_form() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(
                rx.text("⊕", font_size="1.1em", color=ACCENT),
                rx.text(
                    "Nueva tarea",
                    font_weight="600",
                    font_size="0.95em",
                    color=text_pri(),
                ),
                spacing="2",
                align="center",
            ),
            rx.divider(border_color=border_color()),
            # Row 1: title + description
            rx.hstack(
                rx.vstack(
                    rx.text("Título *", font_size="0.72em", color=text_sec(), font_weight="500"),
                    rx.input(
                        placeholder="¿Qué necesitas hacer?",
                        value=AppState.new_title,
                        on_change=AppState.set_new_title,
                        background=card2_bg(),
                        border_color=border_color(),
                        color=text_pri(),
                        _placeholder={"color": TEXT_MUTED},
                        width="100%",
                        border_radius="8px",
                    ),
                    spacing="1",
                    flex="1",
                ),
                rx.vstack(
                    rx.text("Descripción", font_size="0.72em", color=text_sec(), font_weight="500"),
                    rx.input(
                        placeholder="Detalles opcionales...",
                        value=AppState.new_description,
                        on_change=AppState.set_new_description,
                        background=card2_bg(),
                        border_color=border_color(),
                        color=text_pri(),
                        _placeholder={"color": TEXT_MUTED},
                        width="100%",
                        border_radius="8px",
                    ),
                    spacing="1",
                    flex="1",
                ),
                spacing="3",
                width="100%",
            ),
            # Row 2: priority + schedule + date + time
            rx.hstack(
                rx.vstack(
                    rx.text("Prioridad", font_size="0.72em", color=text_sec(), font_weight="500"),
                    rx.select(
                        ["Alta", "Media", "Baja"],
                        value=AppState.new_priority,
                        on_change=AppState.set_new_priority,
                        background=card2_bg(),
                        border_color=border_color(),
                        color=text_pri(),
                    ),
                    spacing="1",
                    flex="1",
                ),
                rx.vstack(
                    rx.text("Horario", font_size="0.72em", color=text_sec(), font_weight="500"),
                    rx.select(
                        ["Todo el día", "Hora específica", "Sin fecha"],
                        value=AppState.new_schedule_type,
                        on_change=AppState.set_new_schedule_type,
                        background=card2_bg(),
                        border_color=border_color(),
                        color=text_pri(),
                    ),
                    spacing="1",
                    flex="1",
                ),
                rx.cond(
                    AppState.new_schedule_type != "Sin fecha",
                    rx.vstack(
                        rx.text("Fecha", font_size="0.72em", color=text_sec(), font_weight="500"),
                        rx.input(
                            type="date",
                            value=AppState.new_date,
                            on_change=AppState.set_new_date,
                            background=card2_bg(),
                            border_color=border_color(),
                            color=text_pri(),
                        ),
                        spacing="1",
                        flex="1",
                    ),
                ),
                rx.cond(
                    AppState.new_schedule_type == "Hora específica",
                    rx.vstack(
                        rx.text("Hora", font_size="0.72em", color=text_sec(), font_weight="500"),
                        rx.input(
                            type="time",
                            value=AppState.new_time,
                            on_change=AppState.set_new_time,
                            background=card2_bg(),
                            border_color=border_color(),
                            color=text_pri(),
                        ),
                        spacing="1",
                        flex="1",
                    ),
                ),
                spacing="3",
                width="100%",
                wrap="wrap",
            ),
            # Buttons
            rx.hstack(
                rx.button(
                    "Cancelar",
                    on_click=AppState.toggle_task_form,
                    variant="outline",
                    border_color=border_color(),
                    color=text_sec(),
                    size="2",
                    border_radius="8px",
                ),
                rx.button(
                    "+ Agregar tarea",
                    on_click=AppState.add_task,
                    background=ACCENT,
                    color="white",
                    size="2",
                    border_radius="8px",
                    font_weight="600",
                    _hover={"background": "#6368e0"},
                ),
                spacing="3",
                justify="end",
                width="100%",
            ),
            spacing="4",
            width="100%",
        ),
        padding="1.5em",
        background=card_bg(),
        border=f"1px solid",
        border_color=ACCENT_SOFT,
        border_radius="14px",
        margin_bottom="1.5em",
    )


def filter_btn(label: str) -> rx.Component:
    is_active = AppState.filter_priority == label
    return rx.button(
        label,
        on_click=lambda: AppState.set_filter(label),
        size="2",
        font_size="0.78em",
        font_weight="500",
        border_radius="20px",
        padding="0.3em 1em",
        background=rx.cond(is_active, ACCENT, "transparent"),
        color=rx.cond(is_active, "white", text_sec()),
        border=rx.cond(is_active, f"1px solid {ACCENT}", f"1px solid"),
        border_color=rx.cond(is_active, ACCENT, border_color()),
        transition="all 0.15s ease",
        _hover={
            "background": rx.cond(is_active, "#6368e0", rx.cond(AppState.dark_mode, "#1c2333", "#eef1fb")),
            "color": rx.cond(is_active, "white", text_pri()),
        },
        cursor="pointer",
    )


def index_page() -> rx.Component:
    return rx.box(
        # ── NAVBAR ──
        rx.hstack(
            rx.hstack(
                rx.text("◈", font_size="1.3em", color=ACCENT),
                rx.text(
                    "TaskFlow",
                    font_size="1.1em",
                    font_weight="700",
                    color=text_pri(),
                    letter_spacing="-0.02em",
                ),
                spacing="2",
                align="center",
            ),
            rx.hstack(
                rx.button(
                    rx.cond(AppState.dark_mode, "☀", "🌙"),
                    on_click=AppState.toggle_dark_mode,
                    variant="ghost",
                    size="2",
                    color=text_sec(),
                    border_radius="8px",
                    _hover={"background": card2_bg(), "color": text_pri()},
                ),
                spacing="2",
                align="center",
            ),
            justify="between",
            align="center",
            padding="0.9em 2em",
            background=card_bg(),
            border_bottom="1px solid",
            border_color=border_color(),
            position="sticky",
            top="0",
            z_index="100",
            width="100%",
        ),

        # ── CONTENIDO ──
        rx.box(
            rx.vstack(

                # ── STATS ──
                rx.hstack(
                    stat_card("📋", AppState.pending_count, "Pendientes", ACCENT),
                    stat_card("✓", AppState.completed_count, "Completadas", GREEN),
                    stat_card("⚠", AppState.high_count, "Alta prioridad", RED),
                    spacing="3",
                    width="100%",
                ),

                # ── TOOLBAR ──
                rx.hstack(
                    # Filtros
                    rx.hstack(
                        filter_btn("Todas"),
                        filter_btn("Alta"),
                        filter_btn("Media"),
                        filter_btn("Baja"),
                        spacing="2",
                        wrap="wrap",
                    ),
                    rx.spacer(),
                    # Botón nueva tarea
                    rx.button(
                        "+ Nueva tarea",
                        on_click=AppState.toggle_task_form,
                        background=ACCENT,
                        color="white",
                        size="2",
                        font_weight="600",
                        border_radius="10px",
                        font_size="0.85em",
                        padding="0.55em 1.2em",
                        _hover={"background": "#6368e0"},
                        transition="background 0.15s ease",
                    ),
                    align="center",
                    width="100%",
                    wrap="wrap",
                    gap="2",
                ),

                # ── FORMULARIO ──
                rx.cond(AppState.show_task_form, new_task_form()),

                # ── GRID DE TAREAS ──
                rx.cond(
                    AppState.filtered_tasks.length() == 0,
                    rx.center(
                        rx.vstack(
                            rx.text("◈", font_size="2.5em", color=TEXT_MUTED),
                            rx.text(
                                "Sin tareas aquí",
                                font_size="0.95em",
                                font_weight="600",
                                color=TEXT_MUTED,
                            ),
                            rx.text(
                                "Agrega una nueva tarea para empezar",
                                font_size="0.8em",
                                color=TEXT_MUTED,
                            ),
                            spacing="2",
                            align="center",
                        ),
                        padding="4em",
                        width="100%",
                    ),
                    rx.grid(
                        rx.foreach(AppState.filtered_tasks, task_card),
                        columns="4",
                        spacing="3",
                        width="100%",
                    ),
                ),

                spacing="4",
                width="100%",
                max_width="1280px",
                margin="0 auto",
                padding="2em",
            ),
        ),

        background=bg(),
        min_height="100vh",
        font_family="'Segoe UI', system-ui, -apple-system, sans-serif",
        transition="background 0.2s ease",
    )


# ─────────────────────────────────────────
#  APP
# ─────────────────────────────────────────

app = rx.App(
    style={
        "font_family": "'Segoe UI', system-ui, -apple-system, sans-serif",
        "box_sizing": "border-box",
    }
)
app.add_page(index_page, route="/")