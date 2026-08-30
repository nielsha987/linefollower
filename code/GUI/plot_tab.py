# gui_app/run_plot_tab.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QListWidget, QPushButton, QListWidgetItem,
    QMessageBox, QSizePolicy
)
from PyQt6.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
import csv
import sqlite3
from datetime import datetime
import os
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT as NavigationToolbar


class RunPlotTab(QWidget):
    def __init__(self, db_path="robot_data.db"):
        super().__init__()
        self.db_path = db_path
        self.initUI()
        self.data_cache = []

    def initUI(self):
        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # --- Filter sectie ---
        filter_layout = QHBoxLayout()

        # Run selectie
        run_layout = QVBoxLayout()
        run_label = QLabel("Selecteer Run(s):")
        self.run_list = QListWidget()
        self.run_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.run_list.itemSelectionChanged.connect(self.update_plot)
        run_layout.addWidget(run_label)
        run_layout.addWidget(self.run_list)

        # Sensor selectie
        sensor_layout = QVBoxLayout()
        sensor_label = QLabel("Selecteer sensoren:")
        self.sensor_list = QListWidget()
        self.sensor_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.sensor_list.itemSelectionChanged.connect(self.update_plot)
        sensor_layout.addWidget(sensor_label)
        sensor_layout.addWidget(self.sensor_list)

        # Voeg toe met verhoudingen
        filter_layout.addLayout(run_layout, stretch=1)
        filter_layout.addLayout(sensor_layout, stretch=1)

        layout.addLayout(filter_layout, stretch=1)

        # --- Plot sectie ---
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)
        self.canvas.setMinimumHeight(300)

        # Toolbar toevoegen voor zoom/pan
        self.toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas, stretch=3)

        # --- Knoppen sectie ---
        btn_layout = QHBoxLayout()

        self.export_btn = QPushButton("Export CSV")
        self.export_btn.clicked.connect(self.export_csv)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: black;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """)

        self.delete_btn = QPushButton("Delete Run(s)")
        self.delete_btn.clicked.connect(self.delete_selected_runs)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: red;
                color: white;
                font-weight: bold;
                padding: 12px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
        """)

        # Zorg dat ze zich horizontaal uitrekken
        self.export_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.delete_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Voeg toe met gelijke stretch
        btn_layout.addWidget(self.export_btn, stretch=1)
        btn_layout.addWidget(self.delete_btn, stretch=1)

        layout.addLayout(btn_layout, stretch=0)

        # --- Data laden ---
        self.load_sensors()
        self.load_runs()

        

    def load_sensors(self):
        """Laad alle unieke sensor namen uit DB"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT name FROM sensor_data ORDER BY name")
        sensors = [r[0] for r in cursor.fetchall()]
        self.sensor_list.clear()
        for s in sensors:
            item = QListWidgetItem(s)
            item.setSelected(True)  # standaard allemaal geselecteerd
            self.sensor_list.addItem(item)
        conn.close()

    def query_data(self):
        """Haal data op voor de geselecteerde runs en sensoren"""
        selected_runs = [i.text() for i in self.run_list.selectedItems()]
        selected_sensors = [i.text() for i in self.sensor_list.selectedItems()]
        
        if not selected_runs or not selected_sensors:
            return []  # niets geselecteerd

        placeholders_runs = ",".join("?" for _ in selected_runs)
        placeholders_sensors = ",".join("?" for _ in selected_sensors)

        query = f"""
            SELECT timestamp, name, value
            FROM sensor_data
            WHERE run_id IN ({placeholders_runs})
            AND name IN ({placeholders_sensors})
            ORDER BY timestamp
        """

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(query, selected_runs + selected_sensors)
        rows = cursor.fetchall()
        conn.close()

        self.data_cache = rows
        return rows

    def update_plot(self):
        rows = self.query_data()
        self.ax.clear()

        if not rows:
            self.canvas.draw()
            return

        # groepeer per naam
        series = {}
        for ts, name, val in rows:
            series.setdefault(name, []).append((ts, val))

        for name, points in series.items():
            ts, vals = zip(*points)
            self.ax.plot(ts, vals, label=name)

        self.ax.set_xlabel("Timestamp")
        self.ax.set_ylabel("Value")
        self.ax.legend()
        self.ax.grid(True)
        self.canvas.draw()

    def export_csv(self):
        output_folder = "csv_files"
        os.makedirs(output_folder, exist_ok=True)

        if not self.data_cache:
            return

        now = datetime.now()
        filename = now.strftime("robot_data_%Y%m%d_%H%M%S.csv")  # bv robot_data_20251108_223012.csv
        filepath = os.path.join(output_folder, filename)
        with open(filepath, "w", newline="") as f:  # gebruik filepath, niet filename
            writer = csv.writer(f)
            writer.writerow(["timestamp", "name", "value"])
            for row in self.data_cache:
                writer.writerow(row)

        print(f"Exported to {filepath}")


    def load_runs(self):
        """Laad alle unieke run_id's uit DB"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT run_id FROM sensor_data ORDER BY run_id")
        runs = [str(r[0]) for r in cursor.fetchall()]  # run_id naar string
        self.run_list.clear()
        for r in runs:
            item = QListWidgetItem(r)
            item.setSelected(True)  # standaard allemaal geselecteerd
            self.run_list.addItem(item)
        conn.close()

    def delete_selected_runs(self):
        selected_items = self.run_list.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Info", "Geen runs geselecteerd.")
            return

        run_ids = [item.text() for item in selected_items]

        # Bevestiging
        reply = QMessageBox.question(
            self,
            "Confirm",
            f"deze run(s) verwijderen?\n\n{', '.join(run_ids)}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for run_id in run_ids:
            cursor.execute("DELETE FROM sensor_data WHERE run_id = ?", (run_id,))

        conn.commit()
        conn.close()

        # Herladen lijst
        self.load_runs()

        QMessageBox.information(self, "Klaar", f"Verwijderd: {len(run_ids)} runs.")
