from spotipy import Spotify
from flask import request  
from flask.views import MethodView
from db import db
from models import UserModel

from sqlalchemy.exc import SQLAlchemyError,IntegrityError
from flask_smorest import Blueprint, abort
from resources.auth_utils import get_spotify_access_token,sp_oauth, clear_cached_token
from schemas import AuthorizationSchema,UserDeleteSchema

blp = Blueprint("authentication", __name__, description="Authentication Operations")

@blp.route("/clearcache")
class cache(MethodView):
    def get(self):
        message= clear_cached_token()
        return {"message":message}
@blp.route("/authorization")
class Authorization(MethodView):
    @blp.response(200, AuthorizationSchema)
    def get(self):
        access_result = get_spotify_access_token()
        print(access_result)
        if access_result and access_result[0]['message'] == 'Please access this URL to authorize':
            authorization_url = access_result[0]['authorization_url']
            abort(401, message=f'Authorization required . Please access this URL to authorize : {authorization_url}')
        
        else:
            get_spotify_access_token()
            return {"message" : "You are successfully authorized !"}



@blp.route("/callback")
class Callback(MethodView):
    def get(self):
        code = request.args.get('code')
        token_info = sp_oauth.get_access_token(code)
        sp_oauth._save_token_info(token_info)
        if 'error' in token_info:
            abort(400, message='Authorization failed')

        access_token = token_info['access_token']
        sp = Spotify(auth=access_token)
        
        user_info = sp.current_user()
        user_id = user_info['id']

        new_user = UserModel(user_id=user_id)
        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            abort(400,message=" User with the same id already exists")
        except SQLAlchemyError:
            abort(500,message="an error occured while adding the user")

        return "Authorization successful! You can now use the access token."
    
@blp.route("/<string:user_id>")
class RemoveUser(MethodView):
    @blp.response(200,UserDeleteSchema)
    def delete(self, user_id):
    
        user_to_remove = UserModel.query.filter_by(user_id=user_id).first()
        if user_to_remove:
            try:
                db.session.delete(user_to_remove)
                db.session.commit()
                clear_cached_token()
                return{'message': 'User deleted successfully'}, 200
            except SQLAlchemyError:
                abort(500,message="an error occured while deleting the user")
        abort(404, message='User not found')
