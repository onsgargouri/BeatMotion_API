from db import db

class PlaylistModel(db.Model):
    __tablename__ = "playlists"

    playlist_id = db.Column(db.String(50), unique=True, nullable=False,primary_key=True)
    playlist_name = db.Column(db.String(80), nullable=False)
    playlist_description = db.Column(db.String(255), nullable=True)
    workout_type = db.Column(db.String(50), nullable=False)
    intensity_level = db.Column(db.String(50), nullable=False)
    music_genre = db.Column(db.String(50), nullable=False)
    mood = db.Column(db.String(50), nullable=True)
    # connect with User model
    user_id = db.Column(db.String(50), db.ForeignKey('users.user_id'), nullable=False)
    user = db.relationship('UserModel', back_populates='playlists')

    playlist_tracks = db.relationship('PlaylistTrackModel', back_populates='playlist', cascade='all, delete-orphan')
    def to_dict(self):
        return {
            "user_id": self.user_id, 
            "playlist_id": self.playlist_id,
            "playlist_name": self.playlist_name,
            "playlist_description": self.playlist_description,
            "workout_type": self.workout_type,
            "intensity_level": self.intensity_level,
            "music_genre": self.music_genre,
            "mood": self.mood
                
            }

class PlaylistTrackModel(db.Model):
    __tablename__ = "playlist_tracks"

    id = db.Column(db.Integer, primary_key=True)
    track_name = db.Column(db.String(100), nullable=False)
    artist_name = db.Column(db.String(100), nullable=False)
    uri = db.Column(db.String(255), nullable=False)
    playlist_id = db.Column(db.String(50), db.ForeignKey('playlists.playlist_id'), nullable=False)
    playlist = db.relationship('PlaylistModel', back_populates='playlist_tracks')
    
    def to_dict(self):
        return {
            "id": self.id,
            "track_name": self.track_name,
            "artist_name": self.artist_name,
            "uri": self.uri,
        }
