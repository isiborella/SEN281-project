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
    network_speed = random.randint(10, 100)  # Generate a random speed in Mbps
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")  # Get current date
    current_time = datetime.datetime.now().strftime("%H:%M:%s")  # Get current time
    return render_template('live_data.html', speed=network_speed, date=current_date, time=current_time)


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