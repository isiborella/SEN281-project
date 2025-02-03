

from datetime import datetime
from flask import render_template, request, jsonify
from application import app
from .logic import NetworkDataHandler
import serial
data_handler = NetworkDataHandler()


from .logic import SIM800C


# SIM800C module configuration
SIM800C_PORT = '/dev/ttyUSB0'  # Serial port for SIM800C (e.g., '/dev/ttyUSB0' or 'COM3')
POSSIBLE_PORTS = ['/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyAMA0', '/dev/ttyS0', '/dev/ttyACM0']

SIM800C_PORT = None
for port in POSSIBLE_PORTS:
    try:
        SIM800C_PORT = serial.Serial(port, 9600, timeout=1)  # Adjust the baud rate as needed
        print(f"Serial port initialized successfully on {port}.")
        break  # Stop trying ports once a valid one is found
    except serial.SerialException as e:
        print(f"Error initializing serial port on {port}: {e}")
        SIM800C_PORT = None  # Reset to None if the port is unavailable

if SIM800C_PORT is None:
    print("No valid serial port found. Network Analyser functionality will be disabled.")

# Initialize the SIM800C module
sim800c = SIM800C(port=SIM800C_PORT, baudrate=9600)

# Connect to the SIM800C module
sim800c.connect()



@app.route('/', methods=['GET', 'POST'])
def home():
    
    """
    Home page route.
    Displays SIM800C module status.
    """
    if not sim800c.connect():
        return render_template('index.html', error="SIM800C module not connected.")

    module_detected = sim800c.is_module_detected()
    sim_inserted = sim800c.is_sim_inserted()
    signal_strength = sim800c.get_signal_strength()

    
    # Default status values
    module_status = "Not Detected"
    sim_status = "Unknown"
    signal_strength = "N/A"

    # Check for SIM800C module detection
    try:
        response = sim800c.send_at_command("AT")
        if "OK" in response:
            module_status = "Detected"
        else:
            module_status = "Not Detected"
    except Exception as e:
        module_status = f"Error: {e}"

    # Check if SIM has been inserted using AT+CPIN?
    try:
        sim_response = sim800c.send_at_command("AT+CPIN?")
        if "READY" in sim_response:
            sim_status = "Inserted"
        else:
            sim_status = "Not Inserted"
    except Exception as e:
        sim_status = f"Error: {e}"

    # Get the network signal level using AT+CSQ
    try:
        csq_response = sim800c.send_at_command("AT+CSQ")
        if "+CSQ:" in csq_response:
            # Example response: "+CSQ: 20,99"
            csq_parts = csq_response.split(":")[1].split(",")
            signal_strength = csq_parts[0].strip() if csq_parts else "N/A"
        else:
            signal_strength = "N/A"
    except Exception as e:
        signal_strength = f"Error: {e}"

    
    #operators = data_handler.get_operators()
    network_operator = ""
    latest_reading = data_handler.get_latest_reading()
    try:
        network_operator=latest_reading['operator'],
    except:
        pass

    return render_template('index.html',
        module_status=module_status, 
        sim_status=sim_status, 
        module_detected=module_detected,
        sim_inserted=sim_inserted,
        signal_strength=signal_strength,
        network_operator=network_operator)

@app.route('/live_data', methods=['GET'])
def live_data():
    latest_reading = data_handler.get_latest_reading()
    
    if latest_reading:
        # Calculate signal quality percentage
        signal_quality = data_handler.get_signal_quality(latest_reading['signal_strength'])
        
        # Format timestamp for better readability
        timestamp = datetime.strptime(latest_reading['timestamp'], "%Y-%m-%d %H:%M:%S")
        formatted_date = timestamp.strftime("%B %d, %Y")  # e.g., February 03, 2025
        formatted_time = timestamp.strftime("%I:%M:%S %p")  # e.g., 02:30:45 PM
        
        return render_template('live_data.html',
                             date=formatted_date,
                             time=formatted_time,
                             network_operator=latest_reading['operator'],
                             network_type=latest_reading['network_type'],
                             signal_strength=latest_reading['signal_strength'],
                             signal_quality=signal_quality,
                             availability=latest_reading.get('availability', True))
    
    return render_template('live_data.html', error="No data available")

@app.route('/historical_data', methods=['GET'])
def historical_data():
    readings = data_handler.get_historical_data(days=7)
    
    processed_data = []
    for reading in readings:
        processed_data.append({
            "date": reading['timestamp'],
            "network_operator": reading['operator'],
            "network_type": reading['network_type'],
            "signal_strength": reading['signal_strength'],
            "signal_quality": data_handler.get_signal_quality(reading['signal_strength']),
            "availability": "Available" if reading.get('availability', True) else "Unavailable"
        })
    
    return render_template('historical_data.html', data=processed_data)

@app.route('/api/record', methods=['POST'])
def record_reading():
    """API endpoint to record new network readings"""
    try:
        data = request.json
        required_fields = ['operator', 'signal_strength', 'network_type', 'latitude', 'longitude']
        
        # Check for missing fields
        if not all(field in data for field in required_fields):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        # Validate signal strength
        try:
            signal_strength = float(data['signal_strength'])
            if signal_strength < -120 or signal_strength > -50:
                return jsonify({"status": "error", "message": "Invalid signal strength range"}), 400
        except ValueError:
            return jsonify({"status": "error", "message": "Signal strength must be a number"}), 400

        # Ensure latitude and longitude are numeric
        try:
            latitude = float(data['latitude'])
            longitude = float(data['longitude'])
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid latitude or longitude"}), 400

        # Set availability to True if not provided
        data['availability'] = data.get('availability', True)

        # Save the reading
        if data_handler.save_reading(data):
            return jsonify({"status": "success", "message": "Reading recorded successfully"}), 201
        else:
            return jsonify({"status": "error", "message": "Failed to save reading"}), 500
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400
    

    