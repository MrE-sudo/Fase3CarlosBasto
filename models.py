"""Data model, fee rules and linear data structures (stack, queue, list).

All data is kept in main memory: no databases and no files are used.
  - Stack : Python ``list``          (push = append, pop = pop)
  - Queue : ``collections.deque``    (enqueue = append, dequeue = popleft)
  - List  : Python ``list``          (add at the end, remove by ID number)
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import date
from typing import Optional

ID_TYPES = ("CC", "CE", "NUIP", "PAS")
SERVICES = (
    "Unemployment Subsidy",
    "Park Admission",
    "Training Course",
    "Travel Package",
    "Preventive Medicine",
)
EMPLOYMENT_TYPES = ("Employee", "Independent")
STRUCTURES = ("Stack", "Queue", "List")

# The fee tables start at $1.000.000: lower incomes are not covered by the tables.
MIN_INCOME = 1_000_000

# Upper limits of the income brackets (inclusive). Above the last one: "> $5.000.000".
INCOME_BRACKET_LIMITS = (2_000_000, 3_000_000, 4_000_000, 5_000_000)
EMPLOYEE_FEES = (45_000, 60_000, 75_000, 90_000, 150_000)
INDEPENDENT_FEES = (10_000, 20_000, 30_000, 40_000, 80_000)

# Fixed surcharge per service. Preventive Medicine is a percentage of the income.
SERVICE_SURCHARGE = {
    "Unemployment Subsidy": 0,
    "Park Admission": 2_500,
    "Training Course": 7_500,
    "Travel Package": 10_000,
}
PREVENTIVE_MEDICINE_RATE = 0.10


def calculate_affiliation_fee(income: int, employment_type: str, service: str) -> float:
    """Return the affiliation fee for the given income, employment type and service.

    Raises ValueError when the income is below MIN_INCOME (not covered by the fee tables).
    """
    if income < MIN_INCOME:
        raise ValueError(f"Income must be at least {format_money(MIN_INCOME)}.")
    fees = EMPLOYEE_FEES if employment_type == "Employee" else INDEPENDENT_FEES

    bracket = len(INCOME_BRACKET_LIMITS)  # default: the "> 5.000.000" bracket
    for index, limit in enumerate(INCOME_BRACKET_LIMITS):
        if income <= limit:
            bracket = index
            break
    base_fee = fees[bracket]

    if service == "Preventive Medicine":
        surcharge = income * PREVENTIVE_MEDICINE_RATE
    else:
        surcharge = SERVICE_SURCHARGE.get(service, 0)
    return round(base_fee + surcharge, 2)


def format_money(value: float) -> str:
    """Format a number as currency, e.g. 1234567 -> '$1,234,567'."""
    if float(value).is_integer():
        return f"${int(value):,}"
    return f"${value:,.2f}"


@dataclass
class EstructuraDatosAfiliado:
    """One affiliate record (the data stored inside the stack, queue and list)."""

    id_type: str
    id_number: str
    full_name: str
    current_income: int
    desired_service: str
    employment_type: str
    affiliation_fee: float
    affiliation_date: date

    def as_row(self) -> tuple:
        """Values in the same order as the Treeview columns."""
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
    """Holds the three linear structures and the operations over them."""

    def __init__(self) -> None:
        self._stack: list[EstructuraDatosAfiliado] = []
        self._queue: deque[EstructuraDatosAfiliado] = deque()
        self._list: list[EstructuraDatosAfiliado] = []

    # ---------------------------------------------------------------- register
    def register(self, structure: str, affiliate: EstructuraDatosAfiliado) -> None:
        """Default insertion: push (stack), enqueue (queue), append (list)."""
        if structure == "Stack":
            self._stack.append(affiliate)
        elif structure == "Queue":
            self._queue.append(affiliate)
        else:
            self._list.append(affiliate)

    # ------------------------------------------------------------------ remove
    def peek(self, structure: str) -> Optional[EstructuraDatosAfiliado]:
        """Element that Delete would remove (top / front); None if empty."""
        if structure == "Stack":
            return self._stack[-1] if self._stack else None
        if structure == "Queue":
            return self._queue[0] if self._queue else None
        return None

    def remove(self, structure: str) -> Optional[EstructuraDatosAfiliado]:
        """Pop (stack) or dequeue (queue). Returns the removed record or None."""
        if structure == "Stack" and self._stack:
            return self._stack.pop()
        if structure == "Queue" and self._queue:
            return self._queue.popleft()
        return None

    def find_in_list(self, id_number: str) -> Optional[EstructuraDatosAfiliado]:
        """Linear search by ID number in the list structure."""
        for affiliate in self._list:
            if affiliate.id_number == id_number:
                return affiliate
        return None

    def remove_from_list(self, id_number: str) -> Optional[EstructuraDatosAfiliado]:
        """Remove the first affiliate with that ID number from the list."""
        for index, affiliate in enumerate(self._list):
            if affiliate.id_number == id_number:
                return self._list.pop(index)
        return None

    # -------------------------------------------------------------------- view
    def items(self, structure: str) -> list[EstructuraDatosAfiliado]:
        """Records in display order (stack: top first, queue: front first)."""
        if structure == "Stack":
            return list(reversed(self._stack))
        if structure == "Queue":
            return list(self._queue)
        return list(self._list)

    def count(self, structure: str) -> int:
        return len(self.items(structure))

    # ------------------------------------------------------------------ report
    def report(self, structure: str) -> str:
        """Stack: sum of fees. Queue: number of records. List: average income."""
        records = self.items(structure)
        if structure == "Stack":
            return f"Total fees: {format_money(sum(r.affiliation_fee for r in records))}"
        if structure == "Queue":
            return f"Records in queue: {len(records)}"
        average = sum(r.current_income for r in records) / len(records) if records else 0
        return f"Average income: {format_money(average)}"
