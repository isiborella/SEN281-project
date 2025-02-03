
import os, json, random, time, logging
import serial
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class NetworkDataHandler:
    def __init__(self, readings_file="data/network_readings.json", operators_file="data/network_operators.json"):
        self.readings_file = readings_file
        self.operators_file = operators_file
        
        # Ensure data directory exists
        os.makedirs("data", exist_ok=True)
        
        # Initialize files if they don't exist
        self._init_files()
    
    def _init_files(self):
        """Initialize JSON files if they don't exist"""
        if not os.path.exists(self.readings_file):
            with open(self.readings_file, 'w') as f:
                json.dump([], f)
        
        if not os.path.exists(self.operators_file):
            default_operators = [
                {
                    "id": 1,
                    "name": "MTN",
                    "country_code": "NG",
                    "network_code": "003"
                },
                {
                    "id": 2,
                    "name": "Glo",
                    "country_code": "NG",
                    "network_code": "005"
                }
            ]
            with open(self.operators_file, 'w') as f:
                json.dump(default_operators, f)
    
    def get_signal_quality(self, dbm):
        """Convert dBm to quality percentage"""
        if dbm >= -50: return 100
        elif dbm <= -120: return 0
        return int(((dbm + 120) / 70) * 100)
    
    def save_reading(self, reading_data):
        """Save a new network reading"""
        try:
            with open(self.readings_file, 'r') as f:
                readings = json.load(f)
            
            # Add timestamp and ID
            reading_data['id'] = len(readings) + 1
            reading_data['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            readings.append(reading_data)
            
            with open(self.readings_file, 'w') as f:
                json.dump(readings, f, indent=4)
            
            logging.info(f"Saved reading: {reading_data}")
            return True
        except Exception as e:
            logging.error(f"Error saving reading: {e}")
            return False
    
    def get_latest_reading(self):
        """Get the most recent network reading"""
        try:
            with open(self.readings_file, 'r') as f:
                readings = json.load(f)
            
            if readings:
                return readings[-1]
            return None
        except Exception as e:
            logging.error(f"Error getting latest reading: {e}")
            return None
    
    def get_historical_data(self, days=7):
        """Get historical readings for the specified number of days"""
        try:
            with open(self.readings_file, 'r') as f:
                readings = json.load(f)
            
            cutoff_date = (datetime.now() - timedelta(days=days))
            
            filtered_readings = [
                reading for reading in readings
                if datetime.strptime(reading['timestamp'], "%Y-%m-%d %H:%M:%S") >= cutoff_date
            ]
            
            return filtered_readings
        except Exception as e:
            logging.error(f"Error getting historical data: {e}")
            return []
    
    def get_operators(self):
        """Get list of network operators"""
        try:
            with open(self.operators_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Error getting operators: {e}")
            return []


class SIM800C:
    def __init__(self, port, baudrate=9600, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None

    def connect(self):
        try:
            self.serial = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            time.sleep(1)  # Allow initialization
            logging.info(f"Connected to SIM800C module on port {self.port}.")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to SIM800C on port {self.port}: {e}")
            return False

    def is_module_detected(self):
        """Check if SIM800C responds to AT command"""
        try:
            response = self.send_at_command("AT", "OK")
            return "OK" in response
        except Exception as e:
            logging.error(f"Error checking module detection: {e}")
            return False

    def is_sim_inserted(self):
        """ Check if a SIM card is inserted """
        try:
            response = self.send_at_command("AT+CPIN?", "+CPIN:")
            return "+CPIN: READY" in response
        except Exception as e:
            print(f"Error checking SIM card: {e}")
            return False
    

    def send_at_command(self, command, expected_response="OK", timeout=5):
        if not self.serial:
            raise Exception("SIM800C module is not connected.")
        
        if self.serial is None:
            return "Serial port not initialized."
        
        try:
            if not self.serial.is_open:
                self.serial.open()  # Attempt to open the port if closed
            
            self.serial.write((command + "\r\n").encode())
            response = self.serial.readline().decode().strip()
            return response if response else "No response received."

        except serial.serialutil.PortNotOpenError:
            return "Error: Serial port is not open."
        
        except serial.SerialException as e:
            return f"Serial communication error: {e}"
        
    
    def get_signal_strength(self):
        """Returns signal strength in dBm (Converted from CSQ value)"""
        response = self.send_at_command("AT+CSQ", "+CSQ:")
        if response:
            try:
                csq_value = int(response.split(":")[1].split(",")[0].strip())
                if csq_value == 99:
                    return -120  # No signal
                return (2 * csq_value) - 113  # Convert to dBm
            except ValueError:
                logging.error("Failed to parse signal strength.")
                return None
        return None

    def get_operator(self):
        """Gets the current network operator"""
        response = self.send_at_command("AT+COPS?", "+COPS:")
        if response:
            try:
                return response.split(",")[2].strip('"')
            except IndexError:
                logging.error("Failed to parse operator.")
                return "Unknown"
        return "Unknown"

    def get_network_type(self):
        """Identifies the network type (e.g., GSM, 3G, 4G, 5G)"""
        response = self.send_at_command("AT+CGREG?", "+CGREG:")
        if response:
            try:
                status_code = int(response.split(",")[1].strip())
                return {0: "Unknown", 1: "2G", 2: "3G", 3: "4G", 4: "5G"}.get(status_code, "Unknown")
            except (IndexError, ValueError):
                logging.error("Failed to parse network type.")
                return "Unknown"
        return "Unknown"

    def get_location(self):
        """Gets latitude and longitude if GPS is available"""
        response = self.send_at_command("AT+CIPGSMLOC=1,1", "+CIPGSMLOC:")
        if response:
            try:
                parts = response.split(":")[1].split(",")
                latitude, longitude = float(parts[1]), float(parts[2])
                return latitude, longitude
            except (IndexError, ValueError):
                logging.error("Failed to parse location.")
                return None, None
        return None, None


def collect_network_data():
    """Collect actual network readings using SIM800C"""
    sim800c = SIM800C(port='/dev/ttyUSB0', baudrate=9600)  # Update with your actual port
    if not sim800c.connect():
        logging.error("Failed to connect to SIM800C module.")
        return []

    readings = []
    
    for i in range(10):  # Collect multiple samples
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        signal_strength = sim800c.get_signal_strength()
        network_operator = sim800c.get_operator()
        network_type = sim800c.get_network_type()
        latitude, longitude = sim800c.get_location()

        reading = {
            "id": i + 1,
            "timestamp": timestamp,
            "operator": network_operator,
            "signal_strength": signal_strength if signal_strength is not None else "Unknown",
            "network_type": network_type,
            "availability": signal_strength is not None,
            "latitude": latitude if latitude is not None else "Unknown",
            "longitude": longitude if longitude is not None else "Unknown"
        }
        
        readings.append(reading)
        time.sleep(5)  # Delay to prevent rapid querying

    return readings


if __name__ == "__main__":
    # Save sample data to file
    os.makedirs("data", exist_ok=True)
    
    with open("data/network_readings.json", "w") as f:
        json.dump(collect_network_data(), f, indent=4)
    
    logging.info("Network readings saved successfully.")