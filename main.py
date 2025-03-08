from flask import Flask, render_template
from controller.database import db
from controller.config import config
from controller.models import *
from datetime import datetime
from flask_login import LoginManager,UserMixin, login_required, current_user, login_user, logout_user

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)  
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

login_manager.login_view = 'login'

with app.app_context():
    db.create_all()

    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin')
        db.session.add(admin_role)
    dob_string = '10-05-2006'
    dob_date = datetime.strptime(dob_string, '%d-%m-%Y').date()
    admin_user = User.query.filter_by(user_email = 'admin@gmail.com').first()
    if not admin_user:
        admin_role = Role.query.filter_by(name='admin').first()
        admin_user = User(
            user_email = 'admin@gmail.com',
            password = '123456789',
            user_name = 'Super admin',
            user_qualification = 'BS',
            dob = dob_date,
            roles = [admin_role]
        )
        db.session.add(admin_user)
    db.session.commit()

from controller.auth_routes import *
from controller.routes import *

if __name__ == '__main__':  
    app.run(debug=True)