import sys
import os
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QMainWindow, QTabWidget
from connect_tab import ConnectTab
from sensorplot_tab import SensorPlotTab
from motor_tab import MotorTab
from plot_tab import RunPlotTab

class MainWindow(QMainWindow):
    def __init__(self, data_manager):
        super().__init__()

        self.setWindowTitle("Mijn App")

        # Icon
        base_path = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(base_path, "assets", "icon.ico")
        self.setWindowIcon(QIcon(icon_path))  
        
        self.setWindowTitle("LineFollow Configurator")
        self.setGeometry(200, 200, 800, 600)

        self.data_manager = data_manager

        self.tabs = QTabWidget()
        
        self.connect_tab = ConnectTab(self.data_manager)

        self.sensor_tab = SensorPlotTab()
        self.sensor_tab.sendData.connect(self.data_manager.send_to_esp)
        
        self.data_manager.sensor_callback = self.sensor_tab.update_values
        self.data_manager.position_callback = self.sensor_tab.update_position 
        self.data_manager.output_callback = self.sensor_tab.update_output

        self.motor_tab = MotorTab()
        self.motor_tab.sendData.connect(self.data_manager.send_to_esp)
        
        self.data_manager.pid_callback = self.motor_tab.update_pid
        self.data_manager.speed_callback = self.motor_tab.update_speed 
        self.data_manager.interval_callback = self.motor_tab.update_interval
        self.data_manager.filter_callback = self.motor_tab.update_filter
        self.data_manager.contrast_callback = self.motor_tab.update_contrast

        self.plot_tab = RunPlotTab()

        # print("sensor_callback set?", self.data_manager.sensor_callback is not None)
        self.tabs.addTab(self.connect_tab, "Connectie")
        self.tabs.addTab(self.sensor_tab, "Sensoren")
        self.tabs.addTab(self.motor_tab, "Settings")
        self.tabs.addTab(self.plot_tab, "Plot")
        self.setCentralWidget(self.tabs)
        
        # Koppel DataManager -> SensorPlotTab
        

        
     
