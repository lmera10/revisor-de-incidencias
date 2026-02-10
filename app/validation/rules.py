from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import Any, Dict, Iterable, List, Optional, Tuple

import pandas as pd

ALL_COLUMNS = [
    "Recorrido",
    "Servicio",
    "Unidad",
    "Salida programada",
    "Salida real",
    "Hora de llegada",
    "Ciclo",
    "Unidad saliente",
    "Hora cambio",
    "Parada",
    "Incidencia",
    "Motivo",
    "Código",
    "Conductor",
    "Observaciones",
]


def is_empty(value: Any) -> bool:
    if value is None:
        return True
    try:
        if pd.isna(value):
            return True
    except Exception:
        pass
    if isinstance(value, str):
        # Normalizar cadenas
        clean = value.strip().lower()
        if clean == "" or clean == "nan":
            return True
    return False


def to_time(value: Any) -> Optional[time]:
    if is_empty(value):
        return None
    if isinstance(value, time):
        return value
    if isinstance(value, datetime):
        return value.time()
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime().time()
    if isinstance(value, (int, float)):
        if 0 <= value < 1:
            seconds = int(round(value * 24 * 60 * 60))
            return (datetime(1900, 1, 1) + timedelta(seconds=seconds)).time()
    if isinstance(value, str):
        ts = pd.to_datetime(value, errors="coerce")
        if pd.isna(ts):
            return None
        if isinstance(ts, pd.Timestamp):
            return ts.to_pydatetime().time()
    return None


def to_int(value: Any) -> Optional[int]:
    if is_empty(value):
        return None
    try:
        return int(str(value).strip())
    except Exception:
        return None


def to_float(value: Any) -> Optional[float]:
    if is_empty(value):
        return None
    try:
        return float(value)
    except Exception:
        return None


def check_required(row: pd.Series, required_fields: Iterable[str], rule: str) -> List[Tuple[str, str]]:
    issues: List[Tuple[str, str]] = []
    for field in required_fields:
        if is_empty(row.get(field)):
            issues.append((field, f"{rule}: Campo obligatorio"))
    return issues


def check_must_be_empty(row: pd.Series, empty_fields: Iterable[str], rule: str) -> List[Tuple[str, str]]:
    issues: List[Tuple[str, str]] = []
    for field in empty_fields:
        if not is_empty(row.get(field)):
            issues.append((field, f"{rule}: Campo debe estar vacio"))
    return issues


def rule_in1(row: pd.Series) -> List[Tuple[str, str]]:
    issues: List[Tuple[str, str]] = []
    
    # Campos obligatorios para IN1 (todos excepto Unidad saliente, Hora cambio y Parada)
    required = [c for c in ALL_COLUMNS if c not in {"Unidad saliente", "Hora cambio", "Parada"}]
    issues.extend(check_required(row, required, "IN1"))
    
    # Unidad saliente no debe tener datos
    if not is_empty(row.get("Unidad saliente")):
        issues.append(("Unidad saliente", "IN1: No debe haber dato aqui"))
    
    return issues


def rule_in2(row: pd.Series) -> List[Tuple[str, str]]:
    issues: List[Tuple[str, str]] = []
    
    # Campos obligatorios para IN2 (todos excepto Unidad saliente, Hora cambio y Parada)
    required = [c for c in ALL_COLUMNS if c not in {"Unidad saliente", "Hora cambio", "Parada"}]
    issues.extend(check_required(row, required, "IN2"))
    
    # Estos campos no deben tener datos
    issues.extend(check_must_be_empty(row, ["Unidad saliente", "Hora cambio", "Parada"], "IN2"))
    
    # Validar que Salida real sea antes que Salida programada (adelantada)
    t_prog = to_time(row.get("Salida programada"))
    t_real = to_time(row.get("Salida real"))
    if t_prog is None or t_real is None:
        issues.append(("Salida real", "IN2: Salida real y programada deben ser validas"))
    elif not (t_real < t_prog):
        issues.append(("Salida real", "IN2: Salida real debe ser menor que Salida programada"))
    
    return issues


def rule_in3(row: pd.Series) -> List[Tuple[str, str]]:
    issues: List[Tuple[str, str]] = []
    
    # Campos obligatorios para IN3 (todos excepto Unidad saliente, Hora cambio y Parada)
    required = [c for c in ALL_COLUMNS if c not in {"Unidad saliente", "Hora cambio", "Parada"}]
    issues.extend(check_required(row, required, "IN3"))
    
    # Estos campos no deben tener datos
    issues.extend(check_must_be_empty(row, ["Unidad saliente", "Hora cambio", "Parada"], "IN3"))
    
    # Validar que Salida real sea después que Salida programada (atrasada)
    t_prog = to_time(row.get("Salida programada"))
    t_real = to_time(row.get("Salida real"))
    if t_prog is None or t_real is None:
        issues.append(("Salida real", "IN3: Salida real y programada deben ser validas"))
    elif not (t_real > t_prog):
        issues.append(("Salida real", "IN3: Salida real debe ser mayor que Salida programada"))
    
    return issues


def rule_in4(row: pd.Series) -> List[Tuple[str, str]]:
    issues: List[Tuple[str, str]] = []
    
    # Campos obligatorios para IN4 (todos excepto Unidad saliente, Hora cambio y Parada)
    required = [c for c in ALL_COLUMNS if c not in {"Unidad saliente", "Hora cambio", "Parada"}]
    issues.extend(check_required(row, required, "IN4"))
    
    # Estos campos no deben tener datos
    issues.extend(check_must_be_empty(row, ["Unidad saliente", "Hora cambio", "Parada"], "IN4"))
    
    # Validar que Salida real sea después que Salida programada
    t_prog = to_time(row.get("Salida programada"))
    t_real = to_time(row.get("Salida real"))
    if t_prog is None or t_real is None:
        issues.append(("Salida real", "IN4: Salida real y programada deben ser validas"))
    elif not (t_real > t_prog):
        issues.append(("Salida real", "IN4: Salida real debe ser mayor que Salida programada"))
    
    return issues


def rule_in5(row: pd.Series) -> List[Tuple[str, str]]:
    required = [c for c in ALL_COLUMNS if c not in {"Parada"}]
    issues = check_required(row, required, "IN5")
    issues += check_must_be_empty(row, ["Parada"], "IN5")
    return issues


def rule_in6(row: pd.Series) -> List[Tuple[str, str]]:
    issues: List[Tuple[str, str]] = []
    allowed = {"Recorrido", "Servicio", "Salida programada", "Incidencia", "Motivo", "Observaciones"}
    
    for field in ALL_COLUMNS:
        if field in allowed:
            continue
        value = row.get(field)
        if not is_empty(value):
            issues.append((
                field,
                "IN6: Solo se permiten datos en Recorrido, Servicio, Salida programada, Incidencia, Motivo y Observaciones",
            ))
    
    return issues


def rule_in7(row: pd.Series) -> List[Tuple[str, str]]:
    issues: List[Tuple[str, str]] = []
    
    motivo = to_int(row.get("Motivo"))
    hora_cambio = row.get("Hora cambio")
    unidad_saliente = row.get("Unidad saliente")
    
    # Campos obligatorios: todos excepto Unidad saliente
    required = [c for c in ALL_COLUMNS if c not in {"Unidad saliente"}]
    issues.extend(check_required(row, required, "IN7"))
    
    # Determinar si es motivo de cambio (8-29)
    is_cambio_motivo = motivo is not None and 8 <= motivo <= 29
    
    # Unidad saliente nunca debe tener datos en IN7
    if not is_empty(unidad_saliente):
        issues.append(("Unidad saliente", "IN7: No debe haber dato aqui"))
    return issues


def rule_no_incidence(row: pd.Series) -> List[Tuple[str, str]]:
    issues: List[Tuple[str, str]] = []
    t_prog = to_time(row.get("Salida programada"))
    t_real = to_time(row.get("Salida real"))
    if t_prog is None or t_real is None:
        issues.append(("Salida real", "SP/SR: Salida programada y real deben existir y ser validas"))
    elif t_prog != t_real:
        issues.append(("Salida real", "SP/SR: Salida programada debe ser igual a Salida real"))
    return issues


def rule_cycle(row: pd.Series, cycle_averages: Dict[str, float]) -> List[Tuple[str, str]]:
    issues: List[Tuple[str, str]] = []
    recorrido_raw = row.get("Recorrido")
    if is_empty(recorrido_raw):
        return issues
    recorrido = str(recorrido_raw).strip()
    if not recorrido:
        return issues
    if recorrido not in cycle_averages:
        return issues

    ciclo = to_float(row.get("Ciclo"))
    promedio = cycle_averages.get(recorrido)
    if promedio is None:
        return issues
    if ciclo is None:
        issues.append(("Ciclo", f"Ciclo invalido; promedio permitido {promedio} para Recorrido {recorrido}"))
    elif ciclo > promedio:
        issues.append(("Ciclo", f"Ciclo {ciclo} supera promedio permitido {promedio} para Recorrido {recorrido}"))
    return issues


# =========================================
# Nuevas reglas para detectar errores humanos
# =========================================

def check_suspicious_placeholders(row: pd.Series) -> List[Tuple[str, str]]:
    """Detecta valores placeholders comunes que indican errores de digitación"""
    issues: List[Tuple[str, str]] = []
    suspicious_values = ["N/A", "NA", "ERROR", "---", "...", "XXX", "SIN DATO", "POR LLENAR", "TEMP"]
    
    for field in ALL_COLUMNS:
        value = row.get(field)
        if is_empty(value):
            continue
        value_str = str(value).strip().upper()
        if value_str in suspicious_values:
            issues.append((field, f"Valor sospechoso: '{value}' (parece un placeholder)"))
    
    return issues


def check_extra_spaces(row: pd.Series) -> List[Tuple[str, str]]:
    """Detecta espacios extras al principio o final que pueden causar problemas"""
    issues: List[Tuple[str, str]] = []
    
    for field in ALL_COLUMNS:
        value = row.get(field)
        if is_empty(value):
            continue
        value_str = str(value)
        # Detectar espacios extras
        if value_str != value_str.strip():
            issues.append((field, "Error de digitación: contiene espacios al inicio o final"))
    
    return issues


def check_invalid_characters(row: pd.Series) -> List[Tuple[str, str]]:
    """Detecta caracteres inválidos o extraños en campos específicos"""
    issues: List[Tuple[str, str]] = []
    
    # Campos que solo deberían contener números y caracteres básicos
    numeric_fields = {"Unidad", "Servicio", "Código", "Recorrido"}
    for field in numeric_fields:
        value = row.get(field)
        if is_empty(value):
            continue
        value_str = str(value).strip()
        
        # Detectar caracteres especiales sospechosos
        if any(char in value_str for char in ["@", "#", "$", "%", "&", "*", "!", "¡"]):
            issues.append((field, f"Contiene caracteres inválidos: '{value}'"))
    
    return issues


def check_numeric_fields_validity(row: pd.Series) -> List[Tuple[str, str]]:
    """Valida que campos numéricos tengan valores válidos"""
    issues: List[Tuple[str, str]] = []
    
    numeric_checks = {
        "Servicio": (1, 999),
        "Unidad": (1, 99999),
        "Código": (1, 999),
    }
    
    for field, (min_val, max_val) in numeric_checks.items():
        value = row.get(field)
        if is_empty(value):
            continue
        
        num = to_int(value)
        if num is None:
            issues.append((field, f"No es un número válido: '{value}'"))
        elif num < min_val or num > max_val:
            issues.append((field, f"Número fuera de rango ({min_val}-{max_val}): {num}"))
    
    return issues


def check_text_field_quality(row: pd.Series) -> List[Tuple[str, str]]:
    """Detecta problemas de calidad en campos de texto"""
    issues: List[Tuple[str, str]] = []
    
    text_fields = {"Conductor", "Motivo"}
    
    for field in text_fields:
        value = row.get(field)
        if is_empty(value):
            continue
        
        value_str = str(value).strip()
        
        # Detectar si es solo números cuando debería ser texto
        if field == "Conductor" and value_str.isdigit():
            issues.append((field, "El conductor debe ser un nombre, no solo números"))
        
        # Detectar textos muy cortos (posible error)
        if len(value_str) < 2 and field in {"Conductor", "Motivo"}:
            issues.append((field, "Texto muy corto (posible error de digitación)"))
        
        # Detectar duplicados de caracteres (typos comunes)
        if any(char * 3 in value_str for char in "abcdefghijklmnopqrstuvwxyz0123456789"):
            issues.append((field, "Contiene caracteres repetidos excesivamente"))
    
    return issues


def check_for_empty_required_fields(row: pd.Series, required_fields: List[str]) -> List[Tuple[str, str]]:
    """Detecta campos obligatorios vacíos"""
    issues: List[Tuple[str, str]] = []
    
    for field in required_fields:
        if is_empty(row.get(field)):
            issues.append((field, "Campo obligatorio vacío"))
    
    return issues
