"""
Task Manager - Organizador de tareas con Reflex
Sin base de datos - datos en memoria
"""

import reflex as rx


class AppState(rx.State):

    tasks: list[dict] = []
    new_title: str = ""
    new_description: str = ""
    new_priority: str = "Media"
    new_schedule_type: str = "Todo el dia"
    new_time: str = ""
    new_date: str = ""
    show_task_form: bool = False
    dark_mode: bool = False
    filter_priority: str = "Todas"
    next_id: int = 1

    def add_task(self):
        if not self.new_title.strip():
            return
        task = {
            "id": self.next_id,
            "title": self.new_title.strip(),
            "description": self.new_description.strip(),
            "priority": self.new_priority,
            "schedule_type": self.new_schedule_type,
            "task_time": self.new_time,
            "task_date": self.new_date,
            "completed": False,
        }
        self.tasks = self.tasks + [task]
        self.next_id += 1
        self.new_title = ""
        self.new_description = ""
        self.new_priority = "Media"
        self.new_schedule_type = "Todo el dia"
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


def task_card(task: dict) -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.checkbox(
                checked=task["completed"],
                on_change=lambda _: AppState.toggle_complete(task["id"]),
            ),
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
                        task["priority"],
                        color_scheme=rx.cond(
                            task["priority"] == "Alta", "red",
                            rx.cond(task["priority"] == "Media", "yellow", "green")
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
                        task["schedule_type"],
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
                            task["task_date"],
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
            rx.button(
                "X",
                on_click=lambda: AppState.delete_task(task["id"]),
                variant="ghost",
                color="#ef4444",
                size="1",
            ),
            align="center",
            spacing="3",
            width="100%",
        ),
        padding="1em",
        border_radius="10px",
        border="1px solid",
        border_color=rx.cond(AppState.dark_mode, "#334155", "#e2e8f0"),
        background=rx.cond(AppState.dark_mode, "#1e293b", "#ffffff"),
        margin_bottom="0.5em",
    )


def new_task_form() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading(
                "Nueva tarea",
                size="4",
                color=rx.cond(AppState.dark_mode, "#f1f5f9", "#1e293b"),
            ),
            rx.input(
                placeholder="Titulo de la tarea *",
                value=AppState.new_title,
                on_change=AppState.set_new_title,
                width="100%",
            ),
            rx.text_area(
                placeholder="Descripcion (opcional)",
                value=AppState.new_description,
                on_change=AppState.set_new_description,
                width="100%",
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
                        ["Todo el dia", "Hora especifica", "Sin fecha"],
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
                    AppState.new_schedule_type == "Hora especifica",
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
                    "Agregar tarea",
                    on_click=AppState.add_task,
                    background="#6366f1",
                    color="white",
                    flex="1",
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


def index() -> rx.Component:
    return rx.box(
        # Navbar
        rx.hstack(
            rx.hstack(
                rx.text("📋", font_size="1.4em"),
                rx.heading("Task Manager", size="5", color="#6366f1"),
                spacing="2",
                align="center",
            ),
            rx.button(
                rx.cond(AppState.dark_mode, "Modo Claro", "Modo Oscuro"),
                on_click=AppState.toggle_dark_mode,
                variant="outline",
                size="2",
                font_size="0.85em",
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
        ),
        # Contenido
        rx.box(
            rx.vstack(
                # Estadisticas
                rx.hstack(
                    rx.box(
                        rx.vstack(
                            rx.text(
                                AppState.pending_count,
                                font_size="2em",
                                font_weight="700",
                                color="#6366f1",
                            ),
                            rx.text("Pendientes", font_size="0.8em", color=rx.cond(AppState.dark_mode, "#94a3b8", "#64748b")),
                            align="center",
                            spacing="0",
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
                            rx.text(
                                AppState.completed_count,
                                font_size="2em",
                                font_weight="700",
                                color="#22c55e",
                            ),
                            rx.text("Completadas", font_size="0.8em", color=rx.cond(AppState.dark_mode, "#94a3b8", "#64748b")),
                            align="center",
                            spacing="0",
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
                # Botones accion y filtros
                rx.hstack(
                    rx.button(
                        "+ Nueva tarea",
                        on_click=AppState.toggle_task_form,
                        background="#6366f1",
                        color="white",
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
                # Formulario nueva tarea
                rx.cond(AppState.show_task_form, new_task_form()),
                # Lista de tareas
                rx.cond(
                    AppState.filtered_tasks.length() == 0,
                    rx.center(
                        rx.vstack(
                            rx.text("No hay tareas. Agrega una!", color=rx.cond(AppState.dark_mode, "#94a3b8", "#64748b"), font_size="0.95em"),
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
    )


app = rx.App()
app.add_page(index, route="/")