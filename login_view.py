"""Ventana de inicio de sesión: 'Login - Compensándote'."""

import tkinter as tk
from datetime import datetime
from tkinter import messagebox

import config

MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre")


def format_today() -> str:
    """Fecha actual en español, p. ej. '5 de junio de 2026'."""
    now = datetime.now()
    return f"{now.day} de {MESES[now.month - 1]} de {now.year}"


def show_about(parent: tk.Misc) -> None:
    """Cuadro de diálogo con el curso, el estudiante y el grupo colaborativo."""
    messagebox.showinfo(
        "Acerca de",
        f"Curso: {config.COURSE_NAME} \u2014 {config.COURSE_CODE}\n"
        f"Estudiante: {config.STUDENT_NAME}\n"
        f"Grupo colaborativo: {config.COLLABORATIVE_GROUP}\n"
        f"{config.INSTITUTION}\n"
        f"{format_today()}",
        parent=parent,
    )


class LoginWindow(tk.Tk):
    """Solicita la contraseña y marca ``authenticated`` cuando es correcta."""

    def __init__(self) -> None:
        super().__init__()
        self.authenticated = False
        self.title("Login - Compens\u00e1ndote")
        self.configure(bg=config.COLOR_BG)
        self.resizable(False, False)
        self._center(460, 540)

        self._build_menu()
        self._build_widgets()
        self.bind("<Return>", lambda _e: self._on_login())
        self.password_entry.focus_set()

    # ------------------------------------------------------------ construcción
    def _center(self, width: int, height: int) -> None:
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 3
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_menu(self) -> None:
        menubar = tk.Menu(self)
        menubar.add_command(label="Acerca de", command=lambda: show_about(self))
        self.config(menu=menubar)

    def _build_widgets(self) -> None:
        tk.Frame(self, bg=config.COLOR_ACCENT, height=5).pack(fill="x")

        tk.Label(self, text="Compens\u00e1ndote", bg=config.COLOR_BG, fg=config.COLOR_ACCENT,
                 font=("Segoe UI", 26, "bold")).pack(pady=(26, 2))
        tk.Label(self, text="Caja de Compensaci\u00f3n Familiar \u2014 Control de Afiliaciones",
                 bg=config.COLOR_BG, fg="#9fd9ea", font=("Segoe UI", 9)).pack()

        card = tk.Frame(self, bg=config.COLOR_PANEL, highlightthickness=1,
                        highlightbackground=config.COLOR_ACCENT)
        card.pack(fill="x", padx=36, pady=18)
        info = (
            ("Aplicaci\u00f3n:", config.APP_NAME),
            ("Estudiante:", config.STUDENT_NAME),
            ("Curso:", f"{config.COURSE_NAME} \u00b7 {config.COURSE_CODE}"),
            ("Fecha:", format_today()),
        )
        for row, (label, value) in enumerate(info):
            tk.Label(card, text=label, bg=config.COLOR_PANEL, fg="#9fd9ea", anchor="w",
                     font=("Segoe UI", 9)).grid(row=row, column=0, sticky="w", padx=(14, 10), pady=4)
            tk.Label(card, text=value, bg=config.COLOR_PANEL, fg=config.COLOR_TEXT, anchor="w",
                     font=("Segoe UI", 9)).grid(row=row, column=1, sticky="w", pady=4)

        tk.Label(self, text="Contrase\u00f1a", bg=config.COLOR_BG, fg="#9fd9ea", anchor="w",
                 font=("Segoe UI", 10)).pack(fill="x", padx=36)

        self.password_var = tk.StringVar()
        self.password_entry = tk.Entry(
            self, textvariable=self.password_var, show="*", font=("Segoe UI", 13),
            bg=config.COLOR_FIELD, fg=config.COLOR_TEXT, insertbackground=config.COLOR_TEXT,
            relief="flat", highlightthickness=1, highlightbackground=config.COLOR_ACCENT,
            highlightcolor=config.COLOR_ACCENT)
        self.password_entry.pack(fill="x", padx=36, pady=(4, 2), ipady=8)
        tk.Label(self, text="Contrase\u00f1a enmascarada (* * *)", bg=config.COLOR_BG,
                 fg=config.COLOR_MUTED, anchor="w", font=("Segoe UI", 8)).pack(fill="x", padx=36)

        buttons = tk.Frame(self, bg=config.COLOR_BG)
        buttons.pack(fill="x", padx=36, pady=18)
        buttons.columnconfigure((0, 1), weight=1, uniform="b")
        tk.Button(buttons, text="Ingresar \u2192", command=self._on_login, bg=config.COLOR_ACCENT,
                  fg="black", activebackground="#33c9e6", relief="flat", cursor="hand2",
                  font=("Segoe UI", 10, "bold")).grid(row=0, column=0, sticky="ew", padx=(0, 6), ipady=10)
        tk.Button(buttons, text="Salir", command=self._on_exit, bg=config.COLOR_RED,
                  fg="white", activebackground="#f0606b", relief="flat", cursor="hand2",
                  font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="ew", padx=(6, 0), ipady=10)

        tk.Button(self, text="Acerca de", command=lambda: show_about(self), bg=config.COLOR_BG,
                  fg="#9fd9ea", activebackground=config.COLOR_PANEL, relief="flat",
                  cursor="hand2", font=("Segoe UI", 9, "underline")).pack()
        tk.Label(self, text=config.INSTITUTION, bg=config.COLOR_BG, fg=config.COLOR_MUTED,
                 font=("Segoe UI", 8)).pack(side="bottom", pady=10)

    # ---------------------------------------------------------------- eventos
    def _on_login(self) -> None:
        if self.password_var.get() == config.LOGIN_PASSWORD:
            self.authenticated = True
            self.destroy()
        else:
            messagebox.showerror("Login", "Contrase\u00f1a incorrecta. Int\u00e9ntelo de nuevo.", parent=self)
            self.password_var.set("")
            self.password_entry.focus_set()

    def _on_exit(self) -> None:
        self.authenticated = False
        self.destroy()
