from __future__ import annotations

from datetime import time
from typing import List

import pandas as pd
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from app.validation.engine import (
    ValidationResult,
    validate_cycles_dataframe,
    validate_dataframe,
)
from app.validation.rules import ALL_COLUMNS, to_time


ERROR_HEADERS = [*ALL_COLUMNS, "Columnas faltantes"]


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Revisión de Incidencias")
        self.resize(1200, 680)

        self.df: pd.DataFrame | None = None
        self.cycle_averages = {}

        self.load_button = QPushButton("Cargar Excel")
        self.validate_button = QPushButton("Validar")
        self.validate_button.setEnabled(False)
        self.cycle_button = QPushButton("Verificador de ciclos")
        self.cycle_button.setEnabled(False)
        self.load_button.setProperty("variant", "primary")

        self.file_label = QLabel("Ningún archivo cargado")
        self.file_label.setWordWrap(True)
        self.file_label.setObjectName("FileLabel")

        self.table = QTableWidget(0, len(ERROR_HEADERS))
        self.table.setHorizontalHeaderLabels(ERROR_HEADERS)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)

        header_widget = QWidget()
        header_widget.setObjectName("Header")
        header_layout = QVBoxLayout()
        header_layout.setContentsMargins(18, 14, 18, 14)
        header_layout.setSpacing(4)

        title_label = QLabel("Revisión de Incidencias")
        title_label.setObjectName("TitleLabel")
        subtitle_label = QLabel("Carga un Excel y valida incidencias o ciclos por ruta.")
        subtitle_label.setObjectName("SubtitleLabel")
        subtitle_label.setWordWrap(True)

        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        header_widget.setLayout(header_layout)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.addWidget(self.load_button)
        button_layout.addWidget(self.validate_button)
        button_layout.addWidget(self.cycle_button)
        button_layout.addStretch(1)

        layout = QVBoxLayout()
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(12)
        layout.addWidget(header_widget)
        layout.addLayout(button_layout)
        layout.addWidget(self.file_label)
        layout.addWidget(self.table)

        container = QWidget()
        container.setObjectName("MainContainer")
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.load_button.clicked.connect(self.load_excel)
        self.validate_button.clicked.connect(self.validate)
        self.cycle_button.clicked.connect(self.validate_cycles)
        self.setStyleSheet(
            """
            QWidget {
                font-family: "Bahnschrift", "Candara", "Segoe UI";
                font-size: 11pt;
                color: #1d1f23;
            }
            #MainContainer {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f4f6f9, stop:1 #e7ecf3);
            }
            #Header {
                background: #ffffff;
                border: 1px solid #d8dee9;
                border-radius: 12px;
            }
            #TitleLabel {
                font-size: 18pt;
                font-weight: 600;
                color: #0f172a;
            }
            #SubtitleLabel {
                color: #475569;
            }
            #FileLabel {
                background: #ffffff;
                border: 1px dashed #cfd6e1;
                border-radius: 10px;
                padding: 8px 12px;
                color: #334155;
            }
            QPushButton {
                background: #ffffff;
                border: 1px solid #cfd6e1;
                border-radius: 10px;
                padding: 8px 14px;
            }
            QPushButton:hover {
                background: #f2f5f9;
            }
            QPushButton:pressed {
                background: #e7ecf3;
            }
            QPushButton[variant="primary"] {
                background: #1d4ed8;
                color: #ffffff;
                border: 1px solid #1d4ed8;
            }
            QPushButton[variant="primary"]:hover {
                background: #1e40af;
            }
            QPushButton:disabled {
                color: #9aa5b1;
                border-color: #e2e8f0;
                background: #f7f9fc;
            }
            QTableWidget {
                background: #ffffff;
                border: 1px solid #d8dee9;
                border-radius: 12px;
                gridline-color: #e2e8f0;
            }
            QHeaderView::section {
                background: #f1f5f9;
                color: #0f172a;
                border: none;
                padding: 8px;
                font-weight: 600;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:selected {
                background: #dbeafe;
                color: #0f172a;
            }
            """
        )

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

        # Filtrar registros entre 04:50 y 14:00
        df = self._filter_by_time_range(df)
        
        self.df = df
        self.file_label.setText(path)
        self.validate_button.setEnabled(True)
        self.cycle_button.setEnabled(True)
        self.table.setRowCount(0)

    def _filter_by_time_range(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filtra el dataframe para mostrar solo registros entre las 04:50 y 14:00
        usando la columna 'Salida programada'
        """
        start_time = time(4, 50)  # 04:50
        end_time = time(14, 0)    # 14:00
        
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
        self._show_info("Validacion", f"Errores encontrados: {len(results)}")

    def validate_cycles(self) -> None:
        if self.df is None:
            QMessageBox.warning(self, "Atencion", "Primero cargue un Excel")
            return

        try:
            results = validate_cycles_dataframe(self.df, self.cycle_averages)
        except ValueError as exc:
            QMessageBox.critical(self, "Error", str(exc))
            return

        self.populate_table(results)
        self._show_info("Verificador de ciclos", f"Errores encontrados: {len(results)}")

    def _show_info(self, title: str, message: str) -> None:
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.setStyleSheet("QLabel { color: #b91c1c; font-weight: 600; }")
        msg.exec()

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
