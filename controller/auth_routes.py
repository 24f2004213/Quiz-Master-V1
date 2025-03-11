from main import app
from flask import render_template, request, session, flash, redirect, url_for
from controller.models import *
from datetime import datetime
from flask_login import LoginManager,UserMixin, login_required, current_user, login_user, logout_user

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)

        if not username or not password:
            flash('Please enter valid data')
            return render_template('login.html')

        if '@' not in username:
            flash('Please enter a valid email')
            return render_template('login.html')

        user = User.query.filter_by(user_email=username).first()
        if not user:
            flash('User does not exist... Please register!')
            return render_template('login.html')

        if user.password != password:  
            flash('Invalid password')
            return render_template('login.html')

        login_user(user)
        session['user_email'] = user.user_email

        if any(role.name == "admin" for role in user.roles):
            session['user_role'] = "admin"
            return redirect(url_for('home'))  

        session['user_role'] = "user"
        return redirect(url_for('user_dashboard'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'GET':
        return render_template('signup.html')



    username = request.form.get('username')
    password = request.form.get('password')
    fullname = request.form.get('fullname')
    qualification = request.form.get('qualification')
    dob = request.form.get('dob')


    if not username or not password or not fullname or not qualification or not dob:
        flash('Please enter all required fields', 'error')
        return render_template('signup.html')

    if '@' not in username:
        flash('Invalid email address', 'error')
        return render_template('signup.html')

    try:
        dob_object = datetime.strptime(dob, "%Y-%m-%d").date()
    except ValueError:
        flash('Invalid date format. Use YYYY-MM-DD', 'error')
        return render_template('signup.html')

    existing_user = User.query.filter_by(user_email=username).first()
    if existing_user:
        flash('User already exists. Please log in.', 'error')
        return redirect(url_for('login'))

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

    return redirect(url_for('user_dashboard'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for('login'))