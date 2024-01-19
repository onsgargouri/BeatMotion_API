from flask import Flask
from flask_smorest import Api

from db import db

from resources.playlists import blp as PlaylistBlueprint
from resources.authentication import blp as AuthBlueprint

app = Flask(__name__)

#http://127.0.0.1:5000/swagger-ui
app.config["PROPAGATE_EXCEPTIONS"] = True
app.config["API_TITLE"] = "BeatMotion REST API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/"
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"   
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"    
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app) #connect our app to SQLAlchemy   0
with app.app_context():
    db.create_all()

api = Api(app)

api.register_blueprint(PlaylistBlueprint)
api.register_blueprint(AuthBlueprint)

if __name__ == '__main__':
    app.run(debug=True)