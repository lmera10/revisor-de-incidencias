from __future__ import annotations

from datetime import time
from typing import List

import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
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

STYLESHEET = """
/* ── Base ─────────────────────────────────────────────── */
QWidget {
    font-family: "Segoe UI", "Bahnschrift", "Candara";
    font-size: 10pt;
    color: #0f172a;
}

/* ── Main container ───────────────────────────────────── */
#MainContainer {
    background: #f1f5f9;
}

/* ── Header ───────────────────────────────────────────── */
#Header {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 #0f2544, stop:1 #1d4ed8);
    border-radius: 14px;
    min-height: 78px;
}
#TitleLabel {
    font-size: 19pt;
    font-weight: 700;
    color: #ffffff;
}
#SubtitleLabel {
    font-size: 9pt;
    color: #93c5fd;
}
#BrandLabel {
    font-size: 14pt;
    font-weight: 700;
    color: #ffffff;
}
#BrandSubLabel {
    font-size: 8pt;
    font-weight: 600;
    color: #6ee7b7;
    letter-spacing: 1px;
}

/* ── Toolbar card ─────────────────────────────────────── */
#ToolbarCard {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
}
#ToolSep {
    background: #e2e8f0;
}
#ShiftLabel {
    color: #64748b;
    font-weight: 600;
    font-size: 9.5pt;
}

/* ── Buttons ──────────────────────────────────────────── */
QPushButton {
    border-radius: 8px;
    padding: 7px 18px;
    font-weight: 600;
    font-size: 10pt;
    border: none;
    background: #e2e8f0;
    color: #334155;
}
QPushButton:hover  { background: #cbd5e1; }
QPushButton:pressed { background: #94a3b8; }
QPushButton:disabled { background: #f1f5f9; color: #c4cdd6; }

QPushButton#LoadButton { background: #1d4ed8; color: #ffffff; }
QPushButton#LoadButton:hover   { background: #1e40af; }
QPushButton#LoadButton:pressed { background: #1e3a8a; }

QPushButton#ValidateButton { background: #0f766e; color: #ffffff; }
QPushButton#ValidateButton:hover   { background: #0d9488; }
QPushButton#ValidateButton:pressed { background: #115e59; }
QPushButton#ValidateButton:disabled { background: #f1f5f9; color: #c4cdd6; }

QPushButton#CycleButton { background: #7c3aed; color: #ffffff; }
QPushButton#CycleButton:hover   { background: #6d28d9; }
QPushButton#CycleButton:pressed { background: #5b21b6; }
QPushButton#CycleButton:disabled { background: #f1f5f9; color: #c4cdd6; }

/* ── ComboBox ─────────────────────────────────────────── */
QComboBox {
    background: #f8fafc;
    border: 1.5px solid #cbd5e1;
    border-radius: 8px;
    padding: 6px 10px;
    min-width: 195px;
    font-weight: 500;
}
QComboBox:hover { border-color: #1d4ed8; background: #eff6ff; }
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    selection-background-color: #eff6ff;
    selection-color: #1d4ed8;
}

/* ── File card ────────────────────────────────────────── */
#FileCard {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #1d4ed8;
    border-radius: 10px;
}
#FileLabel {
    color: #1e293b;
    font-size: 9.5pt;
    font-weight: 500;
}
#FileHint {
    color: #94a3b8;
    font-size: 8.5pt;
}

/* ── Results header card ──────────────────────────────── */
#ResultsHeaderCard {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-bottom: none;
    border-radius: 12px 12px 0 0;
}
#ResultsTitle {
    font-size: 11pt;
    font-weight: 700;
    color: #0f172a;
}
#BadgeWidget {
    border-radius: 10px;
    min-width: 22px;
    max-height: 22px;
    padding: 2px 7px;
}
#BadgeLabel {
    color: #ffffff;
    font-weight: 700;
    font-size: 9pt;
}

/* ── Table ────────────────────────────────────────────── */
QTableWidget {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-top: none;
    border-radius: 0 0 12px 12px;
    gridline-color: transparent;
    font-size: 9.5pt;
    outline: none;
}
QHeaderView::section {
    background: #f1f5f9;
    color: #475569;
    border: none;
    border-right: 1px solid #e2e8f0;
    border-bottom: 2px solid #cbd5e1;
    padding: 8px 10px;
    font-weight: 700;
    font-size: 8.5pt;
}
QHeaderView::section:last-child { border-right: none; }
QTableWidget::item {
    padding: 5px 10px;
    border-bottom: 1px solid #f1f5f9;
}
QTableWidget::item:selected {
    background: #eff6ff;
    color: #1e40af;
}
QTableWidget::item:alternate { background: #f8fafc; }

/* ── Scrollbars ───────────────────────────────────────── */
QScrollBar:vertical, QScrollBar:horizontal {
    background: #f1f5f9;
    border-radius: 4px;
    width: 8px;
    height: 8px;
    margin: 0;
}
QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
    background: #cbd5e1;
    border-radius: 4px;
    min-height: 28px;
    min-width: 28px;
}
QScrollBar::handle:vertical:hover,
QScrollBar::handle:horizontal:hover { background: #94a3b8; }
QScrollBar::add-line, QScrollBar::sub-line { width: 0; height: 0; }
"""


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Revisión de Incidencias")
        self.resize(1280, 720)
        self.setMinimumSize(920, 580)

        self.df: pd.DataFrame | None = None
        self.cycle_averages = {}

        self._build_ui()
        self.setStyleSheet(STYLESHEET)

    # ─────────────────────────── Build UI ──────────────────────────────

    def _build_ui(self) -> None:
        # ── Header ──────────────────────────────────────────────────────
        header_widget = QWidget()
        header_widget.setObjectName("Header")
        header_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(22, 16, 22, 16)
        header_layout.setSpacing(12)

        title_label = QLabel("Revisión de Incidencias")
        title_label.setObjectName("TitleLabel")
        subtitle_label = QLabel("Carga un archivo Excel y valida incidencias o ciclos por ruta.")
        subtitle_label.setObjectName("SubtitleLabel")

        title_vbox = QVBoxLayout()
        title_vbox.setSpacing(4)
        title_vbox.addWidget(title_label)
        title_vbox.addWidget(subtitle_label)

        brand_label = QLabel("MasterPro")
        brand_label.setObjectName("BrandLabel")
        brand_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        brand_sub = QLabel("TECH SOLUTIONS")
        brand_sub.setObjectName("BrandSubLabel")
        brand_sub.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        brand_vbox = QVBoxLayout()
        brand_vbox.setSpacing(2)
        brand_vbox.addWidget(brand_label)
        brand_vbox.addWidget(brand_sub)

        header_layout.addLayout(title_vbox)
        header_layout.addStretch(1)
        header_layout.addLayout(brand_vbox)

        # ── Toolbar card ─────────────────────────────────────────────────
        toolbar_card = QWidget()
        toolbar_card.setObjectName("ToolbarCard")
        toolbar_layout = QHBoxLayout(toolbar_card)
        toolbar_layout.setContentsMargins(14, 10, 14, 10)
        toolbar_layout.setSpacing(8)

        self.load_button = QPushButton("Cargar Excel")
        self.load_button.setObjectName("LoadButton")
        self.load_button.setToolTip("Abrir archivo Excel (.xlsx / .xls)")
        self.load_button.setMinimumHeight(36)

        self.validate_button = QPushButton("Validar Incidencias")
        self.validate_button.setObjectName("ValidateButton")
        self.validate_button.setEnabled(False)
        self.validate_button.setToolTip("Valida las reglas de incidencias del turno seleccionado")
        self.validate_button.setMinimumHeight(36)

        self.cycle_button = QPushButton("Verificar Ciclos")
        self.cycle_button.setObjectName("CycleButton")
        self.cycle_button.setEnabled(False)
        self.cycle_button.setToolTip("Verifica los tiempos de ciclo por ruta")
        self.cycle_button.setMinimumHeight(36)

        sep = QFrame()
        sep.setObjectName("ToolSep")
        sep.setFrameShape(QFrame.Shape.VLine)
        sep.setFixedWidth(1)
        sep.setFixedHeight(26)

        shift_lbl = QLabel("Turno:")
        shift_lbl.setObjectName("ShiftLabel")

        self.shift_combo = QComboBox()
        self.shift_combo.addItem("Turno 1  (05:00 – 14:00)", "turno1")
        self.shift_combo.addItem("Turno 2  (14:01 – 23:59)", "turno2")
        self.shift_combo.setMinimumHeight(36)

        toolbar_layout.addWidget(self.load_button)
        toolbar_layout.addWidget(self.validate_button)
        toolbar_layout.addWidget(self.cycle_button)
        toolbar_layout.addWidget(sep)
        toolbar_layout.addWidget(shift_lbl)
        toolbar_layout.addWidget(self.shift_combo)
        toolbar_layout.addStretch(1)

        # ── File card ────────────────────────────────────────────────────
        file_card = QWidget()
        file_card.setObjectName("FileCard")
        file_layout = QHBoxLayout(file_card)
        file_layout.setContentsMargins(14, 8, 14, 8)
        file_layout.setSpacing(10)

        file_text_vbox = QVBoxLayout()
        file_text_vbox.setSpacing(2)
        self.file_label = QLabel("Ningún archivo cargado")
        self.file_label.setObjectName("FileLabel")
        self.file_label.setWordWrap(True)
        self.file_hint = QLabel("Haz clic en 'Cargar Excel' para comenzar.")
        self.file_hint.setObjectName("FileHint")
        file_text_vbox.addWidget(self.file_label)
        file_text_vbox.addWidget(self.file_hint)

        file_layout.addLayout(file_text_vbox)
        file_layout.addStretch(1)

        # ── Results header ───────────────────────────────────────────────
        results_header = QWidget()
        results_header.setObjectName("ResultsHeaderCard")
        rh_layout = QHBoxLayout(results_header)
        rh_layout.setContentsMargins(14, 9, 14, 9)
        rh_layout.setSpacing(10)

        self.results_title = QLabel("Resultados")
        self.results_title.setObjectName("ResultsTitle")

        self.badge_widget = QWidget()
        self.badge_widget.setObjectName("BadgeWidget")
        self.badge_widget.setVisible(False)
        badge_layout = QHBoxLayout(self.badge_widget)
        badge_layout.setContentsMargins(6, 2, 6, 2)
        self.badge_label = QLabel("0")
        self.badge_label.setObjectName("BadgeLabel")
        self.badge_label.setAlignment(Qt.AlignCenter)
        badge_layout.addWidget(self.badge_label)

        rh_layout.addWidget(self.results_title)
        rh_layout.addWidget(self.badge_widget)
        rh_layout.addStretch(1)

        # ── Table ────────────────────────────────────────────────────────
        self.table = QTableWidget(0, len(ERROR_HEADERS))
        self.table.setHorizontalHeaderLabels(ERROR_HEADERS)
        self.table.setSortingEnabled(True)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        h = self.table.horizontalHeader()
        h.setStretchLastSection(True)
        h.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        h.setTextElideMode(Qt.TextElideMode.ElideNone)

        # ── Root layout ──────────────────────────────────────────────────
        root = QVBoxLayout()
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(10)
        root.addWidget(header_widget)
        root.addWidget(toolbar_card)
        root.addWidget(file_card)
        root.addWidget(results_header)
        root.addWidget(self.table)

        container = QWidget()
        container.setObjectName("MainContainer")
        container.setLayout(root)
        self.setCentralWidget(container)

        # ── Signals ──────────────────────────────────────────────────────
        self.load_button.clicked.connect(self.load_excel)
        self.validate_button.clicked.connect(self.validate)
        self.cycle_button.clicked.connect(self.validate_cycles)

    # ─────────────────────────── Logic ─────────────────────────────────

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
            QMessageBox.critical(self, "Error", f"No se pudo leer el Excel:\n{exc}")
            return

        self.df = df
        self.file_label.setText(path)
        self.file_hint.setText(
            f"{len(df):,} registros cargados  \u00b7  {len(df.columns)} columnas"
        )
        self.validate_button.setEnabled(True)
        self.cycle_button.setEnabled(True)
        self.table.setRowCount(0)
        self.badge_widget.setVisible(False)
        self.results_title.setText("Resultados")

    def _current_shift_key(self) -> str:
        return self.shift_combo.currentData() or "turno1"

    def _shift_time_range(self) -> tuple[time, time]:
        if self._current_shift_key() == "turno2":
            return time(14, 1), time(23, 59)
        return time(5, 0), time(14, 0)

    def _filter_by_time_range(self, df: pd.DataFrame) -> pd.DataFrame:
        start_time, end_time = self._shift_time_range()

        def is_within_range(row):
            hour_value = to_time(row.get("Salida programada"))
            if hour_value is None:
                return False
            if start_time <= end_time:
                return start_time <= hour_value <= end_time
            return hour_value >= start_time or hour_value <= end_time

        mask = df.apply(is_within_range, axis=1)
        return df[mask].reset_index(drop=True)

    def _filtered_df(self) -> pd.DataFrame:
        if self.df is None:
            return pd.DataFrame()
        return self._filter_by_time_range(self.df)

    def validate(self) -> None:
        if self.df is None:
            QMessageBox.warning(self, "Atención", "Primero cargue un archivo Excel.")
            return

        try:
            filtered_df = self._filtered_df()
            if filtered_df.empty:
                self.table.setRowCount(0)
                self._update_results_header("Validación de Incidencias", 0)
                self._show_info(
                    "Validación",
                    "No hay registros en el rango del turno seleccionado.",
                )
                return
            results = validate_dataframe(filtered_df, self.cycle_averages)
        except ValueError as exc:
            QMessageBox.critical(self, "Error", str(exc))
            return

        self._update_results_header("Validación de Incidencias", len(results))
        self.populate_table(results)
        self._show_info("Validación", f"Errores encontrados: {len(results)}")

    def validate_cycles(self) -> None:
        if self.df is None:
            QMessageBox.warning(self, "Atención", "Primero cargue un archivo Excel.")
            return

        try:
            filtered_df = self._filtered_df()
            if filtered_df.empty:
                self.table.setRowCount(0)
                self._update_results_header("Verificador de Ciclos", 0)
                self._show_info(
                    "Verificador de ciclos",
                    "No hay registros en el rango del turno seleccionado.",
                )
                return
            results = validate_cycles_dataframe(filtered_df, self.cycle_averages)
        except ValueError as exc:
            QMessageBox.critical(self, "Error", str(exc))
            return

        self._update_results_header("Verificador de Ciclos", len(results))
        self.populate_table(results)
        self._show_info("Verificador de ciclos", f"Errores encontrados: {len(results)}")

    def _update_results_header(self, mode: str, count: int) -> None:
        self.results_title.setText(mode)
        self.badge_label.setText(str(count))
        self.badge_widget.setVisible(True)
        color = "#16a34a" if count == 0 else "#dc2626"
        self.badge_widget.setStyleSheet(
            f"QWidget#BadgeWidget {{ background: {color}; border-radius: 10px; }}"
        )

    def _show_info(self, title: str, message: str) -> None:
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()

    def _adjust_missing_column_width(self) -> None:
        missing_idx = ERROR_HEADERS.index("Columnas faltantes")
        header_item = self.table.horizontalHeaderItem(missing_idx)
        if header_item is None:
            return
        metrics = self.table.fontMetrics()
        target_width = metrics.horizontalAdvance(header_item.text()) + 32
        if self.table.columnWidth(missing_idx) < target_width:
            self.table.setColumnWidth(missing_idx, target_width)

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

        self.table.horizontalHeader().resizeSections(
            QHeaderView.ResizeMode.ResizeToContents
        )
        self._adjust_missing_column_width()
        if was_sorting:
            self.table.setSortingEnabled(True)
