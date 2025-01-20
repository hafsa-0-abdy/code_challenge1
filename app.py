from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from datetime import timedelta
from models import db, TokenBlocklist
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

#  Flask mail configuration
# app.config["MAIL_SERVER"]= 'smtp.gmail.com'
# app.config["MAIL_PORT"]=587
# app.config["MAIL_USE_TLS"]=True
# app.config["MAIL_USE_SSL"]=False
# app.config["MAIL_USERNAME"]="hafsaabdirizack0@gmail.com"
# app.config["MAIL_PASSWORD"]="jila igua qyac yxcv"
# app.config["MAIL_DEFAULT_SENDER"]="hafsaabdirizack0@gmail.com"


# mail = Mail(app)

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
@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
    jti = jwt_payload["jti"]
    token = db.session.query(TokenBlocklist.id).filter_by(jti=jti).scalar()

    return token is not None
