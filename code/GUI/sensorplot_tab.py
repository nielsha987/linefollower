# APP/sensor_plot_tab.py
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton , QSizePolicy, QRadioButton
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtCore import Qt, pyqtSignal
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle




class SensorPlotTab(QWidget):
    sendData = pyqtSignal(dict)

    def __init__(self, num_sensors=8, max_value=4096):
         
        super().__init__()
        self.vorige_telem_status = True
        self.num_sensors = num_sensors
        self.max_value = max_value
        self.sensor_values = [0] * self.num_sensors

        # ---- Matplotlib setup ----
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.fig)

        # Sensorbalken
        self.bars = self.ax.bar(
            range(1, num_sensors + 1),
            self.sensor_values,
            color='white', width=0.983, align='edge'
        )

        # Lijnpositie
        self.position = None  
        self.position_line = self.ax.axvline(
            x=0, color='red', linewidth=2, linestyle='--', visible=False
        )

        # As en labels
        self.ax.set_ylim(0, max_value)
        self.ax.get_yaxis().set_visible(False)
        self.ax.get_xaxis().set_visible(False)
        for spine in self.ax.spines.values():
            spine.set_visible(False)

        self.labels = [
            self.ax.text(i + 0.5, -max_value * 0.05, '0',
                         ha='center', va='top', color='black', fontsize=10)
            for i in range(1, num_sensors + 1)
        ]

        # Tekst voor positie en output
        self.position_text = self.ax.text(
            0, self.max_value * 1.05, '',
            color='red', fontsize=10, ha='center', va='bottom'
        )

        self.output_test = self.ax.text(
            0, self.max_value * 1.075, '',
            color='black', fontsize=10, ha='center', va='bottom'
        )

        # ---- Buttons ----
        self.calibrate_buttonWhite = QPushButton("Kalibreer wit")
        self.calibrate_buttonWhite.setStyleSheet(
            "background-color: white; color: black; font-weight: bold; padding: 8px;"
        )
        self.calibrate_buttonWhite.clicked.connect(self.calibrate_sensors_white)

        self.calibrate_buttonBlack = QPushButton("Kalibreer zwart")
        self.calibrate_buttonBlack.setStyleSheet(
            "background-color: black; color: white; font-weight: bold; padding: 8px;"
        )
        self.calibrate_buttonBlack.clicked.connect(self.calibrate_sensors_black)



        
        self.radio_button= QRadioButton("Telementrie Aan")
        self.radio_button.toggled.connect(self.verzend_telemetrie_status)
        self.radio_button.setChecked(True)
        # ---- Layouts ----
        # Horizontale rij knoppen
        h_layout = QHBoxLayout()
        h_layout.addWidget(self.calibrate_buttonWhite)
        h_layout.addWidget(self.calibrate_buttonBlack)
       
        h_layout.addWidget(self.radio_button)
        # Zorg dat de knoppen niet meerekken
        for btn in [self.calibrate_buttonWhite, self.calibrate_buttonBlack, self.radio_button]:
            btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        # Canvas mag uitbreiden
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Hoofd-layout
        # Hoofd-layout
        layout = QVBoxLayout()
        layout.addWidget(self.canvas, stretch=5)  # grafiek krijgt meeste ruimte
        layout.addLayout(h_layout, stretch=1)     # knoppen kleiner deel
        self.setLayout(layout)

        

    # ---------------- Update functies ----------------
    def update_values(self, data):
        """Update sensorwaarden (dict of tuple)"""
        if isinstance(data, tuple) and len(data) == 2:
            key, val = data
            if key.startswith("DP_"):
                idx = int(key.split("_")[1]) - 1
                if 0 <= idx < self.num_sensors:
                    self.sensor_values[idx] = val
        elif isinstance(data, dict):
            for key, val in data.items():
                if key.startswith("DP_"):
                    idx = int(key.split("_")[1]) - 1
                    if 0 <= idx < self.num_sensors:
                        self.sensor_values[idx] = val

        # Update grafiek
        
        for i, val in enumerate(self.sensor_values):
            self.bars[i].set_height(val)
            intensity = val / self.max_value
            intensity = min(max(intensity, 0), 1)
            self.bars[i].set_color((1-intensity, 1-intensity, 1-intensity))
            self.labels[i].set_text(str(val))

        self.canvas.draw_idle()
    
    def update_position(self, position):
        if position is None:
            self.position_line.set_visible(False)
            self.position_text.set_visible(False)
            self.canvas.draw_idle()
            return

        self.position = position
        x_center = (position /7.5) + 5  # schaal en verschuiving
        self.position_line.set_xdata([x_center, x_center])
        self.position_line.set_visible(True)
        self.position_text.set_text(f"{position:.2f}")
        self.position_text.set_x(x_center)
        self.position_text.set_visible(True)
        self.canvas.draw_idle()

    def update_output(self, output):
        value = max(0, min(output, 100))  # limiet 0-100%
        height = value / 100  # fraction van de axes hoogte


        self.output_test.set_text(f"Output: {output:.2f}")
        self.output_test.set_x((self.num_sensors / 2) + 0.5)

        self.canvas.draw_idle()


    # ---------------- Knoppen ----------------
    def calibrate_sensors_white(self):
        msg = {"calib": "white"}
        self.sendData.emit(msg)
        print("Kalibratiecommando verzonden:", msg)

    def calibrate_sensors_black(self):
        msg = {"calib": "black"}
        self.sendData.emit(msg)
        print("Kalibratiecommando verzonden:", msg)



    def verzend_telemetrie_status(self, nieuwe_status):
        """
        Deze functie wordt één keer aangeroepen wanneer de radiobutton van
        status verandert (flankdetectie via het .toggled signaal).
        """
        
        if nieuwe_status != self.vorige_telem_status:
            
            if nieuwe_status:
                # 🟢 Stijgende Flank (False -> True)
                msg = {"telem": "true"}
                print("Telementrie AAN (flank) verzonden:", msg)
            else:
                # 🔴 Dalende Flank (True -> False)
                msg = {"telem": "false"}
                print("Telementrie UIT (flank) verzonden:", msg)

            # Emitteren van het bericht
            self.sendData.emit(msg)
            
            # 💡 UPDATE: Stel de vorige status in op de nieuwe status voor de volgende verandering
            self.vorige_telem_status = nieuwe_status
