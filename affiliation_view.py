"""Data entry window: 'Caja Compensándote – Control de Afiliados'."""

import tkinter as tk
from datetime import date
from tkinter import messagebox, simpledialog, ttk

import config
from models import (EMPLOYMENT_TYPES, ID_TYPES, SERVICES, STRUCTURES, AffiliateRepository,
                    EstructuraDatosAfiliado, MIN_INCOME, calculate_affiliation_fee,
                    format_money)

TREE_COLUMNS = (
    ("id_type", "ID Type", 64),
    ("id_number", "ID Number", 84),
    ("full_name", "Full Name", 135),
    ("income", "Income ($)", 90),
    ("service", "Service", 160),
    ("employment", "Employment", 105),
    ("fee", "Tariff ($)", 80),
    ("date", "Date", 100),
)


class AffiliationWindow(tk.Tk):
    """Main form: register, delete, report and clear affiliates."""

    def __init__(self) -> None:
        super().__init__()
        self.title("Caja Compens\u00e1ndote \u2013 Control de Afiliados")
        self.configure(bg=config.COLOR_BG)
        self.geometry("1250x780")
        self.minsize(1150, 740)

        self.repository = AffiliateRepository()
        self._create_variables()
        self._configure_styles()
        self._build_header()
        self._build_body()
        self._build_status_bar()

        self._update_fee()
        self._refresh_tree()
        self.protocol("WM_DELETE_WINDOW", self._on_exit)

    # -------------------------------------------------------------- variables
    def _create_variables(self) -> None:
        today = date.today()
        self.id_type_var = tk.StringVar(value=ID_TYPES[0])
        self.id_number_var = tk.StringVar()
        self.full_name_var = tk.StringVar()
        self.income_var = tk.StringVar()
        self.employment_var = tk.StringVar(value=EMPLOYMENT_TYPES[0])
        self.service_var = tk.StringVar(value=SERVICES[0])
        self.fee_var = tk.StringVar()
        self.day_var = tk.StringVar(value=str(today.day))
        self.month_var = tk.StringVar(value=str(today.month))
        self.year_var = tk.StringVar(value=str(today.year))
        self.structure_var = tk.StringVar(value=STRUCTURES[0])
        self.report_var = tk.StringVar()
        self.status_var = tk.StringVar(value="Ready \u2014 fill in the form and click Register.")

        # The fee is recalculated by events whenever one of its inputs changes.
        for var in (self.income_var, self.employment_var, self.service_var):
            var.trace_add("write", self._update_fee)

    # ----------------------------------------------------------------- styles
    def _configure_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", background=config.COLOR_BG)
        style.configure("TLabel", background=config.COLOR_PANEL, foreground=config.COLOR_TEXT,
                        font=("Segoe UI", 9))
        style.configure("Section.TLabel", foreground=config.COLOR_ACCENT,
                        font=("Segoe UI", 10, "bold"))
        style.configure("TEntry", fieldbackground=config.COLOR_FIELD, foreground=config.COLOR_TEXT,
                        insertcolor=config.COLOR_TEXT, bordercolor=config.COLOR_ACCENT)
        style.configure("Fee.TEntry", fieldbackground="#e8f1f8", foreground="#0f1f33")
        style.map("Fee.TEntry", fieldbackground=[("readonly", "#e8f1f8")],
                  foreground=[("readonly", "#0f1f33")])
        style.configure("Report.TEntry", fieldbackground="#e8f1f8", foreground="#0f1f33")
        style.map("Report.TEntry", fieldbackground=[("readonly", "#e8f1f8")],
                  foreground=[("readonly", "#0f1f33")])
        style.configure("TCombobox", fieldbackground=config.COLOR_FIELD, background=config.COLOR_FIELD,
                        foreground=config.COLOR_TEXT, arrowcolor=config.COLOR_TEXT)
        style.map("TCombobox", fieldbackground=[("readonly", config.COLOR_FIELD)],
                  foreground=[("readonly", config.COLOR_TEXT)])
        style.configure("TSpinbox", fieldbackground=config.COLOR_FIELD, foreground=config.COLOR_TEXT,
                        arrowcolor=config.COLOR_TEXT)
        style.configure("TRadiobutton", background=config.COLOR_PANEL, foreground=config.COLOR_TEXT)
        style.map("TRadiobutton", background=[("active", config.COLOR_PANEL)])
        style.configure("Treeview", background=config.COLOR_BG, fieldbackground=config.COLOR_BG,
                        foreground=config.COLOR_TEXT, rowheight=24, bordercolor=config.COLOR_PANEL)
        style.map("Treeview", background=[("selected", config.COLOR_ACCENT)],
                  foreground=[("selected", "black")])
        style.configure("Treeview.Heading", background=config.COLOR_FIELD, foreground=config.COLOR_ACCENT,
                        font=("Segoe UI", 9, "bold"))

    # ------------------------------------------------------------------ layout
    def _build_header(self) -> None:
        header = tk.Frame(self, bg=config.COLOR_FIELD)
        header.pack(fill="x")
        tk.Label(header, text="Compens\u00e1ndote \u2014 Affiliation Control", bg=config.COLOR_FIELD,
                 fg=config.COLOR_ACCENT, font=("Segoe UI", 14, "bold")).pack(side="left", padx=14, pady=8)
        tk.Label(header, text=f"{config.STUDENT_NAME}  |  {config.COURSE_NAME} {config.COURSE_CODE}",
                 bg=config.COLOR_FIELD, fg="#9fd9ea", font=("Segoe UI", 9)).pack(side="right", padx=14)

    def _build_body(self) -> None:
        body = tk.Frame(self, bg=config.COLOR_BG)
        body.pack(fill="both", expand=True)
        body.columnconfigure(1, weight=1)
        body.rowconfigure(0, weight=1)
        self._build_form(body)
        self._build_table_area(body)

    def _section(self, parent: tk.Misc, title: str) -> ttk.Label:
        label = ttk.Label(parent, text=title, style="Section.TLabel")
        label.pack(fill="x", pady=(10, 2))
        return label

    def _field(self, parent: tk.Misc, text: str) -> None:
        ttk.Label(parent, text=text).pack(fill="x", pady=(4, 0))

    def _build_form(self, body: tk.Misc) -> None:
        form = tk.Frame(body, bg=config.COLOR_PANEL, width=330)
        form.grid(row=0, column=0, sticky="ns", padx=(8, 4), pady=8)
        form.pack_propagate(False)
        inner = tk.Frame(form, bg=config.COLOR_PANEL)
        inner.pack(fill="both", expand=True, padx=12)

        digits_only = (self.register(lambda p: p == "" or (p.isascii() and p.isdigit())), "%P")
        letters_only = (self.register(lambda p: all(c.isalpha() or c == " " for c in p)), "%P")

        # Identification
        self._section(inner, "Identification")
        self._field(inner, "ID Type")
        ttk.Combobox(inner, textvariable=self.id_type_var, values=ID_TYPES,
                     state="readonly").pack(fill="x")
        self._field(inner, "ID Number (digits only)")
        self.id_number_entry = ttk.Entry(inner, textvariable=self.id_number_var,
                                         validate="key", validatecommand=digits_only)
        self.id_number_entry.pack(fill="x")
        self._field(inner, "Full Name (letters only)")
        ttk.Entry(inner, textvariable=self.full_name_var, validate="key",
                  validatecommand=letters_only).pack(fill="x")

        # Economic data
        self._section(inner, "Economic Data")
        self._field(inner, "Current Income ($, digits only)")
        ttk.Entry(inner, textvariable=self.income_var, validate="key",
                  validatecommand=digits_only).pack(fill="x")
        self._field(inner, "Employment Type")
        radios = tk.Frame(inner, bg=config.COLOR_PANEL)
        radios.pack(fill="x")
        for option in EMPLOYMENT_TYPES:
            ttk.Radiobutton(radios, text=option, value=option,
                            variable=self.employment_var).pack(side="left", padx=(0, 16))
        self._field(inner, "Desired Service")
        ttk.Combobox(inner, textvariable=self.service_var, values=SERVICES,
                     state="readonly").pack(fill="x")
        self._field(inner, "Affiliation Tariff ($) \u2014 read only")
        ttk.Entry(inner, textvariable=self.fee_var, state="readonly",
                  style="Fee.TEntry").pack(fill="x")

        # Affiliation date (dd/mm/yyyy)
        self._section(inner, "Affiliation Date (dd/mm/yyyy)")
        date_row = tk.Frame(inner, bg=config.COLOR_PANEL)
        date_row.pack(fill="x")
        for caption, var, low, high, width in (("Day", self.day_var, 1, 31, 4),
                                               ("Month", self.month_var, 1, 12, 4),
                                               ("Year", self.year_var, 1900, 2100, 6)):
            cell = tk.Frame(date_row, bg=config.COLOR_PANEL)
            cell.pack(side="left", padx=(0, 10))
            ttk.Label(cell, text=caption).pack(anchor="w")
            ttk.Spinbox(cell, from_=low, to=high, textvariable=var, width=width,
                        wrap=True).pack()

        # Data structure selector + report
        self._section(inner, "Data Structure")
        structure_box = ttk.Combobox(inner, textvariable=self.structure_var, values=STRUCTURES,
                                     state="readonly")
        structure_box.pack(fill="x")
        structure_box.bind("<<ComboboxSelected>>", self._on_structure_changed)
        self._field(inner, "Report \u2014 read only")
        ttk.Entry(inner, textvariable=self.report_var, state="readonly",
                  style="Report.TEntry").pack(fill="x")

    def _build_table_area(self, body: tk.Misc) -> None:
        area = tk.Frame(body, bg=config.COLOR_BG)
        area.grid(row=0, column=1, sticky="nsew", padx=(4, 8), pady=8)
        area.columnconfigure(0, weight=1)
        area.rowconfigure(1, weight=1)

        self.table_title = tk.Label(area, text="", bg=config.COLOR_BG, fg=config.COLOR_ACCENT,
                                    anchor="w", font=("Segoe UI", 10, "bold"))
        self.table_title.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 4))

        self.tree = ttk.Treeview(area, columns=[c[0] for c in TREE_COLUMNS], show="headings",
                                 selectmode="browse")
        for key, heading, width in TREE_COLUMNS:
            self.tree.heading(key, text=heading)
            self.tree.column(key, width=width, anchor="w", stretch=(key == "service"))
        y_scroll = ttk.Scrollbar(area, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(area, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)
        self.tree.grid(row=1, column=0, sticky="nsew")
        y_scroll.grid(row=1, column=1, sticky="ns")
        x_scroll.grid(row=2, column=0, sticky="ew")
        self.tree.tag_configure("first", foreground=config.COLOR_GREEN)

        bar = tk.Frame(area, bg=config.COLOR_BG)
        bar.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        bar.columnconfigure(tuple(range(5)), weight=1, uniform="btn")
        buttons = (
            ("Register", self._on_register, config.COLOR_ACCENT, "black"),
            ("Delete", self._on_delete, config.COLOR_RED, "white"),
            ("Report", self._on_report, config.COLOR_GREEN, "black"),
            ("Clear", self._on_clear, config.COLOR_ORANGE, "black"),
            ("Exit", self._on_exit, config.COLOR_FIELD, "white"),
        )
        for column, (text, command, bg, fg) in enumerate(buttons):
            tk.Button(bar, text=text, command=command, bg=bg, fg=fg, relief="flat",
                      cursor="hand2", font=("Segoe UI", 10, "bold")).grid(
                row=0, column=column, sticky="ew", padx=3, ipady=9)

    def _build_status_bar(self) -> None:
        tk.Label(self, textvariable=self.status_var, bg=config.COLOR_FIELD, fg="#9fd9ea",
                 anchor="w", font=("Consolas", 9), padx=10).pack(fill="x", side="bottom")

    # ----------------------------------------------------------------- helpers
    def _set_status(self, message: str) -> None:
        self.status_var.set(message)

    def _update_fee(self, *_args) -> None:
        """Recalculate the (read-only) affiliation tariff."""
        income_text = self.income_var.get().strip()
        if not income_text:
            self.fee_var.set("")
            return
        try:
            fee = calculate_affiliation_fee(int(income_text), self.employment_var.get(),
                                            self.service_var.get())
        except ValueError:
            # Income below the first bracket of the tables: no fee can be calculated.
            self.fee_var.set("")
            self._set_status(f"Income must be at least {format_money(MIN_INCOME)} "
                             "(lower values are not covered by the fee tables).")
            return
        self.fee_var.set(format_money(fee))

    def _refresh_tree(self) -> None:
        """Redraw the Treeview with the contents of the selected structure."""
        structure = self.structure_var.get()
        self.tree.delete(*self.tree.get_children())
        for position, affiliate in enumerate(self.repository.items(structure)):
            self.tree.insert("", "end", values=affiliate.as_row(),
                             tags=("first",) if position == 0 else ())
        hints = {"Stack": " (top first)", "Queue": " (front first)", "List": ""}
        self.table_title.config(
            text=f"{structure} \u2014 Registered Affiliates{hints[structure]}  "
                 f"[{self.repository.count(structure)}]")

    def _read_date(self):
        try:
            return date(int(self.year_var.get()), int(self.month_var.get()), int(self.day_var.get()))
        except ValueError:
            return None

    # ---------------------------------------------------------------- handlers
    def _on_structure_changed(self, _event=None) -> None:
        self.report_var.set("")
        self._refresh_tree()
        self._set_status(f"Viewing structure: {self.structure_var.get()}")

    def _on_register(self) -> None:
        id_number = self.id_number_var.get().strip()
        full_name = " ".join(self.full_name_var.get().split())
        income_text = self.income_var.get().strip()

        missing = []
        if not self.id_type_var.get():
            missing.append("ID Type")
        if not id_number:
            missing.append("ID Number")
        if not full_name:
            missing.append("Full Name")
        if not income_text:
            missing.append("Current Income")
        if not self.service_var.get():
            missing.append("Desired Service")
        if missing:
            messagebox.showwarning("Missing data", "Please complete: " + ", ".join(missing) + ".",
                                   parent=self)
            return

        affiliation_date = self._read_date()
        if affiliation_date is None:
            messagebox.showwarning("Invalid date", "The affiliation date is not a valid date.",
                                   parent=self)
            return

        income = int(income_text)
        if income < MIN_INCOME:
            messagebox.showwarning(
                "Income not covered",
                f"The current income must be at least {format_money(MIN_INCOME)}.\n"
                "Lower incomes are not covered by the affiliation fee tables.", parent=self)
            return
        fee = calculate_affiliation_fee(income, self.employment_var.get(), self.service_var.get())
        affiliate = EstructuraDatosAfiliado(
            id_type=self.id_type_var.get(), id_number=id_number, full_name=full_name,
            current_income=income, desired_service=self.service_var.get(),
            employment_type=self.employment_var.get(), affiliation_fee=fee,
            affiliation_date=affiliation_date)

        structure = self.structure_var.get()
        self.repository.register(structure, affiliate)
        self._refresh_tree()
        actions = {"Stack": "pushed onto the stack", "Queue": "enqueued", "List": "added to the list"}
        self._set_status(f"{full_name} {actions[structure]}.")

    def _on_delete(self) -> None:
        structure = self.structure_var.get()

        if structure == "List":
            id_number = simpledialog.askstring(
                "Delete from List", "Enter the ID number of the affiliate to delete:", parent=self)
            if id_number is None:
                return
            id_number = id_number.strip()
            if not id_number.isascii() or not id_number.isdigit():
                messagebox.showwarning("Invalid ID", "The ID number must contain digits only.",
                                       parent=self)
                return
            target = self.repository.find_in_list(id_number)
            if target is None:
                messagebox.showinfo("Not found", f"No affiliate with ID {id_number} in the list.",
                                    parent=self)
                return
        else:
            target = self.repository.peek(structure)
            if target is None:
                messagebox.showinfo("Empty", f"The {structure.lower()} is empty.", parent=self)
                return

        verb = {"Stack": "pop (remove the top)", "Queue": "dequeue (remove the front)",
                "List": "remove from the list"}[structure]
        if not messagebox.askyesno(
                "Confirm deletion",
                f"Do you want to {verb}?\n\n{target.full_name} \u2014 {target.id_type} {target.id_number}",
                parent=self):
            return

        if structure == "List":
            removed = self.repository.remove_from_list(target.id_number)
        else:
            removed = self.repository.remove(structure)
        self._refresh_tree()
        self.report_var.set("")
        self._set_status(f"Removed {removed.full_name} from the {structure.lower()}.")

    def _on_report(self) -> None:
        structure = self.structure_var.get()
        self.report_var.set(self.repository.report(structure))
        self._set_status(f"Report generated for the {structure.lower()}.")

    def _on_clear(self) -> None:
        """Reset the form fields; the records in the structures are untouched."""
        today = date.today()
        self.id_type_var.set(ID_TYPES[0])
        self.id_number_var.set("")
        self.full_name_var.set("")
        self.income_var.set("")
        self.employment_var.set(EMPLOYMENT_TYPES[0])
        self.service_var.set(SERVICES[0])
        self.day_var.set(str(today.day))
        self.month_var.set(str(today.month))
        self.year_var.set(str(today.year))
        self.report_var.set("")
        self._update_fee()
        self.id_number_entry.focus_set()
        self._set_status("Form cleared. Stored records were not affected.")

    def _on_exit(self) -> None:
        self.destroy()
