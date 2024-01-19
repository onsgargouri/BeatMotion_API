from marshmallow import Schema, fields


class PlaylistGenerationSchema(Schema):
    playlist_id = fields.String(dump_only=True)
    playlist_name = fields.String(required=False)
    playlist_description = fields.String(required=False)
    workout_type = fields.String(required=True)
    intensity_level = fields.String(required=True)
    music_genre = fields.String(required=True)
    mood = fields.String(required=False)

class PlaylistSchema(Schema):
    playlist_id = fields.String()
    playlist_name = fields.String()
    playlist_description = fields.String()
    workout_type = fields.String()
    intensity_level = fields.String()
    music_genre = fields.String()
    mood = fields.String()
    message = fields.String()

class UserPreferencesSchema(Schema):
    user_id = fields.String()
    playlists = fields.Nested(PlaylistSchema, many=True)
    message = fields.String()

class UsersPlaylistSchema(Schema):
    users_preferences = fields.Nested(UserPreferencesSchema, many=True)

class PlaylistDeleteSchema(Schema):
    message = fields.String()

class PlaylistPlaySchema(Schema):
    Link_to_play_Spotify_Playlist = fields.String()

class PlaylistTracksSchema(Schema):
    playlist_tracks = fields.List(fields.Dict())

class TracksAudioFeaturesSchema(Schema):
    message = fields.String()
    tracks_info = fields.List(fields.Dict())

class AuthorizationSchema(Schema):
    message = fields.String()
    auth_url = fields.String()

class UserDeleteSchema(Schema):
    message = fields.String()