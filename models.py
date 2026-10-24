"""Modelo de datos, reglas de tarifa y estructuras de datos lineales (pila, cola y lista).

Todos los datos se guardan en memoria principal: no se usan bases de datos ni archivos.
  - Pila  : ``list`` de Python        (apilar = append, desapilar = pop)
  - Cola  : ``collections.deque``     (encolar = append, desencolar = popleft)
  - Lista : ``list`` de Python        (agregar al final, eliminar por identificación)
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import date
from typing import Optional

ID_TYPES = ("CC", "CE", "NUIP", "PAS")
SERVICES = (
    "Subsidio de desempleo",
    "Ingreso a parque",
    "Curso de formación",
    "Paquete de viaje",
    "Medicina preventiva",
)
EMPLOYMENT_TYPES = ("Empleado", "Independiente")
STRUCTURES = ("Pila", "Cola", "Lista")

# Límites superiores (inclusivos) de los rangos de ingresos. Por encima del último: "> $5.000.000".
INCOME_BRACKET_LIMITS = (2_000_000, 3_000_000, 4_000_000, 5_000_000)
EMPLOYEE_FEES = (45_000, 60_000, 75_000, 90_000, 150_000)
INDEPENDENT_FEES = (10_000, 20_000, 30_000, 40_000, 80_000)

# Recargo fijo por servicio. Medicina preventiva es un porcentaje de los ingresos.
SERVICE_SURCHARGE = {
    "Subsidio de desempleo": 0,
    "Ingreso a parque": 2_500,
    "Curso de formación": 7_500,
    "Paquete de viaje": 10_000,
}
PREVENTIVE_MEDICINE_RATE = 0.10


def calculate_affiliation_fee(income: int, employment_type: str, service: str) -> float:
    """Devuelve la tarifa de afiliación según ingresos, modalidad de empleo y servicio."""
    fees = EMPLOYEE_FEES if employment_type == "Empleado" else INDEPENDENT_FEES

    bracket = len(INCOME_BRACKET_LIMITS)  # por defecto: el rango "> 5.000.000"
    for index, limit in enumerate(INCOME_BRACKET_LIMITS):
        if income <= limit:
            bracket = index
            break
    base_fee = fees[bracket]

    if service == "Medicina preventiva":
        surcharge = income * PREVENTIVE_MEDICINE_RATE
    else:
        surcharge = SERVICE_SURCHARGE.get(service, 0)
    return round(base_fee + surcharge, 2)


def format_money(value: float) -> str:
    """Da formato de moneda a un número, p. ej. 1234567 -> '$1.234.567'."""
    if float(value).is_integer():
        text = f"{int(value):,}".replace(",", ".")
        return f"${text}"
    text = f"{value:,.2f}".replace(",", "#").replace(".", ",").replace("#", ".")
    return f"${text}"


@dataclass
class EstructuraDatosAfiliado:
    """Un registro de afiliado (el dato que se guarda en la pila, la cola y la lista)."""

    id_type: str
    id_number: str
    full_name: str
    current_income: int
    desired_service: str
    employment_type: str
    affiliation_fee: float
    affiliation_date: date

    def as_row(self) -> tuple:
        """Valores en el mismo orden que las columnas del Treeview."""
        return (
            self.id_type,
            self.id_number,
            self.full_name,
            format_money(self.current_income),
            self.desired_service,
            self.employment_type,
            format_money(self.affiliation_fee),
            self.affiliation_date.strftime("%d/%m/%Y"),
        )


class AffiliateRepository:
    """Contiene las tres estructuras lineales y las operaciones sobre ellas."""

    def __init__(self) -> None:
        self._stack: list[EstructuraDatosAfiliado] = []
        self._queue: deque[EstructuraDatosAfiliado] = deque()
        self._list: list[EstructuraDatosAfiliado] = []

    # --------------------------------------------------------------- registrar
    def register(self, structure: str, affiliate: EstructuraDatosAfiliado) -> None:
        """Inserción por defecto: apilar (pila), encolar (cola), agregar al final (lista)."""
        if structure == "Pila":
            self._stack.append(affiliate)
        elif structure == "Cola":
            self._queue.append(affiliate)
        else:
            self._list.append(affiliate)

    # ---------------------------------------------------------------- eliminar
    def peek(self, structure: str) -> Optional[EstructuraDatosAfiliado]:
        """Elemento que eliminaría el botón Eliminar (tope / frente); None si está vacía."""
        if structure == "Pila":
            return self._stack[-1] if self._stack else None
        if structure == "Cola":
            return self._queue[0] if self._queue else None
        return None

    def remove(self, structure: str) -> Optional[EstructuraDatosAfiliado]:
        """Desapila (pila) o desencola (cola). Devuelve el registro eliminado o None."""
        if structure == "Pila" and self._stack:
            return self._stack.pop()
        if structure == "Cola" and self._queue:
            return self._queue.popleft()
        return None

    def find_in_list(self, id_number: str) -> Optional[EstructuraDatosAfiliado]:
        """Búsqueda lineal por número de identificación en la lista."""
        for affiliate in self._list:
            if affiliate.id_number == id_number:
                return affiliate
        return None

    def remove_from_list(self, id_number: str) -> Optional[EstructuraDatosAfiliado]:
        """Elimina de la lista al primer afiliado con ese número de identificación."""
        for index, affiliate in enumerate(self._list):
            if affiliate.id_number == id_number:
                return self._list.pop(index)
        return None

    # ------------------------------------------------------------- visualizar
    def items(self, structure: str) -> list[EstructuraDatosAfiliado]:
        """Registros en orden de visualización (pila: tope primero; cola: frente primero)."""
        if structure == "Pila":
            return list(reversed(self._stack))
        if structure == "Cola":
            return list(self._queue)
        return list(self._list)

    def count(self, structure: str) -> int:
        return len(self.items(structure))

    # ----------------------------------------------------------------- reporte
    def report(self, structure: str) -> str:
        """Pila: suma de tarifas. Cola: cantidad de registros. Lista: promedio de ingresos."""
        records = self.items(structure)
        if structure == "Pila":
            return f"Suma de tarifas: {format_money(sum(r.affiliation_fee for r in records))}"
        if structure == "Cola":
            return f"Registros en la cola: {len(records)}"
        average = sum(r.current_income for r in records) / len(records) if records else 0
        return f"Promedio de ingresos: {format_money(average)}"
