from main import app
from flask import render_template, request, session, flash
from controller.models import *

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/home')
def home():
    return render_template('home.html')
@app.route('/user_dashboard')
def user_dashboard():
    return render_template('user_dashboard.html')