from flask import Flask, render_template
from controller.database import db
from controller.config import config
from controller.models import *

app = Flask(__name__, template_folder='templates',static_folder='static')
app.config.from_object(config)
db.init_app(app)

with app.app_context():
    db.create_all()

    admin_role = Role.query.filter_by(name='admin').first()
    if not admin_role:
        admin_role = Role(name='admin')
        db.session.add(admin_role)

    
    admin_user = User.query.filter_by(user_email = 'admin@gmail.com').first()
    if not admin_user:
        admin_role = Role.query.filter_by(name='admin').first()
        admin_user = User(
            user_email = 'admin@gmail.com',
            password = '123456789',
            user_name = 'Super admin',
            roles = [admin_role]
        )
        db.session.add(admin_user)
    db.session.commit()

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':  
    app.run()