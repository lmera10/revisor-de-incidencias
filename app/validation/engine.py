from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

import pandas as pd

from . import rules


@dataclass
class ValidationResult:
    row_number: int
    row_values: Dict[str, str]
    problem_details: List[str]

    def as_dict(self) -> dict:
        data = {col: self.row_values.get(col, "") for col in rules.ALL_COLUMNS}
        data["Columnas faltantes"] = ", ".join(self.problem_details)
        return data


INCIDENCE_RULES = {
    "IN1": rules.rule_in1,
    "IN2": rules.rule_in2,
    "IN3": rules.rule_in3,
    "IN4": rules.rule_in4,
    "IN5": rules.rule_in5,
    "IN6": rules.rule_in6,
    "IN7": rules.rule_in7,
}


def _normalize_incidence(value) -> str:
    if rules.is_empty(value):
        return ""
    # Extrae solo los primeros 3 caracteres (IN1, IN2, IN3, etc.)
    incidence = str(value).strip().upper()
    # Toma solo "INX" de "INX - DESCRIPCION"
    if len(incidence) >= 3:
        incidence = incidence[:3]
    return incidence


def validate_dataframe(
    df: pd.DataFrame,
    cycle_averages: Optional[Dict[str, float]] = None
) -> List[ValidationResult]:

    # Validación de columnas obligatorias
    missing = [c for c in rules.ALL_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas en el Excel: {', '.join(missing)}")

    results: List[ValidationResult] = []
    cycle_averages = cycle_averages or {}

    # Campos obligatorios básicos (siempre deben estar presentes)
    basic_required_fields = [
        "Recorrido", "Servicio", "Salida programada", "Salida real", 
        "Unidad", "Incidencia", "Conductor"
    ]

    for idx, row in df.iterrows():
        issues = []

        # -------------------------
        # Identificar la incidencia (campo principal)
        # -------------------------
        incidence = _normalize_incidence(row.get("Incidencia"))

        # -------------------------
        # Validaciones específicas por incidencia
        # -------------------------
        if incidence:
            rule_fn = INCIDENCE_RULES.get(incidence)
            if rule_fn is not None:
                issues.extend(rule_fn(row))
        else:
            # Sin incidencia definida
            issues.extend(rules.rule_no_incidence(row))

        # -------------------------
        # Regla especial: Servicio == 0 → ignorar si NO es IN7
        # -------------------------
        servicio_zero = rules.to_int(row.get("Servicio")) == 0
        if servicio_zero and incidence != "IN7":
            continue

        # -------------------------
        # Regla de ciclos (si aplica)
        # -------------------------
        if cycle_averages:
            issues.extend(rules.rule_cycle(row, cycle_averages))

        # -------------------------
        # Si no hay errores, no se muestra la fila
        # -------------------------
        if not issues:
            continue

        excel_row = idx + 2  # encabezado + índice base 0

        row_values = {
            col: "" if rules.is_empty(row.get(col)) else str(row.get(col))
            for col in rules.ALL_COLUMNS
        }

        # -------------------------
        # Construcción del detalle de errores
        # -------------------------
        problem_details: List[str] = []

        for field, message in issues:
            # Solo mostrar el nombre de la columna
            if field not in problem_details:
                problem_details.append(field)

        results.append(
            ValidationResult(
                row_number=excel_row,
                row_values=row_values,
                problem_details=problem_details,
            )
        )

    return results


def errors_to_dataframe(results: Iterable[ValidationResult]) -> pd.DataFrame:
    return pd.DataFrame(
        [r.as_dict() for r in results],
        columns=[*rules.ALL_COLUMNS, "Columnas faltantes"],
    )
