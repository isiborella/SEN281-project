import datetime
import random
from flask import Flask,redirect,url_for,render_template,request
from application import app

@app.route('/',methods=['GET','POST'])
def home():
    if request.method=='POST':
        # Handle POST Request here
        return render_template('index.html')
    return render_template('index.html')

# Route for the Live Data Page
@app.route('/live_data.html', methods=['GET'])
def live_data():
    # Simulate live network speed data
    signal_strength = random.randint(10, 100)  # Generate a random speed in Mbps
    return render_template('live_data.html', signalavailability=signal_strength)

# Route for the Historical Data Page
@app.route('/historical_data.html', methods=['GET'])
def historical_data():
    # Generate sample historical data
    historical_data = [
        {"date": datetime.datetime.now().strftime("%Y-%m-%d"), "speed": random.randint(10, 100)},
        {"date": (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d"), "speed": random.randint(10, 100)},
        {"date": (datetime.datetime.now() - datetime.timedelta(days=2)).strftime("%Y-%m-%d"), "speed": random.randint(10, 100)},
    ]
    return render_template('historical_data.html', data=historical_data)