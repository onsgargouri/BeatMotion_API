# these are the functions needed when generating a new playlist 
from spotipy import Spotify

def create_spotify_playlist(sp: Spotify, user_id: str, playlist_name: str, playlist_description: str) -> str:
    playlist = sp.user_playlist_create(user_id, playlist_name, public=False, description=playlist_description)
    return playlist['id']

def convert_preferences_to_audio_features( playlist_prefrences):
    # Map workout type to tempo ranges
    tempo_ranges = {
        'running': (120, 160),
        'walking': (80, 120),
        'cycling': (120, 160),
        'HIIT': (160, 180), #High Intensity Interval Training 
        'weightlifting': (100, 120),
        'yoga': (60, 100),
        'boxing' :(160,180)
    }

    # Map intensity level to energy values
    energy_levels = {
        'energetic': (0.7,0.9),
        'moderate': (0.4,0.6),
        'relaxed': (0.1,0.3),
    }

    # Map music genre to corresponding Spotify genres
    genre = {
        'pop': 'pop',
        'rock': 'rock',
        'hipHop': 'hip-hop',
        'electronic': 'electronic',
        'classical': 'classical'
    }

    # Instrumentalness preference
    instrumentalness = {
        'instrumental': (0.6,1),
        'vocals': (0.1,0.5)
    }
    # Map Danceability to danceability
    danceability={
        "danceable":(0.5,1),
        "normal":(0.1,0.4)
    }

    # Map Mood to valence 
    mood={
        'positive':(0.5,1),
        'negative':(0.1,0.4)
    }

    # Create audio features dictionary
    audio_features = {
        'min_tempo':tempo_ranges[playlist_prefrences['workout_type']][0],
        'max_tempo':tempo_ranges[playlist_prefrences['workout_type']][1],
        'min_energy':energy_levels[playlist_prefrences['intensity_level']][0],
        'max_energy':energy_levels[playlist_prefrences['intensity_level']][1],
        'seed_genres':genre[playlist_prefrences['music_genre']],
        #'min_instrumentalness':instrumentalness[playlist_prefrences['instrumentalness']][0],
        #'max_instrumentalness':instrumentalness[playlist_prefrences['instrumentalness']][1],
        #'min_danceability':danceability[playlist_prefrences['danceability']][0],
        #'max_danceability':danceability[playlist_prefrences['danceability']][1],
        #'min_valence':mood[playlist_prefrences['mood']][0],
        #'max_valence':mood[playlist_prefrences['mood']][1]
    }

    return audio_features

def get_spotify_recommendations(sp: Spotify, audio_features):
    try:
        # Make the recommendation request
        seed_genres = audio_features['seed_genres'].split(',')
        recommendations = sp.recommendations(seed_genres=seed_genres,
                                            min_tempo=audio_features['min_tempo'],
                                            max_tempo=audio_features['max_tempo'],
                                            min_energy=audio_features['min_energy'],
                                            max_energy=audio_features['max_energy'],
                                            #min_instrumentalness=audio_features['min_instrumentalness'],
                                            #max_instrumentalness=audio_features['max_instrumentalness'],
                                            #min_danceability=audio_features['min_danceability'],
                                            #max_danceability=audio_features['max_danceability'],
                                            #min_valence=audio_features['min_valence'],
                                            #max_valence=audio_features['max_valence'],
                                            )
        # Extract the recommended track information
        recommended_tracks_info = []
        for track in recommendations['tracks']:
            # Get audio features for each track
            audio_features_track = sp.audio_features([track['id']])[0]
            track_info = {
                'track_name': track['name'],
                'artist_name': track['artists'][0]['name'],
                'uri': track['uri'],
                'audio_features': audio_features_track,
            }
            recommended_tracks_info.append(track_info)
        #recommended_tracks_info =[{'track_name': track['name'], 'artist_name': track['artists'][0]['name'] , 'uri':track['uri']} for track in recommendations['tracks']]
        if not recommended_tracks_info:
                print("No recommendations found.")
                return None
        return recommended_tracks_info
    except Exception as e:
        return None
