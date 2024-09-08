from flask import Flask
from app.models import db, bcrypt
import os
from flask_migrate import Migrate
from sqlalchemy import text  # Import text from SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"]=os.getenv("DATABASE_URL")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()

with app.app_context():
    try:
        # Test database connection
        result = db.session.execute(text('SELECT 1'))
        print("Database connection successful:", result)
        
        # Create all tables
        db.create_all()
    except Exception as e:
        print("Error connecting to the database:", e)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)