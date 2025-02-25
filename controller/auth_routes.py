from main import app
from flask import render_template, request, session, flash, redirect, url_for
from controller.models import *
from datetime import datetime

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        
        return render_template('login.html')
    
    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)

        #data validation
        if not username or not password:
            flash('Please enter valid data')
            return render_template('login.html')
        
        if '@' not in username:
            flash('Please enter valid username')
            return render_template('login.html')
        
        #query database to check if user exists
        user = User.query.filter_by(user_email=username).first()
        if not user:
            flash('User does not exist... Please register!!!')
            return render_template('login.html')
        if user.password != password:
            flash('Invalid password')
            return render_template('login.html')
        
        session['user_email'] = user.user_email
        session['user_role'] = [role.name for role in user.roles]
        admin_role = Role.query.filter_by(name="admin").first()
    
    if admin_role and admin_role in user.roles:
        session['user_role'] = "admin"
        return redirect(url_for('home'))
    else:  
        session['user_role'] = "user"
        return redirect(url_for('user_dashboard'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'GET':
        return render_template('signup.html')


    # Debug: Print full form data

    username = request.form.get('username')
    password = request.form.get('password')
    fullname = request.form.get('fullname')
    qualification = request.form.get('qualification')
    dob = request.form.get('dob')


    # Validate input
    if not username or not password or not fullname or not qualification or not dob:
        flash('Please enter all required fields', 'error')
        return render_template('signup.html')

    if '@' not in username:
        flash('Invalid email address', 'error')
        return render_template('signup.html')

    # Convert dob string to date object
    try:
        dob_object = datetime.strptime(dob, "%Y-%m-%d").date()
    except ValueError:
        flash('Invalid date format. Use YYYY-MM-DD', 'error')
        return render_template('signup.html')

    # Check if user exists
    existing_user = User.query.filter_by(user_email=username).first()
    if existing_user:
        flash('User already exists. Please log in.', 'error')
        return redirect(url_for('login'))

    # Create user
    new_user = User(
        user_email=username,
        password=password,  
        user_name=fullname,
        user_qualification=qualification,
        dob=dob_object
    )

    db.session.add(new_user)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('Database error. Please try again.', 'error')
        return render_template('signup.html')

    # Store session
    session['user_email'] = new_user.user_email
    session['user_name'] = new_user.user_name
    session['qualification'] = new_user.user_qualification
    session['dob'] = str(new_user.dob)

    return redirect(url_for('home'))
