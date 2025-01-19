from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from datetime import timedelta
from models import User, Order, Address, db

# Import Blueprints
from view.auth import auth_bp
from view.order import order_bp
from view.address import address_bp
from view.user import user_bp

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
migrate = Migrate(app, db)
db.init_app(app)

app.config["JWT_SECRET_KEY"] = "lkigrdfe3ssfhhjo"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=6)
jwt = JWTManager(app)
jwt.init_app(app)

app.register_blueprint(user_bp)
app.register_blueprint(order_bp )
app.register_blueprint(address_bp)
app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app.run(debug=True)
