from flask import Flask
from app.models import db, bcrypt
import os
from flask_migrate import Migrate
from sqlalchemy import text
from app.routes.auth import auth_blueprint

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]=os.getenv("DATABASE_URL")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(auth_blueprint)

with app.app_context():
    try:
        result = db.session.execute(text('SELECT 1'))
        print("Database connection successful:", result)

        db.create_all()
    except Exception as e:
        print("Error connecting to the database:", e)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)