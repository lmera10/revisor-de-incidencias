from __future__ import annotations

from datetime import time
from typing import List

import pandas as pd
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.validation.engine import ValidationResult, validate_dataframe
from app.validation.rules import ALL_COLUMNS, to_time


ERROR_HEADERS = [*ALL_COLUMNS, "Columnas faltantes"]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Revisión de Incidencias")
        self.resize(1200, 600)

        self.df: pd.DataFrame | None = None
        self.cycle_averages = {}

        self.load_button = QPushButton("Cargar Excel")
        self.validate_button = QPushButton("Validar")
        self.validate_button.setEnabled(False)

        self.file_label = QLabel("Ningun archivo cargado")
        self.file_label.setWordWrap(True)

        self.table = QTableWidget(0, len(ERROR_HEADERS))
        self.table.setHorizontalHeaderLabels(ERROR_HEADERS)
        self.table.setSortingEnabled(True)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.validate_button)
        button_layout.addStretch(1)

        layout = QVBoxLayout()
        layout.addLayout(button_layout)
        layout.addWidget(self.file_label)
        layout.addWidget(self.table)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_button.clicked.connect(self.load_excel)
        self.validate_button.clicked.connect(self.validate)

    def load_excel(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Excel",
            "",
            "Excel (*.xlsx *.xls)",
        )
        if not path:
            return

        try:
            df = pd.read_excel(path, engine="openpyxl", dtype=str)
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"No se pudo leer el Excel: {exc}")
            return

        # Filtrar registros entre 04:00 AM y 14:00 PM
        df = self._filter_by_time_range(df)
        
        self.df = df
        self.file_label.setText(path)
        self.validate_button.setEnabled(True)
        self.table.setRowCount(0)

    def _filter_by_time_range(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filtra el dataframe para mostrar solo registros entre las 04:00 AM y 14:00 PM
        usando la columna 'Salida programada'
        """
        start_time = time(4, 0)  # 04:00 AM
        end_time = time(14, 0)   # 14:00 PM
        
        def is_within_range(row):
            hour_value = to_time(row.get("Salida programada"))
            if hour_value is None:
                return False
            return start_time <= hour_value <= end_time
        
        # Aplicar el filtro
        mask = df.apply(is_within_range, axis=1)
        filtered_df = df[mask].reset_index(drop=True)
        
        return filtered_df

    def validate(self) -> None:
        if self.df is None:
            QMessageBox.warning(self, "Atencion", "Primero cargue un Excel")
            return

        try:
            results = validate_dataframe(self.df, self.cycle_averages)
        except ValueError as exc:
            QMessageBox.critical(self, "Error", str(exc))
            return

        self.populate_table(results)
        QMessageBox.information(self, "Validacion", f"Errores encontrados: {len(results)}")

    def populate_table(self, results: List[ValidationResult]) -> None:
        was_sorting = self.table.isSortingEnabled()
        if was_sorting:
            self.table.setSortingEnabled(False)

        self.table.setRowCount(len(results))

        for row_index, result in enumerate(results):
            row_dict = result.as_dict()
            values = [row_dict.get(header, "") for header in ERROR_HEADERS]
            for col_index, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row_index, col_index, item)

        self.table.resizeColumnsToContents()
        if was_sorting:
            self.table.setSortingEnabled(True)
