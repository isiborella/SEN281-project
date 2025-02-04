
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


import getpass, os, subprocess
import time
try:
    import RPi.GPIO as GPIO
except:
    pass

import num2words
import serial


class portIDAllocation(object):
    def __init__(self, *args):
        super(portIDAllocation, self).__init__(*args)
        
    def NumberOfPorts(self):
        NumberOfPorts = len(list(filter(None, " ".join(list(subprocess.check_output(['lsusb', '-s', ':1']).decode())).split("\n"))))
        return NumberOfPorts
     
    def liveUSBPorts(self):
        matchingPortList 	= []
        portIDList		    = []
        NumUSBPort = self.NumberOfPorts()
        print(NumUSBPort)
        current_os_user = getpass.getuser()
        #print("NumUSBPort: ", NumUSBPort, "current_os_user: ", current_os_user)
        constant_path = "/dev/ttyUSB"
        counter = 0
        try:
            USBport = constant_path + str(counter)
            portID  = "Zero"
            if os.path.exists(str(USBport)) == True :
                print("USBport: ", USBport)
                matchingPortList.append(USBport)
                portIDList.append(portID)
        except :
            pass
        counter     = counter + 1
        while (counter < NumUSBPort ):
            variable_path = str(counter)
            USBport = constant_path + variable_path
            print("USBport: ", USBport)
            if os.path.exists(str(USBport)) == True :
                print("USBport: ", USBport, "portID: ", portID)
                portID  = num2words.word(counter)
                matchingPortList.append(USBport)
                portIDList.append(portID)

            counter += 1
        print(portIDList, matchingPortList)
        portAssignment = dict(zip(portIDList, matchingPortList))
        return portAssignment

class serialportSetup(object):
    def __init__(self, serialport, *args):
        self.serialport     = serialport
        super(serialportSetup, self).__init__(*args)

    def serialSetup(self):
        serialport      = self.serialport
        ser             = serial.Serial(serialport, 9600, timeout=1)
        '''with serial.Serial(serialport, 9600, timeout=1) as ser:
            print("Inside Own logic",ser, type(ser))
            return ser
            '''
        return ser

class SMSCommands(object):
    def __init__(self, ser, *args):
        self.ser        = ser
        super(SMSCommands, self).__init__(*args)
    
    def send_at_command(self, command, timeout=1):
        ser     = self.ser
        ser.write((command + "\r\n").encode('utf-8'))
        time.sleep(timeout)
        return ser.read_all().decode('utf-8')

    def get_module_info(self):
        return self.send_at_command( 'ATI')

    def get_sim_info(self):
        return self.send_at_command( 'AT+CCID')

    def get_operator_info(self):
        response = self.send_at_command('AT+COPS?')
        operator_index = response.find('+COPS:')
        if operator_index != -1:
            parts = response[operator_index:].split(',')
            if len(parts) >= 3:
                operator_name = parts[2].strip('"')
                return operator_name
        return None

    def get_signal_info(self):
        response = self.send_at_command('AT+CSQ')
        signal_level = response.split(',')[0].strip('+CSQ: ')
        return signal_level

    def get_network_info(self):
        #response = self.send_at_command('AT+CIPRXGET?')
        #response = self.send_at_command('AT+CPSI?')
        # Enable engineering mode
        self.send_at_command('AT+CENG=3')
        time.sleep(1)  # Wait for response

        # Query detailed cell information
        response = self.send_at_command('AT+CENG?')
        return response 
    
    def get_network_time(self):
        response = self.send_at_command('AT+CCLK?')
        return response 
    
    def get_network_location_info(self):
        response = self.send_at_command('AT+CIPGSMLOC=1,1')
        return response 
    
    def is_sim_attached(self):
        response = self.send_at_command( 'AT+CPIN?')
        return '+CPIN: READY' in response

    def is_network_available(self):
        response = self.send_at_command('AT+CREG?')
        return '+CREG: 0,1' in response or '+CREG: 0,5' in response

    def get_network_operator(self):
        response = self.send_at_command('AT+COPS?')
        operator_index = response.find('+COPS:')
        if operator_index != -1:
            parts = response[operator_index:].split(',')
            if len(parts) >= 3:
                operator_name = parts[2].strip('"')
                return operator_name
        return None

    def truncate_message(message, max_length=160):
        return message[:max_length]
    
    def set_sms_mode(self):
        self.send_at_command('AT+CMGF=1')  # Set SMS mode to text mode
        time.sleep(3)

    def list_sms_messages(self):
        messages = []
        response = self.send_at_command( 'AT+CMGL="ALL"')
        time.sleep(3)
        """buffereing_bytes = ser.read(ser.inWaiting())
        print("response: ", response)
        request = buffereing_bytes.decode('utf-8')
        print("request: ", request)"""
        lines = response.strip().split('\r\n')
        #print("lines: ", lines)
        print(len(lines), type(lines))
        #for i in range(0, len(lines)):
        for line in lines:
            if line.startswith('+CMGL'):
                messages.append({
                    'index': int(line.split(',')[0].split(':')[1].strip())})
                #messages.append(line)
            #print(lines[i], "\n\n")
            #if lines[i].start
            #messages.append({'message': lines[i]})
        """try:
            for i in range(0, len(lines), 2):
                print(lines[i], len(lines))
                messages.append({
                    'index': int(lines[i].split(',')[0].split(':')[1].strip()),
                    'sender': lines[i].split(',')[1].strip(),
                    'date': lines[i].split(',')[3].strip(),
                    'message': lines[i+1].strip()
                })
                print(lines[i+1].strip())
        except:
            pass"""
        print(messages)
        return messages
    
    def check_call_status(self):
        response = self.send_at_command( 'AT+CPAS')
        return '+CPAS: 0' in response  # Call active
    
class gpioDefine(object):
    def __init__(self, *args):
        super(gpioDefine, self).__init__(*args)
    
    def setup(P_BUTTON):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(P_BUTTON, GPIO.IN, GPIO.PUD_UP)



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