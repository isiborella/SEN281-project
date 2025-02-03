

from flask import Flask,redirect,url_for,render_template,request

app=Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

#from .routes import *
from application import routes

