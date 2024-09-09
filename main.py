from flask import Flask
from app.models import db, bcrypt
import os
from flask_migrate import Migrate
from sqlalchemy import text
from app.routes.auth import auth_blueprint
from flask_admin.contrib.sqla import ModelView
from wtforms import StringField
from flask_admin import Admin, AdminIndexView, expose

from app.models import Users, Groups, Resource, Permissions, Reservations

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]=os.getenv("DATABASE_URL")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
bcrypt.init_app(app)
app.app_context().push()
migrate = Migrate(app, db)

app.register_blueprint(auth_blueprint)

def admin_page_creation(app):
    from flask_wtf import FlaskForm
    from wtforms import SelectField, DateField
    from wtforms.validators import DataRequired
       
    
    class UserAdminView(ModelView):
        
        column_list = ["id", "username", "email", "password_hash", "groups", "reservations"]
        def on_model_change(self, form, model, is_created):
            model.set_password(model.password_hash)

    class GroupAdminView(ModelView):
        column_hide_backrefs = False
        column_list = ["id", "name", "users", "permissions"]
        

    admin = Admin(app, name="Manager", template_mode="bootstrap3")
    admin.add_view(UserAdminView(Users, db.session))
    admin.add_view(GroupAdminView(Groups, db.session))
    admin.add_view(ModelView(Resource, db.session))
    admin.add_view(ModelView(Permissions, db.session))
    admin.add_view(ModelView(Reservations, db.session))

admin_page_creation(app)

with app.app_context():
    try:
        result = db.session.execute(text("SELECT 1"))
        print("Database connection successful:", result)

        db.create_all()
    except Exception as e:
        print("Error connecting to the database:", e)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)