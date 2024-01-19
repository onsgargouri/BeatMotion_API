import os #os.environ is used to access env variables to mantain security 

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth

SPOTIFY_CLIENT_ID = os.getenv('SPOTIFY_CLIENT_ID')  
SPOTIFY_CLIENT_SECRET = os.getenv('SPOTIFY_CLIENT_SECRET')
SPOTIPY_REDIRECT_URI = os.getenv('SPOTIPY_REDIRECT_URI')

sp_oauth = SpotifyOAuth(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope="playlist-modify-private")

def clear_cached_token():
    sp_oauth._save_token_info(None) 
    return "Cached token cleared successfully."
    

def get_spotify_access_token():
    # Note: Spotipy library automatically refreshes the access token when it is close to expiration
    # however i used the function sp_oauth.is_token_expired() to ensure the access of the user 
    
    token_info = sp_oauth.get_cached_token()
    if not token_info or sp_oauth.is_token_expired(token_info): 
        auth_url = sp_oauth.get_authorize_url()
        return {'message': 'Please access this URL to authorize', 'authorization_url': auth_url}, 401
    
    sp = Spotify(auth=token_info['access_token'])
    user_info = sp.current_user()
    user_id = user_info['id']
    sp_info = {
        'access_token': token_info['access_token'],
        'user_id': user_id,
    }
    
    return {'message': 'Access token is available', 'access_token': token_info['access_token'], 'userID': user_id, 'sp_info': sp_info}, 200
