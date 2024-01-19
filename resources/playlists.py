from spotipy import Spotify
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import db, tracks_info
from models import PlaylistModel,PlaylistTrackModel,UserModel
from sqlalchemy.exc import SQLAlchemyError
from resources.auth_utils import get_spotify_access_token
from resources.playlists_utils import create_spotify_playlist, convert_preferences_to_audio_features, get_spotify_recommendations
from schemas import PlaylistGenerationSchema, UsersPlaylistSchema,UserPreferencesSchema,PlaylistSchema, PlaylistDeleteSchema, PlaylistPlaySchema, PlaylistTracksSchema, TracksAudioFeaturesSchema


blp = Blueprint("playlists", __name__, description="Operations on playlists")

@blp.route("/preferences")
class UsersPlaylist(MethodView):
    # display all users playlists 
    def get(self):
        all_users = UserModel.query.all()
        if not all_users:
            abort(404, message='No User found')
        users_data = [
            {"user_id": user.user_id, "playlists": [playlist.to_dict() for playlist in user.playlists]}
            for user in all_users
        ]
        return {"users_preferences": users_data}
  
@blp.route("/preferences/<string:user_id>")
class UserPlaylist(MethodView):
    #get all playlists for a specific user
    @blp.response(200, UserPreferencesSchema)
    def get(self, user_id):
        
        user = UserModel.query.filter_by(user_id=user_id).first()
        if user is None:
            abort(404, message='User not found')
        # Retrieve the playlists associated with the user
        playlists = PlaylistModel.query.filter_by(user=user).all()
        if not playlists:
            return {"user_id": user_id, "playlists": [], "message": "User has no playlists"}
        playlists_data = [playlist.to_dict() for playlist in playlists]
        return {"playlists": playlists_data}
        

@blp.route("/generate_playlist/<string:user_id>")
class GeneratePlaylist(MethodView):
    @blp.arguments(PlaylistGenerationSchema)
    @blp.response(201, PlaylistSchema)
    #generate a new playlist for a specific user based on his prefrences
    def post(self,request_data,user_id):
        #get the access token 
        access_result = get_spotify_access_token()
        
        if access_result and access_result[0]['message'] == 'Please access this URL to authorize':
            authorization_url = access_result[0]['authorization_url']
            abort(401, message=f'Authorization required . Please access this URL to authorize : {authorization_url}')

        current_user = UserModel.query.filter_by(user_id=user_id).first()
        if current_user is None:
            abort(404, message='User not found')
        
        sp_info = access_result[0]['sp_info']
        access_token = sp_info.get('access_token')
        # Create a new Spotify object using the access token
        sp = Spotify(auth=access_token)
            #STEP A : create an empty playlist  
        playlist_name=request_data.get('playlist_name', 'Workout Playlist') #second parameter is the default name
        description = request_data.get('playlist_description','Your personalized workout playlist')
        playlist_id= create_spotify_playlist(sp,user_id, playlist_name, description)
        if not playlist_id:
            abort(500, message='Failed to create playlist')

            #STEP B : get playlist prefrences
        playlist_prefrences = {
                        'workout_type': request_data.get('workout_type', 'walking'),
                        'intensity_level': request_data.get('intensity_level', 'moderate'),
                        'music_genre': request_data.get('music_genre', 'pop'),
                        #'instrumentalness': request_data.get('instrumentalness', 'vocals'),
                        #'danceability':request_data.get('danceability', 'normal'),
                        #'mood': request_data.get('mood', 'positive'),   
                        "playlist_tracks": []  
                    }
            # STEP C : convert these prefrences to audio features
        audio_features=convert_preferences_to_audio_features(playlist_prefrences)
        print("Audio Features:", audio_features)

            #STEP D : search for recommendations
        recommended_tracks_info=get_spotify_recommendations(sp,audio_features)
        if not recommended_tracks_info:
            abort(500, message='No recommendations found')
        recommended_uris = [track_info['uri'] for track_info in recommended_tracks_info]
        tracks_info.clear()
        #for testing purposes
        tracks_info.extend(recommended_uris)
                #add tracks to the empty playlist in spotify using their uri 
        sp.playlist_add_items(playlist_id, recommended_uris)

                # Update users_preferences with the new playlist
        new_playlist = PlaylistModel(
            playlist_id=playlist_id,
            playlist_name=playlist_name,
            playlist_description=description,
            workout_type=playlist_prefrences['workout_type'],
            intensity_level=playlist_prefrences['intensity_level'],
            music_genre=playlist_prefrences['music_genre'],
            user=current_user
        )
        try:
            db.session.add(new_playlist)
            db.session.commit()
        except SQLAlchemyError:
            abort(500,message="an error occured while adding a new playlist in the database")
        
        new_playlist_tracks = [
            PlaylistTrackModel(
                track_name=track_info.get('track_name', 'Unknown Track'),
                artist_name=track_info.get('artist_name', 'Unknown Artist'),
                uri=track_info['uri'],
                playlist=new_playlist
            ) for track_info in recommended_tracks_info
        ]
        try:
            db.session.add_all(new_playlist_tracks)
            db.session.commit()
        except SQLAlchemyError:
            abort(500,message="an error occured while adding a tracks in the database")
        
        print("New Playlist Data:", new_playlist.to_dict())

        print("New Playlist Object:", new_playlist)
        return new_playlist.to_dict(), 201


    
@blp.route("/delete_playlist/<string:user_id>/<string:playlist_id>")
class PlaylistDelete(MethodView):
    #delete a user's playlist 
    @blp.response(200,PlaylistDeleteSchema)
    def delete(self, user_id, playlist_id):
        access_result = get_spotify_access_token()


        if access_result and access_result[0]['message'] == 'Please access this URL to authorize':
            authorization_url = access_result[0]['authorization_url']
            abort(401, message=f'Authorization required . Please access this URL to authorize : {authorization_url}')


        sp_info = access_result[0]['sp_info']
        access_token = sp_info.get('access_token')

        sp = Spotify(auth=access_token)
        user = UserModel.query.filter_by(user_id=user_id).first()
        if user is None:
            abort(404, message='User not found')
                
        playlist = PlaylistModel.query.filter_by(user=user, playlist_id=playlist_id).first()
        if not playlist:
            abort(404, message='Playlist not found')
        sp.user_playlist_unfollow(user_id, playlist_id)
        
        try:
            db.session.delete(playlist)
            db.session.commit()
        except SQLAlchemyError:
            abort(500,message="an error occured while deleting a playlist in the database")
        
        return {'message': 'Playlist deleted successfully'}, 200

@blp.route("/playlist/<string:playlist_id>")
class PlaylistPlay(MethodView):
    @blp.response(200, PlaylistPlaySchema)
    def get(self,playlist_id):
        playlist = PlaylistModel.query.filter_by(playlist_id=playlist_id).first()
        if playlist is None:
            abort(404, message='playlist not found')
        
        # Generate the link to the Spotify Playlist Embed
        embed_link = f'https://open.spotify.com/embed/playlist/{playlist_id}'

        return {"Link_to_play_Spotify_Playlist": embed_link}

@blp.route("/playlist_tracks/<string:playlist_id>")
class Playlist_Tracks(MethodView):   
    #see playlist tracks
    @blp.response(200, PlaylistTracksSchema)
    def get(self, playlist_id):
        
        playlist = PlaylistModel.query.get_or_404(playlist_id, description="Playlist not found")
        tracks = PlaylistTrackModel.query.filter_by(playlist=playlist).all()
        tracks_data = [track.to_dict() for track in tracks]
        return {"playlist_tracks": tracks_data}

#Display playlists tracks audio features .. ( this is mainly for verifying purposes during the development)  
@blp.route("/tracks")
class TracksAudioFeatures(MethodView):
    @blp.response(200, TracksAudioFeaturesSchema)
    def get(self):
        access_result = get_spotify_access_token()
        if access_result and access_result[0]['message'] == 'Please access this URL to authorize':
            authorization_url = access_result[0]['authorization_url']
            abort(401, message=f'Authorization required . Please access this URL to authorize : {authorization_url}')


        sp_info = access_result[0]['sp_info']
        access_token = sp_info.get('access_token')
        sp = Spotify(auth=access_token)

        # Extract URIs from track info dictionaries
        
        if not tracks_info:
            abort(404, message= 'No tracks found')

        audio_features = sp.audio_features(tracks_info) if len(tracks_info) > 1 else sp.audio_features(tracks_info[0])

        # Now 'audio_features' contains a list of dictionaries, each representing the audio features of a track
        for i, track_uri in enumerate(tracks_info):
            track_info = {'uri': track_uri}

            if audio_features:
                track_info['audio_features'] = audio_features[i]
            
            tracks_info[i] = track_info

        return {'message': 'Audio features retrieved successfully', 'tracks_info': tracks_info}
