# gui_app/motor_tab.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSlider,
    QDoubleSpinBox, QPushButton,QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer

KEY_STYLE_NORMAL = """
    QPushButton {
        background-color: #303030; 
        color: white; 
        border: 2px solid #505050; 
        min-width: 40px; 
        min-height: 40px;
        font-weight: bold;
        border-radius: 5px;
    }
"""

# CSS-stijl voor ingedrukte toetsen
KEY_STYLE_PRESSED = """
    QPushButton {
        background-color: #4CAF50; /* Groen */
        color: white;
        border: 2px solid #388E3C;
        min-width: 40px;
        min-height: 40px;
        font-weight: bold;
        border-radius: 5px;
    }
"""

class MotorTab(QWidget):
    sendData = pyqtSignal(dict)  # signaal dat dict naar DataManager stuurt

    def __init__(self):
        super().__init__()
        self.initUI()
        self.motor_data = [[], []]
        self.pressed_keys = set()
        self.keyboard_speed = 255
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def initUI(self):
        main_layout = QVBoxLayout(self)
        self.setLayout(main_layout)

        # --- Snelheid slider bovenaan ---
        speed_container = QWidget()
        speed_layout = QVBoxLayout(speed_container)
        speed_layout.addWidget(QLabel("<b>Speed Settings</b>"))

        # Opmerking: Voor speed en interval gebruiken we geen SpinBox omdat dit Int-waarden zijn.
        self.speed_slider, self.speed_label = self._make_slider("Speed", speed_layout, 0, 255, 1, 0, use_spinbox=False)
        self.speed_slider.setToolTip("Stel hier de maximale motorsnelheid in")
        self.interval_slider, self.interval_label = self._make_slider("Diff", speed_layout, 0, 2000, 1, 0, use_spinbox=False)
        self.interval_slider.setToolTip("Zet hier de tijdsinterval in microseconden")
        main_layout.addWidget(speed_container)

        
        # --- PID tuning sectie ---
        pid_container = QWidget()
        pid_layout = QVBoxLayout(pid_container)
        pid_layout.addWidget(QLabel("<b>PID Tuning</b>"))
        
        # Gebruik de aangepaste _make_slider methode voor PID (met SpinBox)
        self.kp_slider, self.kp_label, self.kp_spinbox = self._make_slider("Kp", pid_layout, 0, 2000, 100, 2, use_spinbox=True)
        self.ki_slider, self.ki_label, self.ki_spinbox = self._make_slider("Ki", pid_layout, 0, 2000, 100, 2, use_spinbox=True)
        self.kd_slider, self.kd_label, self.kd_spinbox = self._make_slider("Kd", pid_layout, 0, 2000, 100, 2, use_spinbox=True)
        
        # --- fillter sectie ---
        filter_container = QWidget()
        filter_layout = QVBoxLayout(filter_container)
        filter_layout.addWidget(QLabel("<b>Filter Settings</b>"))

        self.filter_slider, self.filter_label, self.filter_spinbox = self._make_slider("Filter", filter_layout, 0, 100, 100, 2, use_spinbox=True)
       
        filter_container.setToolTip("Stel hier de waarde in voor de low-pass filter\nOm ruis in de positie te verminderen.\nLagere waarden betekenen meer filtering.")
                # --- fillter sectie ---
        geenLijn_container = QWidget()
        geenLijn_layout = QVBoxLayout(geenLijn_container)
        geenLijn_layout.addWidget(QLabel("<b>Geen Lijn detectie</b>"))
        geenLijn_container.setToolTip(
        "Stel het minimale contrast tussen de hoogste \nen de laagste waard in."
        "\nLagere contrast waarden maken de detectie toleranter")
        self.geenLijn_slider, self.geenLijn_label = self._make_slider("contrast", geenLijn_layout, 0, 4095, 1, 0, use_spinbox=False)
        main_layout.addWidget(geenLijn_container)
        main_layout.addWidget(filter_container)
        # 1. Send Setting Knop (over de hele breedte)
        self.send_button = QPushButton("Send Setting")
        self.send_button.clicked.connect(self.send_settings)
        self.send_button.setStyleSheet( "background-color: black; color: white; font-weight: bold; padding: 8px;")

        # 2. Container voor Start/Stop (QHBoxLayout)
        run_stop_container = QWidget()
        run_stop_layout = QHBoxLayout(run_stop_container)
        run_stop_layout.setContentsMargins(0, 0, 0, 0)
        
        self.buttonRun = QPushButton("Start")
        self.buttonRun.setStyleSheet(
            "background-color: lightgreen; color: white; font-weight: bold; padding: 8px;"
        )
        self.buttonRun.clicked.connect(self.send_run)
        
        self.buttonStop = QPushButton("Stop")
        self.buttonStop.setStyleSheet(
            "background-color: red; color: white; font-weight: bold; padding: 8px;"
        )
        self.buttonStop.clicked.connect(self.send_stop)
        
        run_stop_layout.addWidget(self.buttonRun)
        run_stop_layout.addWidget(self.buttonStop)
        pid_layout.addWidget(self.send_button)
        pid_layout.addWidget(run_stop_container)
        
        main_layout.addWidget(pid_container)
        
        # --- Test Motor sectie ---
        TestMotor_container = QWidget()
        TestMotor_layout = QVBoxLayout(TestMotor_container)
        TestMotor_layout.addWidget(QLabel("<b>Manueel Controle</b>"))

        # ----------------------------------------------------
        # Nieuwe Lay-out voor de ZQSD knoppen
        # Z
        # Q S D
        # ----------------------------------------------------
        
        keyboard_layout = QVBoxLayout()
        keyboard_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Rijs 1: Z
        row1 = QHBoxLayout()
        # VERWIJDER: row1.addStretch() - Verwijder deze om de "Z" niet volledig uit te rekken
        
        # Optioneel: voeg een spacer toe om Z iets naar het midden te duwen,
        # maar behoud de compactheid van de rij.
        row1.addSpacing(45) # 45 pixels om Z boven S te krijgen (40px knop + 5px spacing)
        
        self.key_z = QPushButton("Z")
        self.key_z.setStyleSheet(KEY_STYLE_NORMAL)
        self.key_z.setFixedSize(40, 40)
        row1.addWidget(self.key_z)
        
        # Voeg stretch toe aan het einde zodat de knop links blijft
        row1.addStretch() 
        
        # ZET DE AFSTAND TUSSEN ITEMS OP 5 (voor een kleine marge) of 0 (voor tegen elkaar)
        row1.setSpacing(5) 
        keyboard_layout.addLayout(row1)

        # Rijs 2: Q S D
        row2 = QHBoxLayout()
        
        self.key_q = QPushButton("Q")
        self.key_q.setStyleSheet(KEY_STYLE_NORMAL)
        self.key_q.setFixedSize(40, 40)
        
        self.key_s = QPushButton("S")
        self.key_s.setStyleSheet(KEY_STYLE_NORMAL)
        self.key_s.setFixedSize(40, 40)

        self.key_d = QPushButton("D")
        self.key_d.setStyleSheet(KEY_STYLE_NORMAL)
        self.key_d.setFixedSize(40, 40)

        row2.addWidget(self.key_q)
        row2.addWidget(self.key_s)
        row2.addWidget(self.key_d)
        
        # VOEG EEN STRETCH TOE ZODAT DE KNOPPEN NAAR LINKS WORDEN GEDUWD
        row2.addStretch() 
        
        # ZET DE AFSTAND TUSSEN ITEMS OP 5 (voor een kleine marge) of 0 (voor tegen elkaar)
        row2.setSpacing(5) 
        keyboard_layout.addLayout(row2)
       

        # Huidige status label (wordt behouden voor de motorwaarden)
        # self.status_label = QLabel("M1=0, M2=0")
        # self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        TestMotor_layout.addLayout(keyboard_layout)
        #TestMotor_layout.addWidget(self.status_label)

        main_layout.addWidget(TestMotor_container)
        
        # --- Extra stretch als er ruimte over is ---
        main_layout.addStretch()



    # --- Motor Controls ---
    def update_keyboard_display(self):
        """Werkt de styling van de ZQSD knoppen bij op basis van ingedrukte toetsen."""
        
        # Mapping van Qt Key naar de QPushButton instantie
        key_map = {
            Qt.Key.Key_Z: self.key_z,
            Qt.Key.Key_Q: self.key_q,
            Qt.Key.Key_S: self.key_s,
            Qt.Key.Key_D: self.key_d,
        }
        
        for key, button in key_map.items():
            if key in self.pressed_keys:
                button.setStyleSheet(KEY_STYLE_PRESSED)
                # print(f"Button {button.text()} pressed")
            else:
                button.setStyleSheet(KEY_STYLE_NORMAL)

    def sendMotor(self, motor, value):
        data = {"motor": motor, "value": value}
        # print("Sending:", data)
        self.sendData.emit(data)

    def _make_slider(self, name, parent_layout, min_val, max_val, scale, decimals=2, use_spinbox=True):
        """
        Maakt een QLabel, QSlider en optioneel een QDoubleSpinBox.
        Retourneert: (slider, label) of (slider, label, spinbox)
        """
        # --- Hoofd layout voor rij ---
        row_container = QWidget()
        row_layout = QHBoxLayout(row_container)
        row_layout.setContentsMargins(0, 0, 0, 0)
        
        fmt = f"{{:.{decimals}f}}"
        
        # --- Label aanmaken ---
        # Beginwaarde berekenen
        initial_value_scaled = 0 / scale
        lbl = QLabel(f"{name}: {fmt.format(initial_value_scaled)}")
        row_layout.addWidget(lbl)
        
        # --- Slider aanmaken ---
        sld = QSlider(Qt.Orientation.Horizontal)
        sld.setRange(min_val, max_val)
        sld.setValue(0)
        row_layout.addWidget(sld)
        
        spinbox = None
        
        if use_spinbox:
            # --- SpinBox aanmaken ---
            spinbox = QDoubleSpinBox()
            spinbox.setRange(min_val / scale, max_val / scale)
            spinbox.setDecimals(decimals)
            spinbox.setSingleStep(1 / scale) # 0.01 voor scale=100
            spinbox.setValue(initial_value_scaled)
            row_layout.addWidget(spinbox)

            # --- Synchronisatie Functies ---
            
            def slider_to_spinbox(v, s=scale, sp=spinbox, l=lbl):
                """Update SpinBox en Label vanuit Slider."""
                # Verbreek tijdelijk de verbinding van de SpinBox om recursie te voorkomen
                sp.blockSignals(True) 
                
                float_value = v / s
                sp.setValue(float_value)
                l.setText(f"{name}: {fmt.format(float_value)}")
                
                sp.blockSignals(False) # Herstel de verbinding


            def spinbox_to_slider(v, s=scale, sl=sld, l=lbl):
                """Update Slider en Label vanuit SpinBox."""
                # Verbreek tijdelijk de verbinding van de Slider om recursie te voorkomen
                sl.blockSignals(True)
                
                int_value = int(round(v * s)) # Gebruik round() voor betere precisie
                sl.setValue(int_value)
                l.setText(f"{name}: {fmt.format(v)}")
                
                sl.blockSignals(False) # Herstel de verbinding
                
            # Verbind de functies
            sld.valueChanged.connect(slider_to_spinbox)
            spinbox.valueChanged.connect(spinbox_to_slider)
            
            parent_layout.addWidget(row_container)
            return sld, lbl, spinbox # Retourneer spinbox

        else:
            # Alleen Slider & Label (voor Speed/Interval)
            sld.valueChanged.connect(
                lambda v, n=name, l=lbl, f=fmt, s=scale: l.setText(f"{n}: {f.format(v/s)}")
            )
            
            parent_layout.addWidget(row_container)
            return sld, lbl # Retourneer zonder spinbox

    def send_settings(self):

        original_style = "background-color: black; color: white; font-weight: bold; padding: 8px;"
        feedback_style = "background-color: gray; color: white; font-weight: bold; padding: 8px;" # Groen voor succes

        self.send_button.setStyleSheet(feedback_style)
        self.send_button.setText("Sending...")

        self.send_button.setEnabled(False)

        pid_data = {
            "pid": {
                "kp": self.kp_slider.value() / 100.0,
                "ki": self.ki_slider.value() / 100.0,
                "kd": self.kd_slider.value() / 100.0,
            }
        }
        print("Send PID:", pid_data)
        self.sendData.emit(pid_data)

        print("Send Speed", {"speed": self.speed_slider.value()})
        self.sendData.emit({"speed": self.speed_slider.value()})
        
        print("send Interval", {"interval": self.interval_slider.value()})
        self.sendData.emit({"interval": self.interval_slider.value()})

        print("send Filter", {"filter": self.filter_slider.value()/100.0})
        self.sendData.emit({"filter": self.filter_slider.value()})  

        print("send Contrast", {"contrast": self.geenLijn_slider.value()})  
        self.sendData.emit({"contrast": self.geenLijn_slider.value()})

        QTimer.singleShot(500, self.reset_send_button)

    def keyPressEvent(self, event):
        if event.isAutoRepeat():
            return  # <---- negeer automatische herhalingen

        key = event.key()
        if key in (Qt.Key.Key_Z, Qt.Key.Key_Q, Qt.Key.Key_S, Qt.Key.Key_D):
            if key not in self.pressed_keys:
                self.pressed_keys.add(key)
                self.update_keyboard_drive()
                self.update_keyboard_display() # <-- Update de visuele weergave

    def keyReleaseEvent(self, event):

        if event.isAutoRepeat():
            return  # <

        key = event.key()
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
            self.update_keyboard_drive()
            self.update_keyboard_display() # <-- Update de visuele weergave

    def update_keyboard_drive(self):
        s = self.keyboard_speed
        left = 0
        right = 0

        if Qt.Key.Key_Z in self.pressed_keys:
            left += s
            right += s
        if Qt.Key.Key_S in self.pressed_keys:
            left -= s
            right -= s
        if Qt.Key.Key_Q in self.pressed_keys:
            left -= s // 2
            right += s // 2
        if Qt.Key.Key_D in self.pressed_keys:
            left += s // 2
            right -= s // 2

        left = max(-127, min(127, left))
        right = max(-127, min(127, right))

        self.sendData.emit({"motor": 1, "value": left})
        self.sendData.emit({"motor": 2, "value": -right})
        #self.status_label.setText(f"ZQSD → M1={left}, M2={right}")

        if not self.pressed_keys:
            self.sendData.emit({"motor": 1, "value": 0})
            self.sendData.emit({"motor": 2, "value": 0})
            #self.status_label.setText("M1=0, M2=0")

    def on_speed_change(self, value):
        self.speed_label.setText(f"Speed: {value}")
        
    def update_pid(self, pid: dict):
        """Werk PID-sliders en labels bij vanuit ontvangen JSON."""
        # De update functie moet nu ook de SpinBox bijwerken
        if "kp" in pid:
            value = pid["kp"]
            self.kp_slider.setValue(int(value * 100))
            self.kp_label.setText(f"Kp: {value:.2f}")
            self.kp_spinbox.setValue(value) # Spinbox bijwerken
        if "ki" in pid:
            value = pid["ki"]
            self.ki_slider.setValue(int(value * 100))
            self.ki_label.setText(f"Ki: {value:.2f}")
            self.ki_spinbox.setValue(value) # Spinbox bijwerken
        if "kd" in pid:
            value = pid["kd"]
            self.kd_slider.setValue(int(value * 100))
            self.kd_label.setText(f"Kd: {value:.2f}")
            self.kd_spinbox.setValue(value) # Spinbox bijwerken

    def update_speed(self, value: int):
        """Werk speed-slider en label bij vanuit ontvangen JSON."""
        self.speed_slider.setValue(value)
        self.speed_label.setText(f"Speed: {value}")
        
    def update_interval(self, value: int):
        """Werk interval-slider en label bij vanuit ontvangen JSON."""
        self.interval_slider.setValue(value)
        self.interval_label.setText(f"Interval (µs): {value}")
 
    def on_interval_chang(self, value: int):
        self.interval_label.setText(f"Interval (µs): {value}")

    def send_run(self):
        msg = {"run": "true"}
        self.sendData.emit(msg)
        print("runcommando:", msg)

    def send_stop(self):
        msg = {"run": "false"}
        self.sendData.emit(msg)
        print("stopcommando:", msg)
        msg = {"motor": 1, "value": 0}
        self.sendData.emit(msg)
        print("stopcommando:", msg)
        msg = {"motor": 2, "value": 0}
        self.sendData.emit(msg)
        print("stopcommando:", msg)

    def reset_send_button(self):
        # Herstel de oorspronkelijke stijl en tekst
        original_style = "background-color: black; color: white; font-weight: bold; padding: 8px;"
        self.send_button.setStyleSheet(original_style)
        self.send_button.setText("Send Setting")
        self.send_button.setEnabled(True)

    def update_filter(self, value: int):
        """Werk filter-slider en label bij vanuit ontvangen JSON."""
        value =int(value * 100)
        self.filter_slider.setValue(value)
        self.filter_label.setText(f"Filter: {value}")

    def update_contrast(self, value: int):
        """Werk contrast-slider en label bij vanuit ontvangen JSON."""
       
        self.geenLijn_slider.setValue(value)
        self.geenLijn_label.setText(f"contrast: {value}")


    
