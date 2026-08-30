# bluetooth_manager.py
import serial
import threading
import time

class BluetoothManager:
    """Verantwoordelijk voor BT-verbinding en ruwe datastroom van de ESP32."""

    def __init__(self, port=None, baudrate=115200, timeout=2):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.running = False
        self.read_thread = None
        self.keep_alive_thread = None
        self.buffer = ""
        self.data_callback = None  # Wordt ingesteld door DataManager
        self.last_pong_time = time.time()  # starttijd
        self.pong_timeout = 5  # seconden
        self.connected = False
    # ---------------- Verbinden ----------------
    def connect(self):
        """Probeer te verbinden met de ESP32 en start threads."""
        try:
            print(f"Connecting to {self.port} at {self.baudrate}...")
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout, write_timeout=2)
            time.sleep(2)

            # Handshake
            self.serial.write(b"PING\n")
            print(" Sent handshake: PING")

            response = self.serial.readline().decode(errors="ignore").strip()
            print(f" Received: {response}")

            if response != "PONG":
                print("No valid response. Not the correct device.")
                self.disconnect()
                return False

            print("Connected successfully to LineFollow_V1!")
            self.running = True

            # Start lees- en keep-alive threads
            self.read_thread = threading.Thread(target=self._read_loop, daemon=True)
            self.read_thread.start()

            self.keep_alive_thread = threading.Thread(target=self._keep_alive, daemon=True)
            self.keep_alive_thread.start()

            return True

        except serial.SerialException as e:
            print(f"Serial error: {e}")
            return False

    # ---------------- Leesloop ----------------
    def _read_loop(self):
        """Leest alle inkomende data van de ESP32."""
        while self.running and self.serial and self.serial.is_open:
            try:
                if self.serial.in_waiting:
                    # lees één regel
                    msg = self.serial.readline().decode(errors="ignore").strip()
                    #print("msg :", msg)
                    if not msg:
                        continue

                    # PONG ontvangen -> update connected status
                    if msg == "PONG":
                        self.connected = True
                        self.last_pong_time = time.time()
                        # debug
                        # print("PONG ontvangen, verbinding actief")

                    # anders -> stuur naar DataManager callback
                    elif self.data_callback:
                        self.data_callback(msg)

            except Exception as e:
                print("Read error:", e)
                self.connected = False
                break

    # ---------------- Keep-alive ----------------
    def _keep_alive(self):
        """Stuurt periodiek PING naar ESP32 en checkt timeout."""
        while self.running and self.serial and self.serial.is_open:
            try:
                # stuur PING
                self.serial.write(b"PING\n")
            except Exception:
                # Communicatiefout → verbreek verbinding
                print("KeepAlive: write error, afsluiten...")
                self._handle_disconnect()
                return  # thread eindigt

            # check of er te lang geen PONG is geweest
            if time.time() - self.last_pong_time > self.pong_timeout:
                print("KeepAlive: timeout, ESP reageert niet meer.")
                self._handle_disconnect()
                return  # thread eindigt

            time.sleep(3)

    # ---------------- Verbreken ----------------
    def disconnect(self):
        """Sluit verbinding af."""
        self.running = False
        if self.serial and self.serial.is_open:
            try:
                self.serial.close()
                print("Disconnected")
            except Exception as e:
                print(f"Error during disconnect: {e}")

    def send_json(self, json_str):
        if self.serial and self.serial.is_open:
            self.serial.write((json_str + "\n").encode('utf-8'))

    def _handle_disconnect(self):
        """Sluit de verbinding en reset status."""
        try:
            self.running = False
            if self.serial and self.serial.is_open:
                self.serial.close()
        except Exception as e:
            print("Fout bij sluiten:", e)
        finally:
            self.connected = False
            self.serial = None
            print("BT volledig afgesloten.")
