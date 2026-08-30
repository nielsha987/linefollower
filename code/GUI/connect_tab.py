# gui_app/connect_tab.py
import serial.tools.list_ports
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from bluetooth_manager import BluetoothManager


class ConnectTab(QWidget):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.bt_manager = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Poortselectie
        port_layout = QHBoxLayout()
        self.port_combo = QComboBox()
        self.refresh_ports()
        
        
        port_layout.addWidget(QLabel("COM-poort:"))
        port_layout.addWidget(self.port_combo)
        

        # Connectieknoppen
        btn_layout = QHBoxLayout()
        self.connect_btn = QPushButton("Verbinden")
        self.disconnect_btn = QPushButton("Verbreken")

        # ---- Vergroot de knoppen ----
        font_btn = QFont()
        font_btn.setPointSize(14)  # grotere letters
        self.connect_btn.setFont(font_btn)
        self.disconnect_btn.setFont(font_btn)
        self.connect_btn.setMinimumHeight(100)
        self.disconnect_btn.setMinimumHeight(100)

        self.connect_btn.clicked.connect(self.connect_device)
        self.disconnect_btn.clicked.connect(self.disconnect_device)
        btn_layout.addWidget(self.connect_btn)
        btn_layout.addWidget(self.disconnect_btn)

        # Statuslabel
        self.status_label = QLabel("Niet verbonden")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # ---- Vergroot de status ----
        font_label = QFont()
        font_label.setPointSize(11)  # grotere letters
        font_label.setBold(True)
        self.status_label.setFont(font_label)
        self.status_label.setMinimumHeight(100)

        self._start_status_timer()

        layout.addLayout(port_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(self.status_label)
        self.setLayout(layout)

    def refresh_ports(self):
        """Zoekt alle beschikbare seriële poorten."""
        self.port_combo.clear()
        ports = serial.tools.list_ports.comports()
        for port in ports:
            self.port_combo.addItem(port.device)
        if not ports:
            self.port_combo.addItem("Geen poorten gevonden")

    def connect_device(self):
        """Start connectie met de geselecteerde poort."""
        port = self.port_combo.currentText()
        if "Geen" in port:
            self.status_label.setText("Geen poort geselecteerd")
            return

        self.bt_manager = BluetoothManager(port=port)
        self.bt_manager.data_callback = self.data_manager.on_raw_data
        success = self.bt_manager.connect()
        if success:
            self.data_manager.attach_bluetooth(self.bt_manager)
            self.status_label.setText(f"Verbonden met {port}")
        else:
            self.status_label.setText("Verbinding mislukt")

    def disconnect_device(self):
        if self.bt_manager:
            try:
                self.bt_manager._handle_disconnect()
            except Exception as e:
                print("Fout bij verbreken:", e)

            self.data_manager.bt = None
            self.bt_manager = None
            self.status_label.setText("Verbinding verbroken")

    def on_data(self, parsed):
        """Callback bij nieuwe data (voor later grafiek of DB)."""
        print("GUI ontving data:", parsed)

    def _start_status_timer(self):
        from PyQt6.QtCore import QTimer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_status)
        self.timer.start(500)  # update elke 0.5 seconden

    def _update_status(self):
        bt = self.data_manager.bt  # jouw BluetoothManager
        if bt and hasattr(bt, "connected") and bt.connected:
            self.status_label.setText("Verbonden")
           
        else:
            self.status_label.setText("Verbinding verbroken")
            
