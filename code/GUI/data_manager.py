# data_manager.py
import threading
import time
from json_parser import parse_json
from database import init_db, insert_sensor_data , start_new_run

class DataManager:
    def __init__(self, bluetooth_manager=None, db_path="robot_data.db", on_new_data=None, store_to_db=True):
        """
        bluetooth_manager: BluetoothManager of None
        db_path: pad naar sqlite file
        on_new_data: callback(dict) voor GUI updates
        """
        self.bt = bluetooth_manager
        self.db_path = db_path
        self.on_new_data = on_new_data
        self.store_to_db = store_to_db

        self.buffer = ""
        self.lock = threading.Lock()
        self.sensor_callback = None
        self.pid_callback = None
        self.speed_callback = None
        self.position_callback = None
        self.output_callback = None
        # init DB
        init_db()  # gebruikt DB_PATH of maak init_db(db_path) als je dat wil
        self.current_run = start_new_run() # start nieuwe run in DB
        # als bluetooth manager reeds gegeven is, koppel callback
        if self.bt is not None:
            self.bt.data_callback = self.on_raw_data

    def attach_bluetooth(self, bluetooth_manager):
        """Koppel BluetoothManager later (bijv. vanuit ConnectTab)."""
        self.bt = bluetooth_manager
        self.bt.data_callback = self.on_raw_data

    def on_raw_data(self, raw_text):
        """Callback voor ruwe tekst van BluetoothManager."""
        with self.lock:
            self.buffer += raw_text
            parsed_list, self.buffer = parse_json(self.buffer)

        for parsed in parsed_list:
            self. handle_sensor_dict(parsed)

    def handle_sensor_dict(self, sensor_dict):
        """
        Verwerk inkomend dict:
        - DP_ sensoren
        - PID
        - speed
        - position
        - output
        Sla op in DB met huidige run_id
        """
        #print(f"Binnenkomende dictionary: {sensor_dict}")
        # Voeg hier een loop toe om alle types te controleren
        #for key, value in sensor_dict.items():
        #    print(f"Key: {key}, Waarde: {value}, Type: {type(value)}")

        # --- DP_ sensoren ---
        data = {k: v for k, v in sensor_dict.items() if k.startswith("DP_")}
        timestamp = sensor_dict.get("time", int(time.time() * 1000))

        if self.store_to_db and data:
            for k, v in data.items():
                try:
                    v_int = int(v) 
                    insert_sensor_data(self.current_run, k, v_int, timestamp)
                except ValueError:
                    # Optioneel: log de fout als v geen geldig nummer is
                    print(f"Waarde {v} voor sensor {k} is geen geldig getal.")

        if self.sensor_callback:
            if len(data) == 1:
                key, val = next(iter(data.items()))
                self.sensor_callback((key, val))
            elif len(data) > 1:
                self.sensor_callback(data)

        # --- PID ---
        if "pid" in sensor_dict:
            pid = sensor_dict["pid"]
            if self.pid_callback:
                self.pid_callback(pid)
            # optioneel: sla PID ook op in DB
            if self.store_to_db:
                for k, v in pid.items():
                    insert_sensor_data(self.current_run, k, v, timestamp)

        # --- Speed ---
        if "speed" in sensor_dict:
            speed = sensor_dict["speed"]
            if self.speed_callback:
                self.speed_callback(speed)
            if self.store_to_db:
                insert_sensor_data(self.current_run, "speed", speed, timestamp)

        # --- Position ---
        if "position" in sensor_dict:
            pos = sensor_dict["position"]
            if self.position_callback:
                self.position_callback(pos)
            if self.store_to_db:
                insert_sensor_data(self.current_run, "position", pos, timestamp)

        # --- Output ---
        if "output" in sensor_dict:
            out = sensor_dict["output"]
            if self.output_callback:
                self.output_callback(out)
            if self.store_to_db:
                insert_sensor_data(self.current_run, "output", out, timestamp)
   
        if "interval" in sensor_dict:
            interval = sensor_dict["interval"]
            if self.interval_callback:
                self.interval_callback(interval)
            if self.store_to_db:
                insert_sensor_data(self.current_run, "interval", interval, timestamp)
        
        if "filter" in sensor_dict:
            print("Filter value received:", sensor_dict["filter"])
            filter_val = sensor_dict["filter"]
            if self.filter_callback:
                print("Calling filter_callback with value:", filter_val)
                self.filter_callback(filter_val)

        if "contrast" in sensor_dict:
            contrast = sensor_dict["contrast"]
            if self.contrast_callback:
                self.contrast_callback(contrast)
            if self.store_to_db:
                insert_sensor_data(self.current_run, "contrast", contrast, timestamp)
        
    def send_to_esp(self, data: dict):
        """Stuur een JSON-bericht naar de ESP32 via Bluetooth."""
        if self.bt and self.bt.serial and self.bt.serial.is_open:
            import json
            json_str = json.dumps(data)
            try:
                self.bt.send_json(json_str)
                # print(f"Sent to ESP32: {json_str}")
            except Exception as e:
                print(f"Send failed: {e}")
        else:
            print("Bluetooth niet verbonden — kan niet verzenden.")

